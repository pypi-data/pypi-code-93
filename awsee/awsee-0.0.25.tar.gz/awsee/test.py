from time import sleep
erase = '\033[A'
#erase = '\x1b[2K'

def download(number):
    print(erase + "File {} processed".format(number))

def completed(percent):
    print("({:1.1}% Completed)".format(percent))

def main():
    print("Question 1:", end=" ")
    resul = input()
    print(erase + "Question 2:", end=" ")
    resul = input()
    # for i in range(1,4):
    #     download(i)
    #     completed(i/10)
    #     sleep(1)
    

if __name__ == '__main__':
    main()
    