import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        long k = sc.nextLong();

        int[] a = new int[n];

        for(int i = 0; i < n; i++)
            a[i] = sc.nextInt();

        k = k % n;

        for(int i = 0; i < n; i++) {
            int idx = (int)((i - k + n) % n);
            System.out.print(a[idx]);

            if(i == n - 1)
                System.out.println();
            else
                System.out.print(" ");
        }

        sc.close();
    }
}
