x = [1,6,3,7,2,4,5,8,9,10]

print(len(x))
counter = 0
for i in range(0,10,3):
    chunk = x[i:i+3]
    print(chunk)
    for ele in chunk:
        counter +=1
        print(ele)

print(counter)