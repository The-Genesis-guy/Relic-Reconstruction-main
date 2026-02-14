// PROBLEM 1: LONGEST VALID PARENTHESES - CORRECT JAVA
// ============================================
import java.util.*;

class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        if (!sc.hasNext()) {
            System.out.println(0);
            return;
        }
        
        String s = sc.next();
        Stack<Integer> st = new Stack<>();
        st.push(-1);
        int best = 0;
        
        for (int i = 0; i < s.length(); i++) {
            if (s.charAt(i) == '(') {
                st.push(i);
            } else {
                st.pop();
                if (!st.isEmpty()) {
                    best = Math.max(best, i - st.peek());
                } else {
                    st.push(i);
                }
            }
        }
        
        System.out.println(best);
    }
}


// =============================================