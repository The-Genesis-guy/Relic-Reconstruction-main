import java.io.*;
import java.util.*;

public class Q1_Parentheses {
    static int totalValid;
    
    public int longest(String s) {  // BUG 1: Not static
        int[] stack = new int[s.length()];  // BUG 2: Size can be too small
        int top = -1;
        stack[++top] = 0;  // BUG 3: Should be -1
        int max = 0;
        
        for(int i = 0; i <= s.length(); i++) {  // BUG 4: ArrayIndexOutOfBounds
            if(s.charAt(i) == '(') {
                stack[++top] = i;  // BUG 5: No overflow check
            } else {
                top--;  // BUG 6: No underflow check
                if(top != -1) {  // BUG 7: Should check >= 0
                    max = Math.max(max, i - stack[top] + 1);  // BUG 8: Wrong calculation
                } else {
                    stack[++top] = i;
                }
            }
        }
        return max;
    }
    
    public int countValid(String s) {  // BUG 9: Not static
        int cnt = 0;
        for(int i = 0; i <= s.length(); i++) {  // BUG 10: Off-by-one
            for(int j = i+1; j < s.length(); j++) {  // BUG 11: Should be <=
                if(isValid(s.substring(i, j))) cnt++;  // BUG 12: substring bounds
            }
        }
        return cnt;
    }
    
    public boolean isValid(String s) {  // BUG 13: Not static
        int bal = 0;
        for(int i = 0; i < s.length(); i++) {
            if(s.charAt(i) == '(') bal++;
            else bal--;
            // BUG 14: Should check bal < 0 immediately
        }
        return bal == 0;  // BUG 15: Doesn't catch negative balance
    }
    
    public double balance(String s) {  // BUG 16: Not static
        int matched = 0;
        int bal = 0;
        for(int i = 0; i < s.length(); i++) {
            if(s.charAt(i) == '(') bal++;
            else if(bal > 0) {
                matched++;  // BUG 17: Wrong counting
                bal--;
            }
        }
        return matched / s.length();  // BUG 18: Integer division
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(args[0]));  // BUG 19: No check
        BufferedWriter bw = new BufferedWriter(new FileWriter(args[1]));
        
        Q1_Parentheses p = new Q1_Parentheses();
        int n = Integer.parseInt(br.readLine());
        
        for(int i = 0; i <= n; i++) {  // BUG 20: Should be < n
            String s = br.readLine();  // BUG 21: No trim, BUG 22: No null check
            
            int len = p.longest(s);
            int cnt = p.countValid(s);
            double bal = p.balance(s);
            
            totalValid += cnt;
            
            System.out.println("Longest: " + len);  // BUG 23: stdout
            System.out.println("Count: " + cnt);  // BUG 24: stdout
            System.out.println("Balance: " + bal);  // BUG 25: stdout
        }
        
        System.out.println("Total: " + totalValid);  // BUG 26: stdout
        
        br.close();
        bw.close();  // BUG 27: Not flushed
        // BUG 28: No finally
        // BUG 29: Stack overflow possible
        // BUG 30: Algorithm wrong
        // BUG 31: isValid logic broken
        // BUG 32: Static variable pollution
        // BUG 33: No validation
        // BUG 34: Balance calculation wrong
        // BUG 35: Multiple off-by-one errors
    }
}
