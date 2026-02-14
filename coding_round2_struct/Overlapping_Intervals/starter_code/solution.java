import java.util.*;
public class Main {
    public static void main(String[] args){
        Scanner sc = new Scanner(System.in);
        if(!sc.hasNextInt()) return;
        int n = sc.nextInt();
        long[][] iv = new long[n][2];
        for(int i=0;i<n;i++){ iv[i][0]=sc.nextLong(); iv[i][1]=sc.nextLong(); }
        // TODO: merge intervals and print lines
    }
}
