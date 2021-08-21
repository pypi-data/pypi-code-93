import itertools
import numpy as np
import itertools




def shape_to_iterator(size):
    """
    A function to construct an iterator that loops over all elements of an array with a given size.
    Parameters:
        size(List(int)): A list of integers that represent the size of a given array.
    Returns:
        iterator: An iterator with loops over the complete object with size equal to size.
    """
    index_range = [range(k) for k in size]
    iterator = itertools.product(*index_range)
    return iterator


def tensor_index_to_data_index(index):
    """
    A function that converst a tensor index to the corresponding data index. 
    Say that index is equal to [k_1,l_1,k_2,l_2,\dots,k_n,l_n] than this function returns
    [k_1+l_1,k_2+l_2,\dots,k_n+l_n]. 
    If the length of the index is odd, we take the first index value as the index for
    multiple outputs. In this case we have that index is [i,k_1,l_1,k_2,l_2,\dots,k_n,l_n] 
    and return
    [i,k_1+l_1,k_2+l_2,\dots,k_n+l_n]. 
    Parameters:
        index(List(int)): The index in the tensor
    Returns:
        data_index(List(int)): The index of in the dataset. 
    """
    # In the odd-length-case, the first element of the index is static.
    if len(index)%2 == 1:
        return (index[0],) + tuple([k+l for k,l in zip(index[1::2],index[2::2])])
    else:
        return tuple([k+l for k,l in zip(index[::2],index[1::2])])
        

def format_number(a):
    """
    Function to format the number a. Integers and floats are treated differently.
    Parameters:
        a: A scalar of any type
    Returns: 
        formated_a(str): A string with the formatted number
    """
    if np.issubdtype(type(a), np.integer):
        return f'{a:4}'
    else:
        return f'{a:.2f}'


def array_to_row(A, new_line=False):
    """
    Function to create a latex string from a 1D array.
    Parameters:
        A: 1D numpy array.
    Returns:
        row: A string repr. of the array.
    """
    m = len(A)
    dtype = A.dtype
    if new_line:
        row = [f'{format_number(A[k])} & ' if k < (m - 1) else f'{format_number(A[k])}\\\\' for k in range(m)]
    else:
        row = [f'{format_number(A[k])} & ' if k < (m - 1) else f'{format_number(A[k])}' for k in range(m)]
    row = ''.join(row)
    return row


def export_matrix_as_latex(A, latex_matrix_type='bmatrix'):
    """
    A Function to print a 2D array to a latex matrix.
    Parameters:
        A: 2D numpy array.
        latex_matrix_type(str): type of latex matrix.
    Returns:
        latex_matrix(str): String formated in latex syntax.
    """
    n, m = A.shape
    array_body = ''
    array_definition = lambda body: f'\\begin{{{latex_matrix_type}}}\n{body}\n\\end{{{latex_matrix_type}}}'
    for k in range(n):
        new_line = not (k == n - 1)
        if new_line:
            array_body += '\t' + (array_to_row(A[k, :], new_line)) + '\n'
        else:
            array_body += '\t' + (array_to_row(A[k, :], new_line))
    latex_matrix = array_definition(array_body)
    return latex_matrix


def export_SS_as_latex(SS, latex_matrix_type='bmatrix'):
    """
    A function to export an entire state space model to latex.
    Parameters:
        SS: A 2D state space model
    Returns:
        latex(str): A string repr. of the state space model formatted in latex syntax.
    """
    # Transform C to a 2D array
    C = np.array([SS['C']])
    # Transform x to a 2D array
    x0 = np.array([SS['x0']]).T
    A_latex = 'A = ' + export_matrix_as_latex(SS['A'], latex_matrix_type)
    B_latex = 'B = ' + export_matrix_as_latex(SS['B'], latex_matrix_type)
    C_latex = 'C = ' + export_matrix_as_latex(C, latex_matrix_type)
    x_latex = 'x_{0,0} = ' + export_matrix_as_latex(x0, latex_matrix_type)
    # Add a title to the print if a model_name is provided.    
    title = ('-') * 20 + SS['model_name'] + ('-') * 20 if SS['model_name'] else ''
    end_line = ('-') * 40
    latex = '\n'.join([title, A_latex, B_latex, C_latex, x_latex, end_line])
    return latex
