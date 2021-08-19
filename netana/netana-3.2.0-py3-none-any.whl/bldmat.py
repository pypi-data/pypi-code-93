#!/usr/bin/env python3
# The module is used to build a square matrix
# files with a passed in item


def bldmat(nbrow=2,nbcol=2,obj='0'):
    """Build matrix of obj's nbrows by nbcols.
    Call: bldmat(nbrow=2,nbcol=2,obj='0')
    Returns: Matrix (list of lists) of obj."""
    res = []
    for row in range(nbrow):
        temp = []
        for col in range(nbcol):
            temp.append(obj)
        if nbrow == 1:
            return temp
        res.append(temp)
    return res



################### Tests ############################

if  __name__ == "__main__":

    mat = bldmat(10,10)
    print('10X10 "0" matrix')
    print('{}'.format(mat))

    mat = bldmat(1,10)
    print('1X10 "0" matrix')
    print('{}'.format(mat))

    mat = bldmat(3,3,'A')
    print('3X3 "A" matrix')
    print('{}'.format(mat))
    mat[0][0] = 'B'
    print('{}'.format(mat))
