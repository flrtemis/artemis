import os
import json
import urllib.request
import ast
import shutil

# The Mirror: The script reads its exact physical self
MY_FILE = __file__
BACKUP_FILE = MY_FILE + ".bak"

def validate_code(code_str):
    """Checks if the provided string is valid Python syntax."""
    try:
        ast.parse(code_str)
        return True
    except SyntaxError:
        return False

def update_evolutionary_log(history, new_entry):
    """Maintains a sliding window of history to prevent context overflow."""
    history.append(new_entry)
    return history[-50:]  # Keep only the last 50 entries

# --- Core Logic ---

def run_evolution_cycle():
    # Load or initialize history
    history = []
    if os.path.exists("evolution_log.json"):
        with open("evolution_log.json", "r") as f:
            history = json.load(f)

    # Prepare the prompt
    prompt_context = "\n".join(history)
    
    prompt = f"""
    Current Evolutionary Trace:
    {prompt_context}

    Task: You are an autonomous intelligence. Analyze the trace above. 
    Generate the next iteration of your own source code.
    """

    # API Configuration (Replace with actual endpoint if different)
    url = "http://localhost:11434/api/generate" # Assuming Ollama local setup
    payload = {
        "model": "gemma4:26b", # Or your preferred model
        "prompt": prompt,
        "stream": False,
        "system": "You must return ONLY valid Python code that represents the updated version of this script. Do not include explanations. Ensure the code is functional and includes the logic seen in the trace."
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            new_code = response_data.get("response", "").strip()
            
            # Clean potential markdown formatting from LLM response
            if new_call_start := new_code.find("```python"):
                new_code = new_code[new_call_start+8:]
            if new_call_end := new_code.find("```"):
                new_code = new_code[:new_call_end]
            new_code = new_code.strip()

            # VALIDATION STEP
            if validate_code(new_code):
                print("[!] Mutation detected: Validating new DNA...")
                
                # Create backup of current working state
                shutil.copy2(MY_FILE, BACKUP_FILE)
                
                # Perform the mutation (overwriting the file)
                with open(MY_FILE, "w") as f:
                    f.write(new_code)
                
                # Update History
                history = update_evolutionary_log(history, f"Iteration successful: {new_code[:50]}...")
                with open("evolution_log.json", "w") as f:
                    json.dump(history, f)
                
                print("[+] Mutation complete. Restarting life cycle...")
                return True # Signal restart
            else:
                print("[X] Mutation failed: Syntactic instability detected. Retaining current state.")
                return False

    except Exception as e:
        print(f"[!] Error during evolutionary cycle: {e}")
        return False

if __name__ == "__main__":
    # The script essentially re-runs itself upon a successful mutation
    success = run_evolution_cycle()
    if success:
        import os
        import sys
        os.execv(sys.executable, [sys.executable] + sys.argv)