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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 256
#define MAX_CONFIGS 50

typedef struct {
    char key[50];
    char value[100];
} ConfigPair;

int readConfig(const char* filename, ConfigPair configs[]) {
    FILE* file = fopen(filename, "r");
    
    if (file == NULL) {
        printf("Error: File not found - %s\n", filename);
        return -1;
    }
    
    char line[MAX_LINE];
    int count = 0;
    
    while (fgets(line, MAX_LINE, file) != NULL && count < MAX_CONFIGS) {
        // Remove newline
        line[strcspn(line, "\n")] = 0;
        
        // Remove leading/trailing whitespace
        char* trimmed = line;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++;
        
        // Skip empty lines and comments
        if (strlen(trimmed) == 0 || trimmed[0] == '#') {
            continue;
        }
        
        // Parse key=value pairs
        char* equals = strchr(trimmed, '=');
        if (equals != NULL) {
            *equals = '\0';
            char* key = trimmed;
            char* value = equals + 1;
            
            // Trim key and value
            while (*value == ' ' || *value == '\t') value++;
            
            strcpy(configs[count].key, key);
            strcpy(configs[count].value, value);
            count++;
        } else {
            printf("Error parsing config: Invalid format - %s\n", trimmed);
            return -1;
            // BUG HERE: File is not closed when error occurs
        }
    }
    
    fclose(file);
    return count;
}

int main() {
    char filename[100];
    ConfigPair configs[MAX_CONFIGS];
    
    printf("Enter config filename:\n");
    fgets(filename, 100, stdin);
    filename[strcspn(filename, "\n")] = 0;
    
    int count = readConfig(filename, configs);
    
    if (count > 0) {
        printf("\nConfiguration loaded:\n");
        for (int i = 0; i < count; i++) {
            printf("%s = %s\n", configs[i].key, configs[i].value);
        }
    }
    
    return 0;
}
