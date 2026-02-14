import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        if (!sc.hasNextInt()) return;
        int K = sc.nextInt();

        int[] len = new int[K];
        int total = 0;

        // Read sizes
        for (int i = 0; i < K; i++) {
            len[i] = sc.nextInt();
            total += len[i];
        }

        int[] all = new int[total];
        int idx = 0;

        // Read elements
        for (int i = 0; i < K; i++) {
            for (int j = 0; j < len[i]; j++) {
                all[idx++] = sc.nextInt();
            }
        }

        // Sort
        Arrays.sort(all);

        // Print
        for (int i = 0; i < total; i++) {
            System.out.print(all[i] + " ");
        }

        sc.close();
    }
}
