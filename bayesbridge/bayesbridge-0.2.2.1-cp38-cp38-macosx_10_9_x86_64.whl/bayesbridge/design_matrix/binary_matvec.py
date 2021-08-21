def dot(self, x, transpose=False):
    result = np.zeros(self.shape[transpose])
    cdef
    double[:]
    x_view = x
    cdef
    double[:]
    result_view = result
    matvec_status = mkl_plain_matvec(
        self.A, & x_view[0], & result_view[0], int(transpose)
    )
    return result



cdef mkl_plain_matvec(
		sparse_matrix_t A, const double* x, double* result, bint transpose
	):

	cdef sparse_operation_t operation
	if transpose:
		operation = SPARSE_OPERATION_TRANSPOSE
	else:
		operation = SPARSE_OPERATION_NON_TRANSPOSE
	cdef double alpha = 1.
	cdef double beta = 0.
	cdef matrix_descr mat_descript
	mat_descript.type = SPARSE_MATRIX_TYPE_GENERAL
	status = mkl_sparse_d_mv(
		operation, alpha, A, mat_descript, x, beta, result
	)
	return status