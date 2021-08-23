def compare_files(file1,file2,comment='#'):
    with open(file1) as f1:
        lines1 = f1.readlines()
    with open(file2) as f2:
        lines2 = f2.readlines()
    assert len(lines1) == len(lines2)
    for l1, l2 in zip(lines1,lines2):
        if l1.startswith(comment) and l2.startswith(comment):
            pass
        else:
            print(l1,l2)
            assert l1.strip() == l2.strip()
