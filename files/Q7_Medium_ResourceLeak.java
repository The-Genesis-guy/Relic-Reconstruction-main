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

import java.io.*;
import java.util.*;

public class Q7_Medium_ResourceLeak {
    
    public static Map<String, String> readConfig(String filename) {
        Map<String, String> config = new HashMap<>();
        BufferedReader reader = null;
        
        try {
            reader = new BufferedReader(new FileReader(filename));
            String line;
            
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                
                // Skip empty lines and comments
                if (line.isEmpty() || line.startsWith("#")) {
                    continue;
                }
                
                // Parse key=value pairs
                if (line.contains("=")) {
                    String[] parts = line.split("=", 2);
                    String key = parts[0].trim();
                    String value = parts[1].trim();
                    config.put(key, value);
                } else {
                    throw new IllegalArgumentException("Invalid format: " + line);
                }
            }
            
            reader.close();
            
        } catch (FileNotFoundException e) {
            System.out.println("Error: File not found - " + filename);
            return null;
        } catch (IOException e) {
            System.out.println("Error reading file: " + e.getMessage());
            return null;
        } catch (IllegalArgumentException e) {
            System.out.println("Error parsing config: " + e.getMessage());
            return null;
            // BUG HERE: Reader is not closed when exception occurs
            // Should use try-with-resources or finally block
        }
        
        return config;
    }
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        System.out.println("Enter config filename:");
        String filename = sc.nextLine();
        
        Map<String, String> config = readConfig(filename);
        
        if (config != null) {
            System.out.println("\nConfiguration loaded:");
            for (Map.Entry<String, String> entry : config.entrySet()) {
                System.out.println(entry.getKey() + " = " + entry.getValue());
            }
        }
        
        sc.close();
    }
}
