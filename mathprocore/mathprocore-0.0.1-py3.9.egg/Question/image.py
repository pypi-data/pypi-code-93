import sympy, json, copy
#from Question.auto_fitter import auto_fit
#from Question.helpers import imgh

from Question.auto_fitter import auto_fit
from Question.helpers import imgh

class Image:
    """A class that can represent an arbitrary image (graphs, tables, or even shapes).
    Instance variables spelled with a leading underscore are not in the JSON representation."""

    none = None

    def update(self):
        """Every image object should implement this method if attributes other than it's expressions
        must be updated when a question is generated.
        """
        pass

    def preprocess(self, constants, pass_img):
        """Mutates the image such that its expressions are preprocessed, and additional info 
        needed in the map_placeholders method is saved.

        Every Image child implements preprocess and complete_template in a way specific to the 
        implementation of the class. The complete_template method relies on the return values of preprocess.
        See the child documentation for the what preprocess actions are taken.
        
        :param pass_img: Flag that determines if we will pass any arguments from the image to the solver.
        :type pass_img: bool
        """
        pass

    def map_placeholders(self, substitutions):
        """Returns a completed image after using substitutions to map placeholders to values.
        Also returns any arguments to be passed to the solver from the image. Does not mutate the original image.
        
        :param constants: A list of `Relation` objects.
        :type constants: list
        :param substitutions: A dictionary mapping placeholders to values.
        :type substitutions: dict

        """
        pass

    def complete(self):
        """Completes an image where the placeholder values are already specified.
        """
        pass

    def json(self):
        """Returns a json object that contains all the information associated with the Image."""
        json_dict = self.__dict__.copy()
        json_dict["imageType"] = type(self).__name__
        json_dict = { key: value for key, value in json_dict.items() if key[0] != "_" }
        return json_dict

class Graph(Image):
    """A class that represents plots of equations, piecewise equations, and points.
    Supports both Cartesian and Polar systems.

    :param expressions:
    :type expressions:
    :param focus: A dictionary with three keys: 'center', 'hdisp', 'vdisp'. The graph image will
        be centered at the tuple stored at focus['center'], with horizontal displacement focus['hdisp']
        and vertical displacement focus['vdisp'].
    :type focus: dict
    :param mode:
    :type mode:
    :param height:
    :type height:
    :param width:
    :type width:
    :param preserveAxisNumbers:
    :type preserveAxisNumbers:
    :param mathBounds:
    :type mathBounds:
    :param polarMode:
    :type polarMode:
    :param polarNumbers:
    :type polarNumbers:
    :param xAxisStep:
    :type xAxisStep:
    """
    screenshot_settings = ["mode", "height", "width", "preserveAxisNumbers", "mathBounds"]
    update_settings = ["polarMode", "polarNumbers", "xAxisStep"]

    def __init__(self, expressions, focus = None, show = None, **kwargs):
        """Constructor method."""
        assert all([key in (Graph.screenshot_settings + Graph.update_settings) for key in kwargs.keys()]), "invalid keyword arguments"
        self._focus = focus
        self._show = show

        self.expressions = expressions
        if type(self.expressions) != list:
            self.expressions = [expressions]

        # set default values
        self.screenshot = {
            "mode": 'stretch',
            "height": 200,
            "width": 200,
            "preserveAxisNumbers": True,
        }
        self.updateSettings = {
            "polarMode": False,
            "polarNumbers": False
        }
        # update with user-passed attributes
        self.screenshot.update({
            attr: kwargs.get(attr) for attr in Graph.screenshot_settings if attr in kwargs
        })
        self.updateSettings.update({
            attr: kwargs.get(attr) for attr in Graph.update_settings if attr in kwargs
        })

    def preprocess(self, constants, pass_img):
        """Preprocesses the graph such that all of its attributes are latex and the value placeholders 
        are delimited by dollar signs ($) to be filled in when map_placeholders is called.        

        :param constants: A list of `Relation` objects indicating the placeholders in the 
            graph's expressions.
        :type constants: list
        """
        if pass_img:
            self.solver_args = imgh.get_expr_strs_as_sympy(self)
        imgh.to_sympy(self)
        self.sympy_objs = self.expressions[:]
        imgh.to_latex(self, [ constant.var for constant in constants ])
   
    def map_placeholders(self, substitutions):
        """
        Returns a completed graph after using substitutions to map placeholders to values.
        Also returns any arguments to be passed to the solver from the graph's expressions. 
        Does not mutate the original graph.

        :param substitutions: A dictionary mapping placeholders to values.
        :type substitutions: dict
        """
        img = imgh.subs_latex(self, substitutions)
        complete_sympy_exprs = [ expr.subs(substitutions) for expr in self.sympy_objs ]
        img._compute_bounds(complete_sympy_exprs[0])
        solver_args = []
        if hasattr(self, "solver_args"):
            solver_args = [ expr.subs(substitutions) for expr in self.solver_args ]
        return img, solver_args

    def complete(self):
        imgh.to_sympy(self)
        self._compute_bounds()
        imgh.to_latex(self)

    def _compute_mathBounds(self):
        """Computes the Desmos API 'mathBounds' value."""
        bounds = {
            "left": float(self._focus["center"][0] - self._focus["hdisp"]),
            "right": float(self._focus["center"][0] + self._focus["hdisp"]),
            "top": float(self._focus["center"][1] + self._focus["vdisp"]),
            "bottom": float(self._focus["center"][1] - self._focus["vdisp"])
        }
        self.screenshot["mathBounds"] = bounds

    def _compute_bounds(self, expr=None):
        """Ensures the self.updateSettings and self.screenshot instance variables are finalized.
        That is, the window bounds specifications are finalized.

        :param expr: The sympy object to pass to auto_fit if one is not available in self.
        """

        if self._show: # client specifies bounds with the show command
            if expr == None:
                expr = self.expressions[0]
            params = auto_fit(expr, self._show)
            self.screenshot["mathBounds"] = params["mathBounds"]
            if "xAxisStep" in params:
                self.updateSettings["xAxisStep"] = params["xAxisStep"]
        else: # client specifies bounds with the focus command
            if "xAxisStep" in self.updateSettings:
                self.updateSettings["xAxisStep"] = float(self.updateSettings["xAxisStep"])
            if self._focus and "mathBounds" not in self.screenshot:
                self._compute_mathBounds()

    def update(self, func, *args):
        """Applies a given function to the focus and updateSettings attributes of a graph object.

        :param func: An arbitrary function.
        :type func: function
        :param \*args: The arguments the given function takes.
        """
        if self._focus:
            self._focus["center"] = [ func(e, *args) for e in self._focus["center"] ]
            self._focus["hdisp"] = func(self._focus["hdisp"], *args)
            self._focus["vdisp"] = func(self._focus["vdisp"], *args)
        if "xAxisStep" in self.updateSettings:
            self.updateSettings["xAxisStep"] = func(self.updateSettings["xAxisStep"], *args)

    def copy(self):
        """Creates and returns new Graph object identical to the current Graph."""
        return Graph(self.expressions, focus=copy.deepcopy(self._focus), show = self._show, **self.screenshot.copy(), **self.updateSettings.copy())

    def __repr__(self):
        return f"Graph({self.expressions}, {('focus', self._focus)}, {('show', self._show)}, {self.screenshot.items()}, {self.updateSettings.items()})"