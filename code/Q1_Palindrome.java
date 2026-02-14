import java.io.*;
import java.util.*;

public class Q1_Palindrome {
    static int count;
    static int longest;
    static HashMap<Character, Integer> freq = new HashMap<>();
    
    public String check(String s) {  // BUG 1: Not static
        int n = s.length();
        for(int i = 0; i <= n/2; i++) {  // BUG 2: <= should be <
            if(s.charAt(i) != s.charAt(n-i)) return "No";  // BUG 3: Should be n-i-1
        }
        return "Yes";
    }
    
    public void update(String s, String res) {  // BUG 4: Not static
        if(res == "Yes") {  // BUG 5: Should use .equals()
            count++;
            if(s.length() > longest) longest = s.length;  // BUG 6: Missing ()
            for(int i = 0; i <= s.length(); i++) {  // BUG 7: ArrayIndexOutOfBounds
                char c = s.charAt(i);
                freq.put(c, freq.get(c) + 1);  // BUG 8: NullPointerException
            }
        }
    }
    
    public char getMax() {  // BUG 9: Not static
        char max = 'a';
        int cnt = 0;
        for(char c : freq.keySet()) {
            if(freq.get(c) > cnt) {  // BUG 10: Should be >=
                cnt = freq.get(c);
                max = c;
            }
        }
        return max;  // BUG 11: Returns 'a' when empty
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(args[0]));  // BUG 12: No args check
        BufferedWriter bw = new BufferedWriter(new FileWriter(args[1]));
        
        Q1_Palindrome p = new Q1_Palindrome();
        int n = Integer.valueOf(br.readLine());  // BUG 13: Use parseInt
        
        for(int i = 0; i <= n; i++) {  // BUG 14: Should be < n
            String s = br.readLine();  // BUG 15: No null check
            String res = p.check(s);  // BUG 16: Not trimming input
            System.out.println(res);  // BUG 17: Writing to stdout not file
            p.update(s, res);
        }
        
        System.out.println("Total: " + count);  // BUG 18: Writing to stdout
        System.out.println("Longest: " + longest);
        System.out.println("Char: " + p.getMax());  // BUG 19: Empty freq map crash
        
        br.close();
        bw.close();  // BUG 20: Not flushed
        // BUG 21: No finally block
        // BUG 22: No exception handling
        // BUG 23: Static variables not reset
        // BUG 24: count not initialized to 0
        // BUG 25: longest not initialized properly
    }
}
