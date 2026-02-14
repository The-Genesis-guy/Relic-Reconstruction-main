import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        if (!sc.hasNextInt()) return;
        int K = sc.nextInt();

        ArrayList<Integer> all = new ArrayList<>();

        // Read each array
        for (int i = 0; i < K; i++) {
            int n = sc.nextInt();
            for (int j = 0; j < n; j++) {
                all.add(sc.nextInt());
            }
        }

        // Sort
        Collections.sort(all);

        // Print
        for (int i = 0; i < all.size(); i++) {
            if (i > 0) System.out.print(" ");
            System.out.print(all.get(i));
        }
        System.out.println();

        sc.close();
    }
}
