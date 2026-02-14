import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int r = sc.nextInt();
        int c = sc.nextInt();

        long[] dp = new long[r * c];

        for(int i = 0; i < r; i++) {
            for(int j = 0; j < c; j++) {
                long x = sc.nextLong();

                if(i == 0 && j == 0)
                    dp[0] = x;
                else if(i == 0)
                    dp[j] = dp[j - 1] + x;
                else if(j == 0)
                    dp[i * c] = dp[(i - 1) * c] + x;
                else
                    dp[i * c + j] = x + Math.min(
                        dp[(i - 1) * c + j],
                        dp[i * c + j - 1]
                    );
            }
        }

        System.out.println(dp[r * c - 1]);
        sc.close();
    }
}
