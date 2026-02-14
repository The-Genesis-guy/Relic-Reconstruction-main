import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        if (!sc.hasNext()) {   // handle empty input
            System.out.println(0);
            return;
        }

        String s = sc.next();
        Stack<Integer> st = new Stack<>();

        st.push(-1);   // base index
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
