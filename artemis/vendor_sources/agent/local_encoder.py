import base64
import sys

def encode_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    encoded = base64.b64encode(data).decode('utf-8')
    print("=== COPY THE TEXT BELOW THIS LINE ===")
    print(encoded)
    print("=== COPY THE TEXT ABOVE THIS LINE ===")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        encode_file(sys.argv[1])
    else:
        print("Usage: python local_encoder.py <path_to_your_script.py>")