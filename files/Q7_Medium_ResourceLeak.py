"""
PROBLEM: Configuration File Reader

Read configuration settings from a file and parse them.
The program should handle file operations safely and close resources properly.

File format (config.txt):
username=admin
timeout=30
max_connections=100

INPUT: Filename
OUTPUT: Parsed configuration as key-value pairs

EXPECTED BEHAVIOR:
- Read file successfully
- Parse all key-value pairs
- Close file properly even if errors occur
- Handle missing files gracefully

BUG: The code has a resource management issue. Find and fix the bug!
"""

def readConfig(filename):
    config = {}
    
    try:
        file = open(filename, 'r')
        
        for line in file:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse key=value pairs
            if '=' in line:
                parts = line.split('=', 1)
                key = parts[0].strip()
                value = parts[1].strip()
                config[key] = value
            else:
                print(f"Error parsing config: Invalid format - {line}")
                return None
                # BUG HERE: File is not closed when error occurs
                # Should use 'with' statement or finally block
        
        file.close()
        
    except FileNotFoundError:
        print(f"Error: File not found - {filename}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
        # BUG: File is not closed in exception cases
    
    return config

def main():
    filename = input("Enter config filename:\n")
    
    config = readConfig(filename)
    
    if config is not None:
        print("\nConfiguration loaded:")
        for key, value in config.items():
            print(f"{key} = {value}")

if __name__ == "__main__":
    main()
