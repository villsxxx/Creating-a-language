def five():
    _five_ret = 0
    _five_ret = 5
    return _five_ret

def main():
    x = 0
    
    x = five()
    print(str('x = '), str(x), sep='', end='\n')

if __name__ == '__main__':
    main()
