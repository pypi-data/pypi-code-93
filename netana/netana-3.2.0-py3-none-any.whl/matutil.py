#!/usr/bin/env python3
# Program to evaluate a Matrix
# created on Aug. 12, 2005 by jrbainter
# This function always evaluates the Matrix by selecting
# columun zero of the Matrix and calling "evalmat" recursivley
# with all the minors from col. zero and summing the results.
# A 2x2 Matrix is evaluated right away as this is the smallest
# Matrix to evaluate.
# Added "insertmat" function Aug. 16, 2005 jrbainter


def evalmat(mat):
    """Evaluate Matrix
        Called with a list of lists (Square Matrix)
        returns the value of the Matrix"""
    sign = 1
    result = 0
    if len(mat) == 2 and len(mat[0]) == 2:
        return ((mat[0][0]*mat[1][1]) - (mat[0][1]*mat[1][0]))
    else:
        nbrows = range(len(mat))
        for row in nbrows:
            if row % 2 == 0: sign = 1
            else: sign = -1
            minor = []
            if mat[row][0] == 0: continue # Don't mult by zero
            for mrow in nbrows:
                if mrow != row:    # remove current row from minor
                    minor.append(mat[mrow][1:]) # slice off column 0
            result += sign*mat[row][0]*evalmat(minor)
        return result

# Function to insert one Matrix (1,m) (data) in another Matrix (n,m) (mat)
# at location 'offset' and return the resulting Matrix (res).
# The lenght of "data" must be the same as the number of rows in  "mat".

def insertmat(mat, data, offset):
    """ Function to insert one Matrix (1,m) (data) in another Matrix (n,m) (mat)
        at location 'offset' and return the resulting Matrix (res).
        The lenght of "data" must be the same as the number of rows in  "mat";
        else an Assert Error exception will be issued. An exception will also
        be issued if the offset is out of range."""
    assert(len(mat) == len(data)), "insertmat: mat and data lenghts not the same."
    assert(offset >= 0 and offset < len(mat)), "insert: offset out of range"
    res = []
    for row in range(len(mat)):
        res.append(mat[row][:])       # insert matrix orignal data
        res[row][offset] = data[row]  # copy in data item
    return res

# Function to multiply tow matrix's and
# return result
#  |C| = |A| X |B|


def multmat(mata, matb):
    """ Multiply matrix A by Matrix B
    such that |C| = |A| X |B| """
    def sub_sum_product(mata,matb):
        """ Called form function 'multmat'
        not to be called from external programs...."""
        res_mat = []
        for colb in range(len(matb[0])):
            sum_product = 0
            for cola in range(len(mata)):
                sum_product += mata[cola] * matb[cola][colb]
            res_mat.append(sum_product)
        return res_mat
    result = []
    for rowa in range(len(mata)):
        result.append(sub_sum_product(mata[rowa], matb))
    return result


################ Tests #########################################

