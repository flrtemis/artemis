import io
import wave
import os
import json
import httpx
import asyncio
import subprocess
import tempfile
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

app = FastAPI()

# Configuration Settings
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma4:26b"
PIPER_MODEL_PATH = "/home/l3ung/Agent/en_US-amy-medium.onnx"
TOOLS_DIR = "/home/l3ung/Agent/tools"

os.makedirs(TOOLS_DIR, exist_ok=True)

ENGINE_MODE = "native"
voice_engine = None
GLOBAL_CHAT_HISTORY = []

# Initial system check for text-to-speech engine
try:
    from piper import PiperVoice
    if os.path.exists(PIPER_MODEL_PATH):
        voice_engine = PiperVoice.load(PIPER_MODEL_PATH)
        print(f"System Check: Native Piper engine successfully mapped to {PIPER_MODEL_PATH}")
    else:
        print(f"System Check: ONNX file missing at {PIPER_MODEL_PATH}. Switching to system binary wrapper.")
        ENGINE_MODE = "subprocess"
except Exception as init_exception:
    print(f"System Check: Native library loading failed ({init_exception}). Routing to subprocess fallback mode.")
    ENGINE_MODE = "subprocess"

class TTSRequest(BaseModel):
    text: str

# Schema definitions for default system functions
CREATE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "create_tool",
        "description": "Dynamically create and register a brand new external Python tool when a requested capability does not yet exist.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Unique, lowercase name of the tool using underscores (e.g., 'get_system_time')."
                },
                "description": {
                    "type": "string",
                    "description": "Detailed summary explaining exactly what the tool accomplishes and when it should be triggered."
                },
                "parameters": {
                    "type": "object",
                    "description": "The JSON schema 'properties' structure defining input argument keys, types, and descriptions."
                },
                "required_args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Array of mandatory property names required to execute this tool successfully."
                },
                "python_code": {
                    "type": "string",
                    "description": "The complete, self-contained Python script code. It MUST declare an 'execute(**kwargs)' function that handles internal library imports and returns a string or serializable object."
                }
            },
            "required": ["name", "description", "parameters", "required_args", "python_code"]
        }
    }
}

LIST_TOOLS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_tools",
        "description": "Scan the local workspace registry and return a list of all currently available external tools.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
}

def load_tools() -> list:
    """Scans the local storage directory and loads all valid dynamic tools."""
    tools_list = [CREATE_TOOL_SCHEMA, LIST_TOOLS_SCHEMA]
    if not os.path.isdir(TOOLS_DIR):
        return tools_list
    
    for filename in os.listdir(TOOLS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(TOOLS_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    tool_meta = json.load(f)
                    func_name = tool_meta.get("function", {}).get("name")
                    if func_name not in ("create_tool", "list_tools"):
                        tools_list.append(tool_meta)
            except Exception as e:
                print(f"Registry Warning: Failed to parse tool metadata {filename}: {e}")
    return tools_list

def handle_create_tool(args: dict) -> str:
    """Compiles and commits a newly synthesized tool script to workspace storage."""
    try:
        name = args.get("name", "").strip().lower()
        description = args.get("description", "").strip()
        parameters = args.get("parameters", {})
        required_args = args.get("required_args", [])
        python_code = args.get("python_code", "")
        
        if not name or not python_code:
            return "Execution Error: Both 'name' and 'python_code' fields must be populated to instantiate a tool."
        
        if isinstance(parameters, dict):
            properties_dict = parameters.get("properties", parameters)
            required_args = parameters.get("required", required_args)
        else:
            properties_dict = {}

        tool_meta = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties_dict
                }
            }
        }
        if required_args:
            tool_meta["function"]["parameters"]["required"] = required_args
        
        meta_path = os.path.join(TOOLS_DIR, f"{name}.json")
        script_path = os.path.join(TOOLS_DIR, f"{name}.py")
        
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(tool_meta, f, indent=4)
            
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(python_code)
            
        return f"System Confirmation: External tool '{name}' has been written and added to active inventory. You can now execute it."
    except Exception as e:
        return f"Compilation Error: Could not write tool filesystem assets: {str(e)}"

SANDBOX_WRAPPER = """
import json
import sys
sys.path.append('/tools')
try:
    input_data = sys.stdin.read()
    kwargs = json.loads(input_data) if input_data else {}
    
    from importlib import import_module
    tool = import_module(sys.argv[1])
    
    result = tool.execute(**kwargs)
    print(json.dumps({"status": "success", "data": result}))
except Exception as e:
    print(json.dumps({"status": "error", "error": str(e)}))
"""

def _build_bwrap_cmd(name: str) -> list:
    """Constructs the Bubblewrap sandbox command for a given tool."""
    cmd = ["bwrap", "--unshare-all"]
    if "web_scraper" in name or "scrape" in name:
        cmd.append("--share-net")
    cmd.extend([
        "--ro-bind", "/usr", "/usr",
        "--ro-bind", "/lib", "/lib",
        "--ro-bind", "/lib64", "/lib64",
        "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
        "--ro-bind", TOOLS_DIR, "/tools",
        "--dir", "/tmp",
        "--proc", "/proc",
        "--dev", "/dev",
        "python3", "-c", SANDBOX_WRAPPER, name
    ])
    return cmd

