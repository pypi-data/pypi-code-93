from cpuset import CPUSet

if __name__ == '__main__':
    s = CPUSet.new("test")
    s.create()


