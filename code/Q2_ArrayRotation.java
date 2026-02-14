import java.io.*;
import java.util.*;

public class Q2_ArrayRotation {
    public void rotate(int[] arr, int k) {  // BUG 1: Not static
        int n = arr.length;
        int[] temp = new int[k];  // BUG 2: Wrong size when k > n
        
        for(int i = 0; i <= k; i++)  // BUG 3: ArrayIndexOutOfBounds
            temp[i] = arr[n-k+i];  // BUG 4: Wrong index
        
        for(int i = n-1; i > k; i--)  // BUG 5: Wrong loop
            arr[i] = arr[i-k-1];  // BUG 6: Wrong shift
        
        for(int i = 0; i <= k; i++)  // BUG 7: ArrayIndexOutOfBounds
            arr[i] = temp[i];
    }
    
    public int sum(int[] arr) {  // BUG 8: Not static, BUG 9: int overflow
        int s = 0;
        for(int i = 0; i <= arr.length; i++)  // BUG 10: ArrayIndexOutOfBounds
            s += arr[i];
        return s;
    }
    
    public int max(int[] arr) {  // BUG 11: Not static
        int m = 0;  // BUG 12: Wrong init for negative numbers
        for(int i = 1; i < arr.length; i++)  // BUG 13: Skips first element
            if(arr[i] > m) m = arr[i];
        return m;
    }
    
    public int min(int[] arr) {  // BUG 14: Not static
        int m = 0;  // BUG 15: Wrong init
        for(int i = 1; i < arr.length; i++)  // BUG 16: Skips first
            if(arr[i] < m) m = arr[i];
        return m;
    }
    
    public int inversions(int[] arr) {  // BUG 17: Not static
        int cnt = 0;
        for(int i = 0; i < arr.length; i++)
            for(int j = i; j < arr.length; j++)  // BUG 18: Should be j=i+1
                if(arr[i] > arr[j]) cnt++;
        return cnt;
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(args[0]));  // BUG 19: No check
        BufferedWriter bw = new BufferedWriter(new FileWriter(args[1]));
        
        Q2_ArrayRotation ar = new Q2_ArrayRotation();
        int t = Integer.parseInt(br.readLine());
        
        for(int tc = 0; tc <= t; tc++) {  // BUG 20: Should be < t
            String[] nk = br.readLine().split(" ");  // BUG 21: No trim
            int n = Integer.parseInt(nk[0]);
            int k = Integer.parseInt(nk[1]);  // BUG 22: No validation k>=0
            
            int[] arr = new int[n];
            String[] nums = br.readLine().split(" ");  // BUG 23: No trim
            for(int i = 0; i < n; i++)
                arr[i] = Integer.parseInt(nums[i]);
            
            ar.rotate(arr, k);  // BUG 24: k not modded by n
            
            for(int i = 0; i < arr.length; i++)
                System.out.print(arr[i] + " ");  // BUG 25: Writing to stdout
            System.out.println();  // BUG 26: Writing to stdout
            
            System.out.println("Sum: " + ar.sum(arr));  // BUG 27: stdout
            System.out.println("Max: " + ar.max(arr));  // BUG 28: stdout
            System.out.println("Min: " + ar.min(arr));  // BUG 29: stdout
            System.out.println("Inv: " + ar.inversions(arr));  // BUG 30: stdout
        }
        
        br.close();
        bw.close();  // BUG 31: Not flushed
        // BUG 32: No finally
        // BUG 33: Rotation algorithm completely wrong
    }
}
