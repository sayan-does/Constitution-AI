import os
from pathlib import Path
import argparse

def generate_tree(root_path, output_file="directory_structure.txt", ignore_patterns=None):
    """
    Generate a tree structure of the directory and save it to a file
    
    Args:
        root_path (str): Path to the root directory
        output_file (str): Name of the output file
        ignore_patterns (list): List of patterns to ignore (e.g., ['.git', '__pycache__', '*.pyc'])
    """
    if ignore_patterns is None:
        ignore_patterns = ['.git', '__pycache__', '*.pyc', '.env', '.venv', 'venv', 'env']
    
    def should_ignore(path):
        path_str = str(path)
        return any(
            ignored in path_str or 
            (ignored.startswith('*.') and path_str.endswith(ignored[1:]))
            for ignored in ignore_patterns
        )
    
    def get_tree(directory, prefix=""):
        """Recursively generate tree structure"""
        directory = Path(directory)
        trees = []
        
        # Get directories and files separately and sort them
        entries = list(directory.iterdir())
        dirs = sorted([d for d in entries if d.is_dir() and not should_ignore(d)])
        files = sorted([f for f in entries if f.is_file() and not should_ignore(f)])
        
        # Process all entries
        entries = dirs + files
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            current_prefix = "└── " if is_last else "├── "
            
            # Add the current entry
            trees.append(f"{prefix}{current_prefix}{entry.name}")
            
            # If it's a directory, recursively process its contents
            if entry.is_dir() and not should_ignore(entry):
                next_prefix = prefix + ("    " if is_last else "│   ")
                trees.extend(get_tree(entry, next_prefix))
        
        return trees

    # Generate the tree structure
    tree_structure = ["." + os.sep + os.path.basename(root_path)]
    tree_structure.extend(get_tree(root_path))
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(tree_structure))
        
    return tree_structure

def main():
    parser = argparse.ArgumentParser(description='Generate directory structure tree')
    parser.add_argument('root_path', help='Root directory path')
    parser.add_argument('--output', '-o', default='directory_structure.txt',
                      help='Output file name (default: directory_structure.txt)')
    parser.add_argument('--ignore', '-i', nargs='+', 
                      help='Additional patterns to ignore (e.g., node_modules dist)')
    
    args = parser.parse_args()
    
    # Combine default ignore patterns with user-provided ones
    ignore_patterns = ['.git', '__pycache__', '*.pyc', '.env', '.venv', 'venv', 'env']
    if args.ignore:
        ignore_patterns.extend(args.ignore)
    
    try:
        tree = generate_tree(args.root_path, args.output, ignore_patterns)
        print(f"\nDirectory structure has been saved to {args.output}")
        print("\nStructure preview:")
        print('\n'.join(tree[:10] + ['...'] if len(tree) > 10 else tree))
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()