def execute(**kwargs):
    operation = kwargs.get('operation')
    numbers = kwargs.get('numbers', [])
    
    try:
        if not numbers:
            return "Error: No numbers provided"
        
        if operation == 'add':
            result = sum(numbers)
        elif operation == 'subtract':
            result = numbers[0] - sum(numbers[1:])
        elif operation == 'multiply':
            result = 1
            for num in numbers:
                result *= num
        elif operation == 'divide':
            if 0 in numbers[1:]:
                return "Error: Cannot divide by zero"
            result = numbers[0]
            for num in numbers[1:]:
                result /= num
        else:
            return "Error: Invalid operation. Use add, subtract, multiply, or divide"
        
        return {
            "operation": operation,
            "numbers": numbers,
            "result": result
        }
        
    except Exception as e:
        return f"Error: {str(e)}"