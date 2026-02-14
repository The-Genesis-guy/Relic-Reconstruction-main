import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (!sc.hasNextInt()) return;

        int n = sc.nextInt();
        long d = sc.nextLong();
        long r = sc.nextLong();

        long[] p = new long[n];
        for (int i = 0; i < n; i++) p[i] = sc.nextLong();

        // TODO: determine if travel from 0 to d is possible using illuminated segments
        // Print "YES" or "NO".
        // System.out.println("YES");
    }
}
