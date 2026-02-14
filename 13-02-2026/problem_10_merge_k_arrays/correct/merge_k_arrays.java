// PROBLEM 3: MERGE K SORTED ARRAYS - CORRECT JAVA
// ===================================================
import java.util.*;

class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        if (!sc.hasNextInt()) return;
        int K = sc.nextInt();
        
        ArrayList<Integer> all = new ArrayList<>();
        
        for (int i = 0; i < K; i++) {
            int n = sc.nextInt();
            for (int j = 0; j < n; j++) {
                all.add(sc.nextInt());
            }
        }
        
        Collections.sort(all);
        
        for (int i = 0; i < all.size(); i++) {
            if (i > 0) System.out.print(" ");
            System.out.print(all.get(i));
        }
        System.out.println();
        
        sc.close();
    }
}