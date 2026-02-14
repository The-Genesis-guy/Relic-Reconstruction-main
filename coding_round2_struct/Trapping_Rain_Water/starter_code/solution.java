import java.util.*;
public class Main {
    public static void main(String[] args){
        Scanner sc = new Scanner(System.in);
        if(!sc.hasNextInt()) return;
        int n = sc.nextInt();
        long[] h = new long[n];
        for(int i=0;i<n;i++) h[i]=sc.nextLong();
        // TODO: compute trapped water and print
    }
}
