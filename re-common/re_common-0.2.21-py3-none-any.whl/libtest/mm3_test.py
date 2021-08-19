from re_common.vip.mmh3Hash import Mmh3Hash

if __name__ == "__main__":
    mmh3Test = Mmh3Hash("bs")
    print(mmh3Test.generatehashPath('7001469049.pdf', '2017', 'cn'))