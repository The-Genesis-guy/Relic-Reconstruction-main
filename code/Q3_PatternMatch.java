import java.io.*;
import java.util.*;

public class Q3_PatternMatch {
    static int totalMatches;
    
    public int find(String text, String pat) {  // BUG 1: Not static
        int cnt = 0;
        int tLen = text.length();
        int pLen = pat.length();
        
        for(int i = 0; i <= tLen - pLen; i++) {  // BUG 2: Off-by-one
            boolean match = true;
            for(int j = 0; j <= pLen; j++) {  // BUG 3: ArrayIndexOutOfBounds
                if(text.charAt(i+j) != pat.charAt(j)) {
                    match = false;
                    break;
                }
            }
            if(match) cnt++;  // BUG 4: No skip for overlapping
        }
        return cnt;
    }
    
    public String getMost(HashMap<String, Integer> map) {  // BUG 5: Not static
        String most = null;  // BUG 6: Returns null
        int max = 0;
        for(String key : map.keySet()) {
            if(map.get(key) > max) {  // BUG 7: Should be >=
                max = map.get(key);
                most = key;
            }
        }
        return most;
    }
    
    public double avgPos(HashMap<String, ArrayList<Integer>> pos) {  // BUG 8: Not static
        int total = 0;
        int cnt = 0;
        for(ArrayList<Integer> list : pos.values()) {
            for(int p : list) {
                total += p;
                cnt++;
            }
        }
        return total / cnt;  // BUG 9: Integer division, BUG 10: Division by zero
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(args[0]));  // BUG 11: No check
        BufferedWriter bw = new BufferedWriter(new FileWriter(args[1]));
        
        Q3_PatternMatch pm = new Q3_PatternMatch();
        int n = Integer.parseInt(br.readLine());
        
        for(int i = 0; i <= n; i++) {  // BUG 12: Should be < n
            String text = br.readLine();  // BUG 13: No trim, BUG 14: No null check
            int m = Integer.parseInt(br.readLine());
            
            HashMap<String, Integer> counts = new HashMap<>();
            HashMap<String, ArrayList<Integer>> positions = new HashMap<>();
            
            for(int j = 0; j <= m; j++) {  // BUG 15: Should be < m
                String pat = br.readLine();  // BUG 16: No trim
                int c = pm.find(text, pat);
                counts.put(pat, c);
                totalMatches += c;
                
                ArrayList<Integer> pos = new ArrayList<>();
                for(int k = 0; k < text.length(); k++) {  // BUG 17: Inefficient recalculation
                    // BUG 18: Logic missing for position tracking
                }
                positions.put(pat, pos);
            }
            
            for(String p : counts.keySet())
                System.out.println(p + ": " + counts.get(p));  // BUG 19: stdout
            
            System.out.println("Total: " + totalMatches);  // BUG 20: stdout
            System.out.println("Most: " + pm.getMost(counts));  // BUG 21: stdout
            System.out.println("Avg: " + pm.avgPos(positions));  // BUG 22: stdout
        }
        
        br.close();
        bw.close();  // BUG 23: Not flushed
        // BUG 24: No finally
        // BUG 25: Static variable not reset
        // BUG 26: Position tracking incomplete
        // BUG 27: No validation
        // BUG 28: totalMatches accumulates across test cases wrongly
    }
}
