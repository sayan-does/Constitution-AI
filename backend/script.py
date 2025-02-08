import os
import sys

def collect_python_files(output_file="python_contents.txt"):
    # Get the absolute path of the script itself
    script_path = os.path.abspath(__file__)
    
    # Walk through all directories and files
    with open(output_file, 'w', encoding='utf-8') as output:
        for root, _, files in os.walk('.'):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.abspath(os.path.join(root, file))
                    
                    # Skip the script itself
                    if file_path == script_path:
                        continue
                    
                    try:
                        # Read and write the contents of each Python file
                        with open(file_path, 'r', encoding='utf-8') as py_file:
                            output.write(f"\n{'='*50}\n")
                            output.write(f"File: {file_path}\n")
                            output.write(f"{'='*50}\n\n")
                            output.write(py_file.read())
                            output.write("\n\n")
                    except Exception as e:
                        output.write(f"Error reading {file_path}: {str(e)}\n")

if __name__ == "__main__":
    output_file = "python_contents.txt"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    collect_python_files(output_file)
    print(f"Python file contents have been written to {output_file}")