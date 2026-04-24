def main():
    # declarations
    arr = [0] * 5
    i = 0
    s = 0
    
    # statements
    i = 1
    while (i <= 5):
        arr[i - 1] = (i * 2)
        i = (i + 1)
    s = 0
    for i in range(1, 5 + 1):
        s = (s + arr[i - 1])
    print(str('Sum = '), str(s), sep='', end='\n')

if __name__ == '__main__':
    main()
