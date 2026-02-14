// ===================================================
// PROBLEM 3: PATTERN MATCH COUNT - BUGGY JAVA
// ===================================================
import java.io.*;

public class Solution {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String t = br.readLine();
        String p = br.readLine();
        int cnt = 0;
        
        for (int i = 0; i < t.length() - p.length(); i++) {
            if (t.substring(i, i + p.length()) != p) {
                cnt++;
            }
        }
        
        System.out.println(cnt);
    }
}