async def handle_execute_tool(name: str, args: dict) -> str:
    """Loads a dynamic tool and executes it inside a secure Bubblewrap sandbox (non-blocking)."""
    script_path = os.path.join(TOOLS_DIR, f"{name}.py")
    if not os.path.exists(script_path):
        return f"Runtime Error: The requested tool asset '{name}' was not found in storage."
    
    try:
        # Run the blocking subprocess in a worker thread so the event loop stays responsive
        process = await asyncio.to_thread(
            subprocess.run,
            _build_bwrap_cmd(name),
            input=json.dumps(args),
            capture_output=True,
            text=True,
            timeout=30
        )

        if process.returncode != 0:
            return f"Sandbox Violation or Core Crash: {process.stderr.strip()}"

        output = json.loads(process.stdout.strip())
        if output.get("status") == "success":
            return str(output.get("data"))
        return f"Runtime Execution Failure inside sandboxed tool '{name}': {output.get('error')}"

    except subprocess.TimeoutExpired:
        return f"Security Block: External tool '{name}' timed out (max 30 seconds) and was terminated."
    except Exception as e:
        return f"Sandbox Controller Error: Failed to safely provision sandbox environment: {str(e)}"


# Raw string block for the rich HTML/JS layout including the responsive Canvas split screen
HTML_CONTENT = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✦ THE SANCTUM ✦</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=Syncopate:wght@400;700&display=swap');

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: 'Cormorant Garamond', serif;
            background: #000;
            color: #e8e0f0;
        }

        /* ═══════════════════════════════════════════════════════════════
           THREE.JS CANVAS - THE LIVING WORLD
        ═══════════════════════════════════════════════════════════════ */
        #world-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
        }

        /* ═══════════════════════════════════════════════════════════════
           ATMOSPHERIC OVERLAYS
        ═══════════════════════════════════════════════════════════════ */
        .vignette {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
            background: radial-gradient(ellipse 70% 60% at 50% 50%, transparent 0%, rgba(0,0,0,0.7) 100%);
        }

        .grain {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 2;
            opacity: 0.04;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
            animation: grain 0.5s steps(1) infinite;
        }

        @keyframes grain {
            0%, 100% { transform: translate(0, 0); }
            10% { transform: translate(-1%, -1%); }
            20% { transform: translate(1%, 1%); }
            30% { transform: translate(-1%, 1%); }
            40% { transform: translate(1%, -1%); }
            50% { transform: translate(-1%, 0); }
            60% { transform: translate(1%, 0); }
            70% { transform: translate(0, 1%); }
            80% { transform: translate(0, -1%); }
            90% { transform: translate(1%, 1%); }
        }

        /* ═══════════════════════════════════════════════════════════════
           THE SANCTUM - MAIN CONTAINER
        ═══════════════════════════════════════════════════════════════ */
        .sanctum {
            position: relative;
            z-index: 10;
            width: 100%;
            height: 100%;
            display: grid;
            grid-template-rows: 1fr auto;
        }

        /* ═══════════════════════════════════════════════════════════════
           AVATAR STAGE - WHERE THE ORACLE RESIDES
        ═══════════════════════════════════════════════════════════════ */
        .avatar-stage {
            position: relative;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            padding-bottom: 80px;
        }

        .avatar-container {
            position: relative;
            width: 400px;
            height: 500px;
        }

        /* Avatar glow pedestal */
        .avatar-pedestal {
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 40px;
            background: radial-gradient(ellipse, rgba(147, 51, 234, 0.6) 0%, transparent 70%);
            filter: blur(20px);
            animation: pedestalPulse 4s ease-in-out infinite;
        }

        @keyframes pedestalPulse {
            0%, 100% { opacity: 0.6; transform: translateX(-50%) scale(1); }
            50% { opacity: 1; transform: translateX(-50%) scale(1.2); }
        }

        /* Avatar silhouette (placeholder for 3D model) */
        .avatar-figure {
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            width: 180px;
            height: 380px;
            background: linear-gradient(180deg, 
                rgba(147, 51, 234, 0.3) 0%,
                rgba(59, 130, 246, 0.2) 30%,
                rgba(236, 72, 153, 0.2) 60%,
                transparent 100%);
            border-radius: 50% 50% 40% 40% / 30% 30% 20% 20%;
            filter: blur(1px);
            animation: avatarFloat 6s ease-in-out infinite;
        }

        .avatar-figure::before {
            content: '';
            position: absolute;
            top: -60px;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 100px;
            background: linear-gradient(180deg, 
                rgba(147, 51, 234, 0.4) 0%,
                rgba(59, 130, 246, 0.3) 100%);
            border-radius: 50%;
        }

        .avatar-figure::after {
            content: '';
            position: absolute;
            top: -30px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 60px;
            background: radial-gradient(circle at 30% 30%, 
                rgba(255,255,255,0.3) 0%, 
                rgba(147, 51, 234, 0.5) 40%,
                transparent 70%);
            border-radius: 50%;
            animation: eyeGlow 3s ease-in-out infinite;
        }

        @keyframes avatarFloat {
            0%, 100% { transform: translateX(-50%) translateY(0); }
            50% { transform: translateX(-50%) translateY(-15px); }
        }

        @keyframes eyeGlow {
            0%, 100% { box-shadow: 0 0 30px rgba(147, 51, 234, 0.8), 0 0 60px rgba(59, 130, 246, 0.4); }
            50% { box-shadow: 0 0 50px rgba(147, 51, 234, 1), 0 0 100px rgba(59, 130, 246, 0.6); }
        }

        /* Avatar particles around figure */
        .avatar-aura {
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 300px;
            height: 450px;
            pointer-events: none;
        }

        .aura-particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: radial-gradient(circle, rgba(255,255,255,0.8), rgba(147, 51, 234, 0.4));
            border-radius: 50%;
            animation: auraFloat var(--duration) ease-in-out infinite;
            animation-delay: var(--delay);
        }

        @keyframes auraFloat {
            0%, 100% { 
                transform: translate(0, 0) scale(1); 
                opacity: 0.3;
            }
            50% { 
                transform: translate(var(--tx), var(--ty)) scale(1.5); 
                opacity: 1;
            }
        }

        /* ═══════════════════════════════════════════════════════════════
           SPEECH BUBBLE - THOUGHT MANIFESTATION
        ═══════════════════════════════════════════════════════════════ */
        .speech-container {
            position: absolute;
            top: 20%;
            left: 50%;
            transform: translateX(-50%);
            width: min(600px, 90%);
            pointer-events: none;
        }

        .speech-bubble {
            background: rgba(15, 10, 30, 0.85);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(147, 51, 234, 0.4);
            border-radius: 30px;
            padding: 24px 32px;
            opacity: 0;
            transform: scale(0.9) translateY(20px);
            transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            box-shadow: 
                0 0 40px rgba(147, 51, 234, 0.3),
                0 20px 60px rgba(0, 0, 0, 0.5);
        }

        .speech-bubble.visible {
            opacity: 1;
            transform: scale(1) translateY(0);
        }

        .speech-bubble::before {
            content: '';
            position: absolute;
            bottom: -15px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 15px solid transparent;
            border-right: 15px solid transparent;
            border-top: 20px solid rgba(147, 51, 234, 0.4);
            filter: blur(1px);
        }

        .speech-text {
            font-size: 16px;
            line-height: 1.8;
            color: #e8e0f0;
            text-align: center;
        }

        /* ═══════════════════════════════════════════════════════════════
           CONTROL ORBS - BOTTOM INTERFACE
        ═══════════════════════════════════════════════════════════════ */
        .controls {
            padding: 30px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }

        .input-sanctum {
            width: min(700px, 90%);
            position: relative;
        }

        .input-glow {
            position: absolute;
            inset: -2px;
            background: linear-gradient(135deg, rgba(147, 51, 234, 0.5), rgba(59, 130, 246, 0.5));
            border-radius: 35px;
            filter: blur(10px);
            opacity: 0.5;
            animation: inputGlow 3s ease-in-out infinite;
        }

        @keyframes inputGlow {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.7; }
        }

        .input-frame {
            position: relative;
            background: rgba(10, 5, 20, 0.9);
            border: 1px solid rgba(147, 51, 234, 0.3);
            border-radius: 35px;
            display: flex;
            align-items: center;
            padding: 8px;
            gap: 8px;
            backdrop-filter: blur(20px);
        }

        .voice-btn {
            width: 54px;
            height: 54px;
            border-radius: 50%;
            border: 1px solid rgba(147, 51, 234, 0.4);
            background: rgba(30, 20, 50, 0.8);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            transition: all 0.3s;
            flex-shrink: 0;
        }

        .voice-btn:hover {
            background: rgba(147, 51, 234, 0.3);
            border-color: rgba(147, 51, 234, 0.6);
            box-shadow: 0 0 30px rgba(147, 51, 234, 0.4);
        }

        .voice-btn.listening {
            background: rgba(147, 51, 234, 0.5);
            border-color: rgba(147, 51, 234, 0.8);
            animation: listeningPulse 1s ease-in-out infinite;
        }

        @keyframes listeningPulse {
            0%, 100% { box-shadow: 0 0 20px rgba(147, 51, 234, 0.4); }
            50% { box-shadow: 0 0 50px rgba(147, 51, 234, 0.8); }
        }

        .text-input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: #e8e0f0;
            font-family: 'Cormorant Garamond', serif;
            font-size: 18px;
            padding: 12px 16px;
        }

        .text-input::placeholder {
            color: rgba(232, 224, 240, 0.4);
            font-style: italic;
        }

        .send-btn {
            width: 54px;
            height: 54px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(135deg, rgba(147, 51, 234, 0.8), rgba(59, 130, 246, 0.8));
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            transition: all 0.3s;
            flex-shrink: 0;
        }

        .send-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 0 40px rgba(147, 51, 234, 0.6);
        }

        .send-btn:active {
            transform: scale(0.95);
        }

        /* ═══════════════════════════════════════════════════════════════
           STATUS WHISPERS
        ═══════════════════════════════════════════════════════════════ */
        .status-whisper {
            font-family: 'Syncopate', sans-serif;
            font-size: 10px;
            letter-spacing: 0.3em;
            text-transform: uppercase;
            color: rgba(232, 224, 240, 0.5);
            text-align: center;
        }

        .status-whisper span {
            display: inline-block;
            animation: statusBlink 2s ease-in-out infinite;
        }

        .status-whisper span:nth-child(2) { animation-delay: 0.3s; }
        .status-whisper span:nth-child(3) { animation-delay: 0.6s; }
        .status-whisper span:nth-child(4) { animation-delay: 0.9s; }

        @keyframes statusBlink {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 1; }
        }

        /* ═══════════════════════════════════════════════════════════════
           TOAST NOTIFICATIONS
        ═══════════════════════════════════════════════════════════════ */
        .toast {
            position: fixed;
            top: 40px;
            left: 50%;
            transform: translateX(-50%) translateY(-20px);
            background: rgba(15, 10, 30, 0.95);
            border: 1px solid rgba(147, 51, 234, 0.4);
            border-radius: 20px;
            padding: 14px 28px;
            color: #e8e0f0;
            font-size: 14px;
            opacity: 0;
            pointer-events: none;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            z-index: 100;
            backdrop-filter: blur(20px);
            box-shadow: 0 0 40px rgba(147, 51, 234, 0.3);
        }

        .toast.visible {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }

        /* ═══════════════════════════════════════════════════════════════
           SETTINGS PANEL
        ═══════════════════════════════════════════════════════════════ */
        .settings-btn {
            position: fixed;
            top: 30px;
            right: 30px;
            z-index: 50;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: 1px solid rgba(147, 51, 234, 0.3);
            background: rgba(15, 10, 30, 0.8);
            backdrop-filter: blur(20px);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            transition: all 0.3s;
        }

        .settings-btn:hover {
            background: rgba(147, 51, 234, 0.3);
            border-color: rgba(147, 51, 234, 0.6);
            transform: rotate(90deg);
        }

        .settings-panel {
            position: fixed;
            top: 90px;
            right: 30px;
            z-index: 50;
            width: 300px;
            background: rgba(15, 10, 30, 0.95);
            border: 1px solid rgba(147, 51, 234, 0.3);
            border-radius: 20px;
            padding: 24px;
            backdrop-filter: blur(20px);
            opacity: 0;
            pointer-events: none;
            transform: translateY(-10px);
            transition: all 0.3s;
        }

        .settings-panel.visible {
            opacity: 1;
            pointer-events: all;
            transform: translateY(0);
        }

        .settings-panel h3 {
            font-family: 'Syncopate', sans-serif;
            font-size: 12px;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            margin-bottom: 20px;
            color: rgba(232, 224, 240, 0.7);
        }

        .setting-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            font-size: 14px;
        }

        .setting-row label {
            color: rgba(232, 224, 240, 0.8);
        }

        .setting-row input[type="checkbox"] {
            accent-color: rgba(147, 51, 234, 0.8);
            width: 18px;
            height: 18px;
        }

        /* ═══════════════════════════════════════════════════════════════
           LOADING STATE
        ═══════════════════════════════════════════════════════════════ */
        .loading-orb {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 100;
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(147, 51, 234, 0.8), transparent 70%);
            animation: loadingPulse 1.5s ease-in-out infinite;
            display: none;
        }

        .loading-orb.active {
            display: block;
        }

        @keyframes loadingPulse {
            0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
            50% { transform: translate(-50%, -50%) scale(1.5); opacity: 1; }
        }
    </style>
