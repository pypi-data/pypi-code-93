import sympy

""" Helper functions to auto_fit. """
def expr_search(expr, found):
	"""Returns the (single) found expression nested within the larger expression.
	
	>>> # the expression is an absolute value function
	>>> expr_search( -4 * sympy.Abs(x + 1) + x, lambda expr: type(expr) == sympy.Abs)
	Abs(x + 1)
	"""
	if found(expr):
		return expr

	#print("expression: ", repr(expr))
	for e in expr.args:
		temp = expr_search(e, found)
		if temp:
			return temp

	return None

def cmp_bounds(center, max_dispx, max_dispy = None):
	"""Returns a json-style dictionary for the 'mathBounds' window."""

	if not max_dispy:
		max_dispy = max_dispx

	return {
		"mathBounds": {
			"left":   float(center[0] - max_dispx),
			"right":  float(center[0] + max_dispx),
			"top":    float(center[1] + max_dispy),
			"bottom": float(center[1] - max_dispy)
			}
		}

def cmp_quadratic_vertex_bounds(eq, ind_var, dep_var):
	""" Returns the bounds that contain the quadratic function's vertex.

	:param ind_var: The independent variable
	:param dep_var: The dependent variable
	"""
	if type(eq) == sympy.Equality:
		expr = sympy.solve(eq, dep_var, implicit = True)[0]
	else:
		expr = eq

	derivative = sympy.diff(expr, ind_var)
	
	ind_val = sympy.solve(derivative, ind_var)[0] #derivative equals zero --> quadratic hits its critical point
	dep_val = expr.subs(ind_var, ind_val)

	if sympy.symbols("x") == ind_var:
		center = (ind_val, dep_val)
	else:
		center = (dep_val, ind_val)

	max_disp = max(abs(ind_val), abs(dep_val)) / 3

	return cmp_bounds(center, max_disp)

def cmp_abs_val_vertex_bounds(expr, abs_val_expr, ind_var, dep_var):
	"""Returns the window that bounds the vertex of the linear abs-val function.

	:param expr: The overall equation that has variables x and y.
	:param abs_val_expr: The (single) absolute value expression within expr.
	""" 
	inner_expr = abs_val_expr.args[0]
	ind_pos = sympy.solve(inner_expr, ind_var)[0]

	dep_pos = sympy.solve(expr.subs(ind_var, ind_pos), dep_var)[0]
	
	if sympy.symbols("x") == ind_var:
		center = (ind_pos, dep_pos)
	else:
		center = (dep_pos, ind_pos)

	return cmp_bounds(center, abs(center[0]) * 3 / 2, abs(center[1]) * 3 / 2)

def auto_fit(eq, show):
	"""Computes the display parameters for a Graph.

	:param eq: A sympy.Eq object.
	:param show: The graph specifications
	:type show: str
	:rtype: dict
	"""

	valid_commands = ["intercepts", "roots", "quadratic-vertex", "absval-vertex"]
	assert show in valid_commands, "Not a valid show command."
	assert type(eq) != str, "Must pass a sympy object, not a str, to auto_fit."

	avg = lambda lst: sum(lst) / len(lst)
	x, y = sympy.symbols("x y")

	if show == "intercepts":
		"""Centers the graph at half the average of the intercepts.
		The graph's dimensions are double the maximum intercept value.
		Errors if the function does not have intercepts."""
		x_int = sympy.solve(eq.subs(y, 0), x)
		y_int = sympy.solve(eq.subs(x, 0), y)

		if len(x_int) == 0 and len(y_int) == 0:
			raise Exception(
				"Function displayed with show = 'intercepts' must have intercepts." + str(eq)
				)

		max_disp = abs(max(x_int + y_int, key = abs))

		if max_disp == 0:
			max_disp = 10 #default value

		def find_position(ints, safety):
			if len(ints) == 0:
				#no intercepts along an axis exist. use the other axis as a reference point
				return round(avg(safety) * 0.5, 2)
			else:
				return round(avg(ints) * 0.5, 2)

		center = (
			find_position(x_int, y_int), 
			find_position(y_int, x_int)
		)

		return cmp_bounds(center, max_disp)
	elif show == "roots":
		"""Displays a window that shows all roots of the arbitrary function.
		Errors if the function does not have any roots."""
		x_int = sympy.solve(eq.subs(y, 0), x)

		if len(x_int) == 0:
			raise Exception(
				"Function displayed with show = 'roots' must have x-intercepts." + str(eq)
				)

		max_dispx = abs(max(x_int, key = abs))
		max_dispy = max_dispx / 3
		center = (
			round(avg(x_int), 2), 
			0
		)

		return cmp_bounds(center, max_dispx, max_dispy)
	elif show == "quadratic-vertex":
		"""Displays the vertex of the function.
		"""
		if sympy.degree(eq, x) == 2:
			return cmp_quadratic_vertex_bounds(eq, x, y)
		elif sympy.degree(eq, y) == 2:
			return cmp_quadratic_vertex_bounds(eq, y, x)
		else:
			raise Exception(
				"Function displayed with show = 'quadratic-vertex' must have a vertex." + str(eq)
				)
	elif show == "absval-vertex":
		"""Only supports auto-fit for V shape abs-value functions.
		If an expression is passed, we assume it is a function.
		Raises an error if there is no absolute value term in the expression or equation."""
		if type(eq) == sympy.Eq:
			expr = eq.lhs - eq.rhs
		else:
			expr = eq

		abs_val_expr = expr_search(expr, lambda expr: type(expr) == sympy.Abs)

		if not abs_val_expr:
			raise Exception(
				"Function displayed with show = 'absval-vertex' must have an absolute value term." + str(eq)
				)

		standard = expr_search(abs_val_expr, lambda expr: x == expr)

		if standard:
			return cmp_abs_val_vertex_bounds(expr, abs_val_expr, x, y)
		else:
			return cmp_abs_val_vertex_bounds(expr, abs_val_expr, y, x)
