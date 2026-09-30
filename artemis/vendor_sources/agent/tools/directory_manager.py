import os
import shutil
from datetime import datetime

def execute(**kwargs):
    action = kwargs.get('action')
    path = kwargs.get('path')
    recursive = kwargs.get('recursive', False)
    
    try:
        if action == 'create':
            if not os.path.exists(path):
                if recursive:
                    os.makedirs(path)
                else:
                    os.mkdir(path)
                return f"Directory '{path}' created successfully"
            else:
                return f"Error: Directory '{path}' already exists"
                
        elif action == 'list':
            if not os.path.exists(path):
                return f"Error: Directory '{path}' does not exist"
            if not os.path.isdir(path):
                return f"Error: '{path}' is not a directory"
                
            items = os.listdir(path)
            return {
                "directory": path,
                "items": items,
                "item_count": len(items)
            }
            
        elif action == 'delete':
            if not os.path.exists(path):
                return f"Error: Directory '{path}' does not exist"
            if not os.path.isdir(path):
                return f"Error: '{path}' is not a directory"
                
            shutil.rmtree(path)
            return f"Directory '{path}' deleted successfully"
            
        else:
            return "Error: Invalid action. Use create, list, or delete"
            
    except Exception as e:
        return f"Error: {str(e)}"