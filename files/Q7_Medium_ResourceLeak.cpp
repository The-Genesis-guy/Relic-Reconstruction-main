/**
 * PROBLEM: Configuration File Reader
 * 
 * Read configuration settings from a file and parse them.
 * The program should handle file operations safely and close resources properly.
 * 
 * File format (config.txt):
 * username=admin
 * timeout=30
 * max_connections=100
 * 
 * INPUT: Filename
 * OUTPUT: Parsed configuration as key-value pairs
 * 
 * EXPECTED BEHAVIOR:
 * - Read file successfully
 * - Parse all key-value pairs
 * - Close file properly even if errors occur
 * - Handle missing files gracefully
 * 
 * BUG: The code has a resource management issue. Find and fix the bug!
 */

#include <iostream>
#include <fstream>
#include <map>
#include <string>
using namespace std;

map<string, string>* readConfig(const string& filename) {
    map<string, string>* config = new map<string, string>();
    ifstream* file = new ifstream(filename);
    
    if (!file->is_open()) {
        cout << "Error: File not found - " << filename << endl;
        delete config;
        delete file;
        return nullptr;
    }
    
    string line;
    
    while (getline(*file, line)) {
        // Trim whitespace
        size_t start = line.find_first_not_of(" \t");
        if (start == string::npos) continue;
        line = line.substr(start);
        
        // Skip empty lines and comments
        if (line.empty() || line[0] == '#') {
            continue;
        }
        
        // Parse key=value pairs
        size_t pos = line.find('=');
        if (pos != string::npos) {
            string key = line.substr(0, pos);
            string value = line.substr(pos + 1);
            
            // Trim value
            size_t valueStart = value.find_first_not_of(" \t");
            if (valueStart != string::npos) {
                value = value.substr(valueStart);
            }
            
            (*config)[key] = value;
        } else {
            cout << "Error parsing config: Invalid format - " << line << endl;
            delete config;
            return nullptr;
            // BUG HERE: File stream is not closed/deleted when error occurs
        }
    }
    
    file->close();
    delete file;
    
    return config;
}

int main() {
    string filename;
    
    cout << "Enter config filename:" << endl;
    getline(cin, filename);
    
    map<string, string>* config = readConfig(filename);
    
    if (config != nullptr) {
        cout << "\nConfiguration loaded:" << endl;
        for (const auto& pair : *config) {
            cout << pair.first << " = " << pair.second << endl;
        }
        delete config;
    }
    
    return 0;
}
