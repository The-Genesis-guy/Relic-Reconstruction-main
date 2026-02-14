import heapq

k = int(input())

h = []
arrays = []

for i in range(k):
    parts = list(map(int, input().split()))
    n = parts[0]
    arr = parts[1:]
    arrays.append(arr)
    if n > 0:
        heapq.heappush(h, (arr[0], i, 1))

res = []

while h:
    v, i, j = heapq.heappop(h)
    res.append(v)
    if j < len(arrays[i]):   # fixed condition
        heapq.heappush(h, (arrays[i][j], i, j + 1))

print(" ".join(map(str, res)))
 