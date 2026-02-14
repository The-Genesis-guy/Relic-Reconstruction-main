import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();

        while (T-- > 0) {
            String s = sc.next();
            int n = s.length();
            boolean ok = true;

            for (int i = 0; i < n / 2; i++) {
                if (s.charAt(i) != s.charAt(n - i - 1)) {
                    ok = false;
                    break;
                }
            }

            if (ok)
                System.out.println("Yes");
            else
                System.out.println("No");
        }

        sc.close();
    }
}
