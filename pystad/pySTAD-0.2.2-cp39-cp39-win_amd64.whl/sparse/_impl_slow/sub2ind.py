def sub2ind(i: int,  j: int, n: int):
  """
  Computes the index in a condensed matrix for a row and column location in a 
  dense matrix.
  
  Parameters
  ----------
  i : unsigned int 
    The row value.
  j : unsigned int
    The column value.
  n : unsigned int
    The number of nodes in the distance matrix (N x N).
  Returns
  -------
    The index in the condensed matrix. -1 if the given values do not exist in 
    a condensed distance matrix of the given size.
  """
  if i == j:
    return -1
  if i < j:
      i, j = j, i
  a = n*j
  b = j*(j+1)//2 + i - 1 - j
  if a < b:
    return -1
  return a - b
