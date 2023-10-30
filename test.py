import math
n = int(input())
print(math.floor(n / 3) * 2 + int(n % 3 != 0))