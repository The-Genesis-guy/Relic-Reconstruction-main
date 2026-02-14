// PROBLEM 4: MERGE INTERVALS - CORRECT JAVA
// ===================================================
import java.util.*;

class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        long[][] intervals = new long[n][2];
        
        for (int i = 0; i < n; i++) {
            intervals[i][0] = sc.nextLong();
            intervals[i][1] = sc.nextLong();
        }
        
        Arrays.sort(intervals, (a, b) -> Long.compare(a[0], b[0]));
        
        long cs = intervals[0][0];
        long ce = intervals[0][1];
        
        for (int i = 1; i < n; i++) {
            if (intervals[i][0] <= ce) {
                ce = Math.max(ce, intervals[i][1]);
            } else {
                System.out.println(cs + " " + ce);
                cs = intervals[i][0];
                ce = intervals[i][1];
            }
        }
        
        System.out.println(cs + " " + ce);
    }
}