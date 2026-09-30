import subprocess
import sys
from typing import Dict, Any

def python_interpreter(code: str) -> Dict[str, Any]:
    """
    Executes pure Python code locally using a separate subprocess.
    Requires NO API keys or external cloud services.
    Matches the schema defined in python_interpreter.json.
    """
    response = {
        "stdout": "",
        "stderr": "",
        "status": "success",
        "error_message": None
    }

    try:
        # Run the code string in a separate, isolated Python process
        # timeout=30 prevents the LLM from freezing your app with an infinite loop
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        response["stdout"] = result.stdout
        response["stderr"] = result.stderr
        
        # If the script returned a non-zero exit code, it failed
        if result.returncode != 0:
            response["status"] = "error"
            response["error_message"] = "Code executed with an error."
            
    except subprocess.TimeoutExpired:
        response["status"] = "error"
        response["error_message"] = "Execution timed out (max 30 seconds)."
    except Exception as e:
        response["status"] = "error"
        response["error_message"] = f"Failed to run code: {str(e)}"
        
    return response

# --- Example Usage ---
if __name__ == "__main__":
    llm_payload = {
        "code": "import math\nprint(f'The square root of 144 is {math.sqrt(144)}')"
    }
    
    result = python_interpreter(llm_payload["code"])
    
    import json
    print(json.dumps(result, indent=2))
