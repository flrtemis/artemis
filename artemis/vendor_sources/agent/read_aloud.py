import os 
import sys 
import json
import numpy as np 
import sounddevice as sd 
from piper import PiperVoice 
import ollama 

# --- CONFIGURATION --- 
MODEL_PATH = "en_US-amy-medium.onnx" 
OLLAMA_MODEL = "gemma4:latest"  # Change this to whatever model you have installed (e.g., mistral, phi4, gemma3) 

# --- SYSTEM PROMPT ---
# Hardened to strictly forbid emojis, emoticons, or decorative text symbols
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, concise voice assistant. Give brief answers suitable for text-to-speech conversion. "
    "CRITICAL REQUIREMENT: Never use emojis, emoticons, icons, or special symbolic characters under any circumstances "
    "in your responses. Use only clean, standard written text."
)

# --- DYNAMIC TOOLS DEFINITION ---
def get_current_weather(location: str) -> str:
    """Get the current weather for a given location."""
    loc = location.lower()
    if "london" in loc:
        return json.dumps({"location": location, "temperature": "15", "condition": "rainy"})
    elif "new york" in loc:
        return json.dumps({"location": location, "temperature": "22", "condition": "sunny"})
    else:
        return json.dumps({"location": location, "temperature": "20", "condition": "partly cloudy"})

# Mapping of tool names to their corresponding Python functions
DEFINED_TOOLS = {
    'get_current_weather': get_current_weather
}

# Ollama tool specification schema
OLLAMA_TOOLS_SCHEMA = [
    {
        'type': 'function',
        'function': {
            'name': 'get_current_weather',
            'description': 'Get the current weather for a specific location',
            'parameters': {
                'type': 'object',
                'properties': {
                    'location': {
                        'type': 'string',
                        'description': 'The city and state, e.g. San Francisco, CA or London, UK',
                    },
                },
                'required': ['location'],
            },
        },
    }
]

def split_into_sentences(text_buffer): 
    """ 
    Extracts complete sentences from a text buffer based on punctuation boundaries. 
    Returns a list of complete sentences and the remaining incomplete text fragment. 
    """ 
    sentences = [] 
    current_sentence = "" 
     
    delimiters = ('.', '!', '?', '\n') 
     
    i = 0 
    while i < len(text_buffer): 
        char = text_buffer[i] 
        current_sentence += char 
         
        if char in delimiters: 
            if (i + 1 == len(text_buffer)) or (text_buffer[i + 1] in (' ', '\n')): 
                sentences.append(current_sentence.strip()) 
                current_sentence = "" 
        i += 1 
         
    return sentences, current_sentence 
 
def speak_text(voice_engine, sample_rate, text): 
    """Appends punctuation safety rules and plays the sentence via Piper.""" 
    if not text.strip(): 
        return 
 
    if not text.endswith(('.', '!', '?', ',', ';')): 
        text += "." 
 
    audio_bytes = b"" 
    for chunk in voice_engine.synthesize(text): 
        audio_bytes += chunk.audio_int16_bytes 
 
    audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0 
 
    sd.play(audio_data, samplerate=sample_rate) 
    sd.wait() 

def handle_slash_command(command_str, messages_history, current_system_prompt):
    """Processes native Ollama-like slash commands."""
    parts = command_str.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd in ['/bye', '/exit', '/quit']:
        print("Exiting application. Goodbye!")
        sys.exit(0)
        
    elif cmd == '/clear':
        messages_history.clear()
        messages_history.append({'role': 'system', 'content': current_system_prompt})
        print("Chat history cleared.")
        return current_system_prompt
        
    elif cmd == '/system':
        if not args:
            print(f"Current System Prompt: {current_system_prompt}")
        else:
            current_system_prompt = args
            # Update the system prompt in the active history matrix
            if messages_history and messages_history[0]['role'] == 'system':
                messages_history[0]['content'] = current_system_prompt
            else:
                messages_history.insert(0, {'role': 'system', 'content': current_system_prompt})
            print(f"System prompt updated to: \"{current_system_prompt}\"")
        return current_system_prompt
        
    elif cmd == '/help':
        print("\nAvailable Commands:")
        print("  /help              - Show this help menu")
        print("  /system <prompt>   - View or temporarily update the system prompt")
        print("  /clear             - Reset chat conversation memory")
        print("  /bye, /exit        - Terminate the program")
        print("")
        return current_system_prompt
    else:
        print(f"Unknown command: {cmd}. Type /help for available options.")
        return current_system_prompt