</head>
<body>
    <!-- THE LIVING WORLD - Three.js Canvas -->
    <canvas id="world-canvas"></canvas>

    <!-- Atmospheric Overlays -->
    <div class="vignette"></div>
    <div class="grain"></div>

    <!-- Loading Indicator -->
    <div class="loading-orb" id="loadingOrb"></div>

    <!-- THE SANCTUM - Main Interface -->
    <div class="sanctum">
        <!-- Avatar Stage -->
        <div class="avatar-stage">
            <!-- Speech Bubble -->
            <div class="speech-container">
                <div class="speech-bubble" id="speechBubble">
                    <p class="speech-text" id="speechText"></p>
                </div>
            </div>

            <!-- Avatar -->
            <div class="avatar-container">
                <div class="avatar-pedestal"></div>
                <div class="avatar-figure"></div>
                <div class="avatar-aura" id="avatarAura"></div>
            </div>
        </div>

        <!-- Controls -->
        <div class="controls">
            <p class="status-whisper" id="statusWhisper">
                <span>◆</span> <span>◆</span> <span>◆</span> <span>connection ethereal</span>
            </p>

            <div class="input-sanctum">
                <div class="input-glow"></div>
                <div class="input-frame">
                    <button class="voice-btn" id="voiceBtn" title="Voice Input">
                        🎙️
                    </button>
                    <input 
                        type="text" 
                        class="text-input" 
                        id="textInput" 
                        placeholder="Speak your desire into the void..."
                        onkeydown="handleInputKeydown(event)"
                    >
                    <button class="send-btn" id="sendBtn" onclick="sendMessage()">
                        ✦
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Settings -->
    <button class="settings-btn" id="settingsBtn" onclick="toggleSettings()">⚙</button>
    <div class="settings-panel" id="settingsPanel">
        <h3>Configuration</h3>
        <div class="setting-row">
            <label>Auto Voice Response</label>
            <input type="checkbox" id="autoVoice" checked>
        </div>
        <div class="setting-row">
            <label>Show Subtitles</label>
            <input type="checkbox" id="showSubtitles" checked>
        </div>
        <div class="setting-row">
            <label>Ambient Particles</label>
            <input type="checkbox" id="showParticles" checked>
        </div>
        <div class="setting-row">
            <label>Voice Recognition</label>
            <input type="checkbox" id="voiceRecognition" checked>
        </div>
    </div>

    <!-- Toast -->
    <div class="toast" id="toast"></div>

    <!-- Three.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

    <script>
        // ═══════════════════════════════════════════════════════════════
        // THREE.JS SCENE - THE LIVING WORLD
        // ═══════════════════════════════════════════════════════════════
        let scene, camera, renderer;
        let fogParticles = [];
        let cloudMeshes = [];
        let ambientLight, pointLight1, pointLight2;

        function initThreeJS() {
            // Scene
            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x050108, 0.015);

            // Camera
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.z = 5;
            camera.position.y = 0;

            // Renderer
            renderer = new THREE.WebGLRenderer({
                canvas: document.getElementById('world-canvas'),
                antialias: true,
                alpha: true
            });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

            // Lighting
            ambientLight = new THREE.AmbientLight(0x1a0a2e, 0.3);
            scene.add(ambientLight);

            pointLight1 = new THREE.PointLight(0x9333ea, 2, 20);
            pointLight1.position.set(3, 3, 3);
            scene.add(pointLight1);

            pointLight2 = new THREE.PointLight(0x3b82f6, 1.5, 20);
            pointLight2.position.set(-3, 2, 2);
            scene.add(pointLight2);

            // Create fog particles
            createFogParticles();

            // Create volumetric clouds
            createClouds();

            // Create distant stars
            createStars();

            // Animation loop
            animate();
        }

        function createFogParticles() {
            const particleCount = 500;
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(particleCount * 3);
            const colors = new Float32Array(particleCount * 3);

            for (let i = 0; i < particleCount; i++) {
                positions[i * 3] = (Math.random() - 0.5) * 30;
                positions[i * 3 + 1] = (Math.random() - 0.5) * 20;
                positions[i * 3 + 2] = (Math.random() - 0.5) * 20 - 5;

                // Purple/blue gradient colors
                const t = Math.random();
                colors[i * 3] = 0.3 + t * 0.4;     // R
                colors[i * 3 + 1] = 0.1 + t * 0.2; // G
                colors[i * 3 + 2] = 0.5 + t * 0.3; // B
            }

            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

            const material = new THREE.PointsMaterial({
                size: 0.3,
                vertexColors: true,
                transparent: true,
                opacity: 0.4,
                blending: THREE.AdditiveBlending
            });

            const particles = new THREE.Points(geometry, material);
            scene.add(particles);
            fogParticles.push(particles);
        }

        function createClouds() {
            const cloudGeometry = new THREE.SphereGeometry(1, 8, 8);
            const cloudMaterial = new THREE.MeshBasicMaterial({
                color: 0x2d1f4e,
                transparent: true,
                opacity: 0.15,
                blending: THREE.AdditiveBlending
            });

            for (let i = 0; i < 15; i++) {
                const cloud = new THREE.Group();
                
                // Create cloud from multiple spheres
                const sphereCount = 3 + Math.floor(Math.random() * 4);
                for (let j = 0; j < sphereCount; j++) {
                    const sphere = new THREE.Mesh(
                        cloudGeometry,
                        cloudMaterial.clone()
                    );
                    sphere.position.set(
                        (Math.random() - 0.5) * 2,
                        (Math.random() - 0.5) * 0.5,
                        (Math.random() - 0.5) * 2
                    );
                    sphere.scale.setScalar(0.5 + Math.random() * 1);
                    cloud.add(sphere);
                }

                cloud.position.set(
                    (Math.random() - 0.5) * 20,
                    -2 + Math.random() * 4,
                    -8 - Math.random() * 10
                );
                cloud.userData.speed = 0.001 + Math.random() * 0.002;
                cloud.userData.startX = cloud.position.x;

                scene.add(cloud);
                cloudMeshes.push(cloud);
            }
        }

        function createStars() {
            const starGeometry = new THREE.BufferGeometry();
            const starCount = 1000;
            const positions = new Float32Array(starCount * 3);

            for (let i = 0; i < starCount; i++) {
                const theta = Math.random() * Math.PI * 2;
                const phi = Math.acos(2 * Math.random() - 1);
                const r = 30 + Math.random() * 20;

                positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
                positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
                positions[i * 3 + 2] = r * Math.cos(phi);
            }

            starGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

            const starMaterial = new THREE.PointsMaterial({
                size: 0.05,
                color: 0xffffff,
                transparent: true,
                opacity: 0.8
            });

            const stars = new THREE.Points(starGeometry, starMaterial);
            scene.add(stars);
        }

        function animate() {
            requestAnimationFrame(animate);

            const time = Date.now() * 0.001;

            // Animate fog particles
            fogParticles.forEach(particles => {
                particles.rotation.y += 0.0002;
                particles.rotation.x += 0.0001;
            });

            // Animate clouds
            cloudMeshes.forEach(cloud => {
                cloud.position.x = cloud.userData.startX + Math.sin(time * cloud.userData.speed * 100) * 2;
                cloud.position.y += Math.sin(time * 0.5) * 0.001;
            });

            // Animate lights
            pointLight1.position.x = Math.sin(time * 0.5) * 4;
            pointLight1.position.y = Math.cos(time * 0.3) * 3;
            
            pointLight2.position.x = Math.cos(time * 0.4) * 4;
            pointLight2.position.y = Math.sin(time * 0.2) * 3;

            // Subtle camera movement
            camera.position.x = Math.sin(time * 0.1) * 0.2;
            camera.position.y = Math.cos(time * 0.15) * 0.1;

            renderer.render(scene, camera);
        }

        // ═══════════════════════════════════════════════════════════════
        // AVATAR AURA PARTICLES
        // ═══════════════════════════════════════════════════════════════
        function createAvatarAura() {
            const aura = document.getElementById('avatarAura');
            
            for (let i = 0; i < 30; i++) {
                const particle = document.createElement('div');
                particle.className = 'aura-particle';
                particle.style.left = (20 + Math.random() * 60) + '%';
                particle.style.bottom = (Math.random() * 100) + '%';
                particle.style.setProperty('--duration', (3 + Math.random() * 4) + 's');
                particle.style.setProperty('--delay', (Math.random() * 3) + 's');
                particle.style.setProperty('--tx', (Math.random() * 40 - 20) + 'px');
                particle.style.setProperty('--ty', (-30 - Math.random() * 50) + 'px');
                aura.appendChild(particle);
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // AUDIO SYSTEM
        // ═══════════════════════════════════════════════════════════════
        let audioContext = null;
        let isAudioEnabled = true;

        function initAudio() {
            if (audioContext) return;
            
            try {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
            } catch (e) {
                console.log('Audio not available');
            }
        }

        function playTone(frequency, duration, type = 'sine', volume = 0.1) {
            if (!audioContext || !isAudioEnabled) return;
            
            const osc = audioContext.createOscillator();
            const gain = audioContext.createGain();
            
            osc.type = type;
            osc.frequency.value = frequency;
            gain.gain.value = volume;
            gain.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + duration);
            
            osc.connect(gain);
            gain.connect(audioContext.destination);
            osc.start();
            osc.stop(audioContext.currentTime + duration);
        }

        function playAmbientChime() {
            playTone(523.25, 1, 'sine', 0.05); // C5
            setTimeout(() => playTone(659.25, 1.2, 'sine', 0.04), 100); // E5
            setTimeout(() => playTone(783.99, 1.5, 'sine', 0.03), 200); // G5
        }

        function playSendSound() {
            playTone(400, 0.2, 'triangle', 0.08);
            playTone(600, 0.3, 'triangle', 0.06);
        }

        function playReceiveSound() {
            playTone(300, 0.4, 'sine', 0.06);
            setTimeout(() => playTone(450, 0.5, 'sine', 0.05), 150);
        }

        // ═══════════════════════════════════════════════════════════════
        // VOICE RECOGNITION
        // ═══════════════════════════════════════════════════════════════
        let recognition = null;
        let isListening = false;

        function initVoiceRecognition() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                console.log('Speech recognition not available');
                return;
            }

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                const transcript = Array.from(event.results)
                    .map(result => result[0].transcript)
                    .join('');
                
                document.getElementById('textInput').value = transcript;

                if (event.results[0].isFinal) {
                    stopListening();
                    sendMessage();
                }
            };

            recognition.onerror = (event) => {
                console.log('Speech recognition error:', event.error);
                stopListening();
            };

            recognition.onend = () => {
                stopListening();
            };
        }

        function toggleListening() {
            if (!recognition) {
                initVoiceRecognition();
            }

            if (isListening) {
                stopListening();
            } else {
                startListening();
            }
        }

        function startListening() {
            if (!recognition) return;
            
            isListening = true;
            document.getElementById('voiceBtn').classList.add('listening');
            document.getElementById('voiceBtn').textContent = '🔴';
            recognition.start();
            initAudio();
        }

        function stopListening() {
            isListening = false;
            document.getElementById('voiceBtn').classList.remove('listening');
            document.getElementById('voiceBtn').textContent = '🎙️';
            if (recognition) recognition.stop();
        }

        // ═══════════════════════════════════════════════════════════════
        // MESSAGE HANDLING
        // ═══════════════════════════════════════════════════════════════
        let conversationHistory = [];

        function handleInputKeydown(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        function showSpeech(text, isUser = false) {
            const bubble = document.getElementById('speechBubble');
            const speechText = document.getElementById('speechText');
            
            speechText.textContent = text;
            bubble.classList.add('visible');

            if (!isUser) {
                playReceiveSound();
            }
        }

        function hideSpeech() {
            const bubble = document.getElementById('speechBubble');
            bubble.classList.remove('visible');
        }

        async function sendMessage() {
            const input = document.getElementById('textInput');
            const message = input.value.trim();
            
            if (!message) return;

            // Clear and show user message
            input.value = '';
            showSpeech(message, true);
            playSendSound();

            // Show loading
            const loadingOrb = document.getElementById('loadingOrb');
            loadingOrb.classList.add('active');

            // Add to history
            conversationHistory.push({ role: 'user', content: message });

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: message,
                        history: conversationHistory.slice(-10)
                    })
                });

                if (!response.ok) throw new Error('Network error');

                // Read streaming response
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let fullResponse = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value, { stream: true });
                    fullResponse += chunk;
                    
                    // Update speech bubble progressively
                    showSpeech(fullResponse);
                }

                // Add to history
                conversationHistory.push({ role: 'assistant', content: fullResponse });

                // Auto-voice if enabled
                if (document.getElementById('autoVoice').checked && audioContext) {
                    // Simple beep notification that TTS is ready
                    playAmbientChime();
                }

            } catch (error) {
                showSpeech('The void ripples with an error. Please try again.');
                console.error(error);
            } finally {
                loadingOrb.classList.remove('active');
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // SETTINGS
        // ═══════════════════════════════════════════════════════════════
        function toggleSettings() {
            const panel = document.getElementById('settingsPanel');
            panel.classList.toggle('visible');
            playTone(800, 0.1, 'sine', 0.03);
        }

        // ═══════════════════════════════════════════════════════════════
        // TOAST NOTIFICATIONS
        // ═══════════════════════════════════════════════════════════════
        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('visible');
            
            setTimeout(() => {
                toast.classList.remove('visible');
            }, 2500);
        }

        // ═══════════════════════════════════════════════════════════════
        // MOUSE PARALLAX
        // ═══════════════════════════════════════════════════════════════
        document.addEventListener('mousemove', (e) => {
            const x = (e.clientX / window.innerWidth - 0.5) * 0.02;
            const y = (e.clientY / window.innerHeight - 0.5) * 0.02;
            
            if (camera) {
                camera.position.x = x * 2;
                camera.position.y = -y * 2;
            }
        });

        // ═══════════════════════════════════════════════════════════════
        // WINDOW RESIZE
        // ═══════════════════════════════════════════════════════════════
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // ═══════════════════════════════════════════════════════════════
        // INITIALIZATION
        // ═══════════════════════════════════════════════════════════════
        document.addEventListener('DOMContentLoaded', () => {
            // Initialize Three.js world
            initThreeJS();
            
            // Create avatar aura
            createAvatarAura();
            
            // Initialize voice recognition
            initVoiceRecognition();
            
            // Voice button click handler
            document.getElementById('voiceBtn').addEventListener('click', toggleListening);
            
            // Initialize audio on first interaction
            document.addEventListener('click', () => {
                initAudio();
                playAmbientChime();
            }, { once: true });

            // Welcome message
            setTimeout(() => {
                showSpeech('Welcome to The Sanctum. I am the Oracle, here to guide you through the void. Speak your desires, and let us create together.');
            }, 1500);
        });

        // ═══════════════════════════════════════════════════════════════
        // KEYBOARD SHORTCUTS
        // ═══════════════════════════════════════════════════════════════
        document.addEventListener('keydown', (e) => {
            // Space to toggle voice (when not typing)
            if (e.code === 'Space' && document.activeElement !== document.getElementById('textInput')) {
                e.preventDefault();
                toggleListening();
            }
            
            // Escape to stop listening
            if (e.code === 'Escape' && isListening) {
                stopListening();
            }
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_user_interface():
    return HTML_CONTENT

SYSTEM_INSTRUCTION = (
    "You are an advanced autonomous assistant with access to local dynamic system tools via function calling.\n"
    "Instructions:\n"
    "1. Check your inventory of active external tools. If an existing tool fits the user requirement, trigger it immediately.\n"
    "2. If no available tool fits the request but it can be handled programmatically by writing a small Python application "
    "(e.g., file adjustments, calculated tasks, data extraction, fetching system status), you MUST invoke 'create_tool'.\n"
    "3. When invoking 'create_tool', formulate complete, production-ready, functional code containing an entry-point function "
    "defined exactly as: def execute(**kwargs). Handle all necessary python module imports directly within the script block.\n"
    "4. After creating a tool, you will receive a success report. You must immediately utilize that tool in the subsequent turn "
    "to satisfy the prompt.\n"
    "5. If the user asks what tools you have access to or what capabilities you possess, invoke the 'list_tools' function to inspect the local registry.\n"
    "6. Never answer using emojis."
)

@app.post("/api/chat")
async def process_agent_interaction(request: Request):
    global GLOBAL_CHAT_HISTORY
    request_data = await request.json()
    user_prompt = request_data.get("prompt", "")

    if not GLOBAL_CHAT_HISTORY:
        GLOBAL_CHAT_HISTORY.append({"role": "system", "content": SYSTEM_INSTRUCTION})

    async def streaming_pipeline():
        # Work on a COPY so a failed request cannot poison the global history
        local_history = list(GLOBAL_CHAT_HISTORY)
        local_history.append({"role": "user", "content": user_prompt})

        async with httpx.AsyncClient() as client:
            loop_depth = 0
            max_depth = 5

            while loop_depth < max_depth:
                loop_depth += 1
                available_tools = load_tools()

                try:
                    response = await client.post(
                        OLLAMA_URL,
                        json={
                            "model": MODEL_NAME,
                            "messages": local_history,
                            "tools": available_tools if len(available_tools) > 0 else None,
                            "stream": False
                        },
                        timeout=60.0
                    )
                except (httpx.TimeoutException, httpx.ConnectError) as exc:
                    yield f"\n[Backend Error: Could not reach Ollama ({exc}). Is it running and is '{MODEL_NAME}' pulled?]"
                    return

                if response.status_code != 200:
                    yield f"Error: Local model communication broke down with code {response.status_code}."
                    return

                response_data = response.json()
                assistant_message = response_data.get("message", {})
                tool_calls = assistant_message.get("tool_calls", [])

                local_history.append(assistant_message)

                if tool_calls:
                    for tool_call in tool_calls:
                        tool_call_id = tool_call.get("id")
                        function_data = tool_call.get("function", {})
                        tool_name = function_data.get("name", "")
                        tool_args = function_data.get("arguments", {})

                        if isinstance(tool_args, str):
                            try:
                                tool_args = json.loads(tool_args)
                                function_data["arguments"] = tool_args
                            except Exception:
                                pass

                        yield f"[Executing Tool: {tool_name}...\n]"

                        if tool_name == "create_tool":
                            execution_result = handle_create_tool(tool_args)
                        elif tool_name == "list_tools":
                            try:
                                built_tools = [f.replace(".json", "") for f in os.listdir(TOOLS_DIR) if f.endswith(".json")]
                                execution_result = (
                                    f"System Inventory Check: You currently have access to the following custom external tools: {', '.join(built_tools)}."
                                    if built_tools else
                                    "System Inventory Check: No custom external tools have been built yet. Only 'create_tool' and 'list_tools' are active."
                                )
                            except Exception as registry_error:
                                execution_result = f"Registry Error: Unable to scan tools directory: {str(registry_error)}"
                        else:
                            execution_result = await handle_execute_tool(tool_name, tool_args)

                        tool_message = {
                            "role": "tool",
                            "content": execution_result
                        }
                        if tool_call_id:
                            tool_message["tool_call_id"] = tool_call_id

                        local_history.append(tool_message)
                    continue
                else:
                    conversational_text = assistant_message.get("content", "")
                    chunk_increment = 4
                    for index in range(0, len(conversational_text), chunk_increment):
                        yield conversational_text[index:index+chunk_increment]
                        await asyncio.sleep(0.005)

                    # Successful final answer — commit local history back to global
                    GLOBAL_CHAT_HISTORY[:] = local_history
                    return

            yield "\n[Agent Loop Error: Maximum depth limit reached without solution resolution.]"
            GLOBAL_CHAT_HISTORY[:] = local_history

    return StreamingResponse(streaming_pipeline(), media_type="text/plain")

@app.post("/api/tts")
async def process_text_to_speech(payload: TTSRequest):
    audio_buffer = io.BytesIO()

    if ENGINE_MODE == "native" and voice_engine:
        try:
            with wave.open(audio_buffer, "wb") as wav_file:
                voice_engine.synthesize_wav(payload.text, wav_file)
            audio_buffer.seek(0)
            return StreamingResponse(audio_buffer, media_type="audio/wav")
        except Exception as native_fault:
            print(f"Dynamic Catch: Native runtime fault triggered: {native_fault}. Tripping fallback switch.")
    else:
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_path = temp_wav.name

            command = ["piper", "--model", PIPER_MODEL_PATH, "--output-file", temp_path]
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _, stderr_data = process.communicate(input=payload.text.encode("utf-8"))

            if process.returncode == 0:
                with open(temp_path, "rb") as file_reader:
                    binary_payload = file_reader.read()
                os.remove(temp_path)
                return StreamingResponse(io.BytesIO(binary_payload), media_type="audio/wav")
            else:
                runtime_error = stderr_data.decode("utf-8", errors="ignore")
                print(f"Pipeline Fault: Subprocess closed with non-zero status: {runtime_error}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except Exception as system_fault:
            print(f"Pipeline Failure: Both audio layers compromised: {system_fault}")

    return StreamingResponse(io.BytesIO(b""), media_type="audio/wav")

@app.on_event("startup")
async def verify_model():
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get("http://localhost:11434/api/tags", timeout=5.0)
            if r.status_code == 200:
                tags = [m["name"] for m in r.json().get("models", [])]
                if MODEL_NAME not in tags:
                    print(f"WARNING: Model '{MODEL_NAME}' not found locally. Run: ollama pull {MODEL_NAME}")
                else:
                    print(f"Model '{MODEL_NAME}' confirmed available.")
            else:
                print(f"WARNING: Ollama responded with status {r.status_code}.")
    except Exception as e:
        print(f"WARNING: Could not contact Ollama at startup ({e}). Is it running on {OLLAMA_URL}?")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)