if __name__ == "__main__":
    print('Null Matrix Test')
    amat = [[1,1],[1,1]]
    print('Input Matrix = {}'.format(amat))
    ans = evalmat(amat)   #evaluate null Matrix
    PF = "Fail"
    if ans == 0: PF = "Pass"
    print('ans = {:d}, {:s}'.format(ans, PF))

    print()
    print('Unit Matrix Test')
    amat = [[1,0],[0,1]]
    print ('Input Matrix = {}'.format(amat))
    ans = evalmat(amat)   #evaluate unit Matrix
    PF = "Fail"
    if ans == 1: PF = "Pass"
    print('ans = {:d}, {:s}'.format(ans, PF))

    print()
    print ('3X3  Null Matrix Test')
    amat = [[0,1,6],[0,2,-3],[0,9,12]]
    print ('Input Matrix = {}'.format(amat))
    ans = evalmat(amat)   #evaluate 3x3 null Matrix
    PF = "Fail"
    if ans == 0: PF = "Pass"
    print('ans = {:d}, {:s}'.format(ans, PF))

    print()
    print ('3X3 Matrix Test')
    amat = [[3,1,6],[2,2,-3], [5,9,12]]
    print ('Input Matrix = {}'.format(amat))
    ans = evalmat(amat)   #evaluate 3x3 null Matrix
    PF = "Fail"
    if ans == 162: PF = "Pass"
    print ('ans = {:d}, {:s}'.format(ans, PF))

    print()
    print ('3X3 Unit Matrix Test')
    amat = [[1,0,0],[0,1,0], [0,0,1]]   #evaluate a 3x3 Unit Matrix
    print ('Input Matrix = {}'.format(amat))
    ans = evalmat(amat)
    PF = "Fail"
    if ans == 1: PF = "Pass"
    print ('ans = {:d}, {:s}'.format(ans, PF))

    print()
    print ('3X3 General Matrix Test')
    amat = [[3,5,1],[2,-2,2], [1,9,5]]
    print ('Input Matrix = {}'.format(amat))
    ans = evalmat(amat)   #evaluate a 3x3 General Matrix
    PF = "Fail"
    if ans == -104: PF = "Pass"
    print ('ans = {:d}, {:s}'.format(ans, PF))

    print()
    print ('5x5 More Complex Matrix Test')
    amat = [[0,1,2,3,4],[5,6,7,8,9], [10,11,12,13,14],
                     [15,16,17,18,19],[20,21,22,23,24]]    #evaluate a 5x5  Matrix
    print ('Input Matrix = {}'.format(amat))
    ans = evalmat(amat)
    PF = ("Fail")
    if ans == 0: PF = "Pass"
    print ('ans = {:d}, {:s}'.format(ans, PF))

    print()
    print ('Test "insertmat function" ')                 # offset = 2
    amat = [[1,2,3],[4,5,6],[7,8,9],[10,11,12]]
    imat = [100,200,300,400]
    print ('Input Matrix = {}'.format(amat))
    print ('Insert Data = {}'.format(imat))
    ans = insertmat(amat, imat, 2)
    PF = "Fail"
    if ans == [[1,2,100],[4,5,200],[7,8,300],[10,11,400]]: PF = "Pass"
    print ('ans = {}, {:s}'.format(ans, PF))

    print()
    ans = insertmat(amat, imat, 0)                      # offset = 0
    PF = "Fail"
    if ans == [[100,2,3],[200,5,6],[300,8,9],[400,11,12]]: PF = "Pass"
    print ('ans = {}, {:s}'.format(ans, PF))

    print()
    ans = insertmat(amat, imat, 1)                      # offset = 1
    PF = "Fail"
    if ans == [[1,100,3],[4,200,6],[7,300,9],[10,400,12]]: PF = "Pass"
    print ('ans = {}, {:s}'.format(ans, PF))

    print()
    print ('Test "multmat" function')
    print ('Test 1')
    a = [[1,2,3],[4,5,6],[1,2,3]]   # 3x3
    b = [[7,8],[1,2],[5,6]]         # 3x2
    print ('a = {}'.format(a))
    print ('b = {}'.format(b))
    c = multmat(a,b)
    PF = 'Fail'
    if c == [[24, 30], [63, 78], [24, 30]]: PF = 'Pass'
    print ('Result = {} {:s}'.format(c, PF))

    print()
    print ('Test 2')
    a = [[1,2],[4,5]]       # 2x2
    b = [[7,8],[1,2]]       # 2x2
    print ('a = {}'.format(a))
    print ('b = {}'.format(b))
    c = multmat(a,b)
    PF = 'Fail'
    if c == [[9, 12], [33, 42]]: PF = 'Pass'
    print ('Result = {} {:s}'.format(c, PF))

###### Time "evalmat" ############################
    import time
    print()
    print ('5x5 More Complex Matrix Timing Test')
    amat = [[0,1,2,3,4],[5,6,7,8,9], [10,11,12,13,14],
                     [15,16,17,18,19],[20,21,22,23,24]]    #evaluate a 5x5  Matrix
    print ('Input Matrix = {}'.format(amat))
    start = time.time()
    ans = evalmat(amat)
    stop = time.time()
    PF = ("Fail")
    if ans == 0: PF = "Pass"
    print ('ans = {:d}, {:s}'.format(ans, PF))
    print ('Time = {:.4f} ms.'.format(1000*(stop-start)))

####### Try 5x5 Mat matrix using numpy
    print()
    print('5x5 matrix using numpy')
    import numpy as np
    amat = np.arange(0,25).reshape(5,5)
    print ('amat = ', amat)
    start = time.time()
    ans = np.linalg.det(amat)
    stop = time.time()
    PF = ("Fail")
    if ans == 0: PF = "Pass"
    print ('numpy ans = {:f}, {:s}'.format(ans, PF))
    print ('Time = {:.4f} ms.'.format(1000*(stop-start)))