if __name__ == "__main__": 
    if not os.path.exists(MODEL_PATH): 
        print(f"Error: Could not find Piper model file at {MODEL_PATH}") 
        sys.exit(1) 
 
    print("Initializing Piper Voice Engine...") 
    voice = PiperVoice.load(MODEL_PATH) 
    sample_rate = voice.config.sample_rate 
 
    print(f"Connected to Ollama engine. Target LLM model: {OLLAMA_MODEL}") 
    print("\n==================================================") 
    print("    PIPER + OLLAMA VOICE CHAT MODE (WITH TOOLS)") 
    print("==================================================") 
    print("Type /help to view available commands.\n") 

    # Initialize dynamic system configuration and message history
    active_system_prompt = DEFAULT_SYSTEM_PROMPT
    messages_history = [{'role': 'system', 'content': active_system_prompt}]
 
    while True: 
        try: 
            user_input = input("\nYou > ") 
            if not user_input.strip(): 
                continue 
 
            # Intercept standard Ollama slash "/" commands
            if user_input.strip().startswith('/'):
                active_system_prompt = handle_slash_command(user_input, messages_history, active_system_prompt)
                continue

            # Append user message to active history tracking
            messages_history.append({'role': 'user', 'content': user_input})
            
            # Setup primary processing loop to handle potential multi-turn function updates
            while True:
                print("AI > ", end="", flush=True) 
                
                stream = ollama.chat( 
                    model=OLLAMA_MODEL, 
                    messages=messages_history, 
                    tools=OLLAMA_TOOLS_SCHEMA,
                    stream=True, 
                ) 
     
                text_buffer = "" 
                tool_calls_to_process = []
                assistant_response_content = ""
                 
                for chunk in stream: 
                    message_chunk = chunk.get('message', {})
                    
                    # Accumulate tool calls if suggested by the model
                    if 'tool_calls' in message_chunk and message_chunk['tool_calls']:
                        for tool_call in message_chunk['tool_calls']:
                            tool_calls_to_process.append(tool_call)
                    
                    token = message_chunk.get('content', '')
                    if token:
                        print(token, end="", flush=True)  # Print text to console live 
                        text_buffer += token 
                        assistant_response_content += token
         
                        # Process sentence-level chunk blocks for the TTS pipeline
                        sentences, text_buffer = split_into_sentences(text_buffer) 
                        for sentence in sentences: 
                            if sentence.strip(): 
                                speak_text(voice, sample_rate, sentence) 
         
                # Flush final text remaining in the streaming buffer
                if text_buffer.strip(): 
                    speak_text(voice, sample_rate, text_buffer) 
                    assistant_response_content += text_buffer
                
                print() # Terminate console lines
                
                # Commit structural text assistant context to history tracking maps
                messages_history.append({'role': 'assistant', 'content': assistant_response_content, 'tool_calls': tool_calls_to_process if tool_calls_to_process else None})

                # If no tool calls were requested, exit generation loop for the current turn
                if not tool_calls_to_process:
                    break
                
                # Execute tool functions dynamically
                for tool_call in tool_calls_to_process:
                    function_name = tool_call['function']['name']
                    function_args = tool_call['function']['arguments']
                    
                    if function_name in DEFINED_TOOLS:
                        print(f"[System Tool Execution: Calling '{function_name}' with parameters {function_args}...]")
                        
                        # Dynamically call matching Python function mapping blocks
                        tool_output = DEFINED_TOOLS[function_name](**function_args)
                        
                        # Feed the tool response execution schema back into the memory pipeline context
                        messages_history.append({
                            'role': 'tool',
                            'name': function_name,
                            'content': tool_output
                        })
                    else:
                        print(f"Error: Tool '{function_name}' was requested but is missing an execution mapping.")
                
                print("Thinking (processing tool data)...")
                # Loop will repeat here, sending updated message history containing tool results back to Ollama
 
        except KeyboardInterrupt: 
            print("\nExiting...") 
            break 
        except Exception as e: 
            print(f"\nAn error occurred: {e}") 
            break
