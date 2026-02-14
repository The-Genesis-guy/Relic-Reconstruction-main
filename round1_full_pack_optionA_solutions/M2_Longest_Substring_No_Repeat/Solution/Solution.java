import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        if (!sc.hasNext()) {
            System.out.println(0);
            return;
        }

        String s = sc.next();

        int[] last = new int[256];
        Arrays.fill(last, -1);

        int l = 0, best = 0;

        for (int r = 0; r < s.length(); r++) {
            char c = s.charAt(r);

            if (last[c] >= l)
                l = last[c] + 1;

            last[c] = r;

            best = Math.max(best, r - l + 1);
        }

        System.out.println(best);
    }
}
