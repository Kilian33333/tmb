import math
while 1:
    i=1000
    base = int(input("Base:"))
    while i > 0:
        i -= 1
        print (int(base / math.log(abs(i/3) + 2)))