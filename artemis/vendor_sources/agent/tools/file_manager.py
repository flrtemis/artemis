import os

def execute(**kwargs):
    action = kwargs.get('action')
    filename = kwargs.get('filename')
    content = kwargs.get('content', '')
    
    try:
        if action == 'create':
            with open(filename, 'w') as f:
                f.write(content)
            return f"File '{filename}' created successfully"
            
        elif action == 'read':
            if not os.path.exists(filename):
                return f"Error: File '{filename}' does not exist"
            with open(filename, 'r') as f:
                content = f.read()
            return {
                "filename": filename,
                "content": content
            }
            
        elif action == 'update':
            if not os.path.exists(filename):
                return f"Error: File '{filename}' does not exist"
            with open(filename, 'a') as f:
                f.write(content)
            return f"File '{filename}' updated successfully"
            
        elif action == 'delete':
            if not os.path.exists(filename):
                return f"Error: File '{filename}' does not exist"
            os.remove(filename)
            return f"File '{filename}' deleted successfully"
            
        else:
            return "Error: Invalid action. Use create, read, update, or delete"
            
    except Exception as e:
        return f"Error: {str(e)}"