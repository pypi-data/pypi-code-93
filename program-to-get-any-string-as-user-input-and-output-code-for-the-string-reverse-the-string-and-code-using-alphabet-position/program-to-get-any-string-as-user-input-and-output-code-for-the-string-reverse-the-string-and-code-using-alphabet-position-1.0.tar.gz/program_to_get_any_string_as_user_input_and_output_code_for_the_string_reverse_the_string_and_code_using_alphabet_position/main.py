# Program to get any string as user input and output code for the string reverse the string and code using alphabet position
def main():
    print(' '.join(str(ord(x) - ord('a') + 1) for x in input().lower()[::-1]))

if __name__ == "__main__":
    main()
