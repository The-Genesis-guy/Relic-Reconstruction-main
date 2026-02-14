import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        String t = sc.nextLine();
        String p = sc.nextLine();
        
        int n = t.length();
        int m = p.length();
        int count = 0;
        
        for (int i = 0; i <= n - m; i++) {
            if (t.substring(i, i + m).equals(p)) {
                count++;
            }
        }
        
        System.out.println(count);
    }
}
