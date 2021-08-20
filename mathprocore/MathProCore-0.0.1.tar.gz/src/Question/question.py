import copy
import json
import random
import sympy
from Question.nums import *
from Question.image import *
from Question.helpers import exprh, imgh
from Question.helpers.csympy.printing.latex import latex as clatex


# for the later parameter transformations=transforms in sympify
latex_params = {
    "order": "none",
    "inv_trig_style": "power"
}

def question_as_json(prompt=None, prompt_image=Image.none, answer=None, answer_image=Image.none, directions="", sub_topic=""):
    """Returns the json instructions for creating a question."""

    assert not prompt or type(prompt) == str
    assert prompt_image is Image.none or isinstance(prompt_image, Image)
    assert not answer or type(answer) == str
    assert answer_image is Image.none or isinstance(answer_image, Image)
    assert type(directions) == str
    assert type(sub_topic) == str

    data = {
        "type": sub_topic,
        "directions": directions,
        "q-data": {
            "prompt": prompt,
            "answer": answer,
            "promptImage": {},
            "answerImage": {}
        }
    }
    if prompt_image:
        data["q-data"]["promptImage"] = prompt_image.json()
    if answer_image:
        data["q-data"]["answerImage"] = answer_image.json()
    return data

class QuestionGenerator(object):
    """A class that represents a generator object that produces :class:`Question` objects.

    :param prompts: A list of (or one) parseable strings that represents the question.
    :type prompts: str or list, optional
    :param img: An image included in the prompt of a generated question.
    :type img: Image, optional
    :param solver: A function applied to the sympy expressions in the prompt that returns an answer.
        The returned answer can either be sympy/string object, an Image object, or both (in the form of a tuple).
    :type solver: function
    :param constants: A list of `Relation` instances for each variable to substitute.
    :type constants: list
    :param permute: A boolean Flag that determines if the expression/equation should be algebraically
        shuffled (currently only supported over addition)
    :type permute: bool, optional
    :param pass_img: A boolean Flag that determines if img expressions will be passed to the solver. Defaults to True.
    :type pass_img: bool, optional
    :param directions: A latex string that will be shown to the student as instructions for this question.
    :type directions: str, optional
    :param sub_topic: A plain-text string that can be used to categorize questions (outsource this functionality at scale).
    :type sub_topic: str, optional
    """

    @staticmethod
    def permute(sympy_obj):
        """Generates a random permutation of a sympy object.

        :param sympy_obj: A sympy object.
        :type sympy_obj: sympy.core.expr.Expr
        :returns: A random permutation of the original sympy object.
        :rtype: sympy.core.expr.Expr
        """
        # print(f"permuting {sympy_obj}")
        if isinstance(sympy_obj, (sympy.Number, sympy.Symbol)):
            # base case: we can't permute a constant
            return sympy_obj
        elif isinstance(sympy_obj, sympy.Rel):
            # index 0 is new left side, index 1 is new right side
            args = [[], []]
            # for each side,  (i=0 --> left side, i=1 --> right side)
            for i in range(len(args)):
                side = (sympy_obj.lhs, sympy_obj.rhs)[i]
                if isinstance(side, sympy.core.add.Add):
                    # decide whether each term will move to the other side
                    for term in side.args:
                        if random.choice([True, False]):
                            # if it does swap, multiply it by -1
                            args[1-i] += [sympy.Mul(sympy.sympify('-1',
                                                    evaluate=False), term)]
                        else:
                            args[i] += [term]
                else:
                    # if there's only one, decide if that'll move over
                    if not isinstance(side, sympy.core.numbers.Zero):
                        if random.choice([True, False]):
                            args[1-i] += [sympy.Mul(sympy.sympify('-1',
                                                    evaluate=False), side)]
                        else:
                            args[i] += [side]
            del side
            # now we turn each side into a sympy object
            # this is in a new loop cause' we want to shuffle both the left and right hand sides before that
            for i in range(len(args)):
                # we also want
                args[i] = [QuestionGenerator.permute(term) for term in args[i]]
                if len(args[i]) > 1:
                    # add a number of terms
                    args[i] = sympy.Add(*args[i], evaluate=False)
                elif len(args[i]) == 1:
                    # leave a single term alone
                    args[i] = args[i][0]
                else:
                    # replace an empty side with 0
                    args[i] = sympy.sympify('0', evaluate=False)
            args = tuple(args)
        elif isinstance(sympy_obj, (sympy.Add, )):
            # permute the members of each term
            args = [QuestionGenerator.permute(term) for term in sympy_obj.args]
            # then permute the terms themselves
            random.shuffle(args)
            obj = sympy.Add(*args, evaluate=False)
            return obj
        else:
            # it's not either a `Relation` or an `Add` so we should just permute its members
            args = [QuestionGenerator.permute(term) for term in sympy_obj.args]
        # Finally, put it back together
        return sympy_obj.func(*args, evaluate=False)

    @staticmethod
    def validate_input(prompts, img, solver, constants, permute, pass_img, pass_constants, directions, sub_topic):
        if not prompts and not img:
            raise TypeError("QuestionGenerator() takes at least 1 'prompts' or 'img' argument (0 given)")
        if prompts:
            if type(prompts) not in [str, list]:
                raise TypeError(f"'prompts' must be a string or list, not {type(prompts)}")
            if type(prompts) == list and any(type(p) != str for p in prompts):
                raise TypeError("'prompts' list may only contain strings")
        if img != Image.none and not isinstance(img, Image):
            raise TypeError(f"'img' must be of type Image, not {type(img)}")
        if not solver or not hasattr(solver, "__call__"):
            raise TypeError("'solver' must be callable")
        if type(constants) != list or any(type(r) != Relation for r in constants):
            raise TypeError("'constants' must be a list of Relation objects")
        if type(directions) != str:
            raise TypeError(f"'directions' must be a string, not {type(directions)}")
        if type(sub_topic) != str:
            raise TypeError(f"'sub_topic' must be a string, not {type(sub_topic)}")
        if type(permute) != bool:
            raise TypeError(f"'permute' must evaluate to True or False, not {type(permute)}")
        if type(pass_img) != bool:
            raise TypeError(f"'pass_img' must evaluate to True or False, not {type(pass_img)}")
        if type(pass_constants) != bool:
            raise TypeError(f"'pass_constants' must evaluate to True or False, not {type(pass_constants)}")

    def __init__(self,
                 prompts=None, img=Image.none, solver=None,
                 constants=[],
                 permute=False, pass_img=True, pass_constants=False,
                 directions="", sub_topic=""):
        """Constructor method.
        """   
        QuestionGenerator.validate_input(prompts, img, solver, constants, permute, pass_img, pass_constants, directions, sub_topic)
        self.prompts = prompts
        self.img = img
        self.solver = solver
        self.permute = permute
        self.pass_img = pass_img
        self.pass_constants = pass_constants
        self.directions = directions
        self.sub_topic = sub_topic

        # solve the system of relations for a set of independent and dependent constants
        self.matrices = [ rel for rel in constants if rel.matrix is not None ]
        self.constants = [ rel for rel in constants if rel.expr == "" and rel.matrix is None ] # independent placeholders
        if len(self.constants) + len(self.matrices) != len(constants):
            self.relations = random.choice(
                sympy.solve(
                    [sympy.Eq(rel.var, rel.expr, evaluate=False)
                     for rel in constants if rel.expr != ""],
                    [rel.var for rel in constants],
                    exclude=[c.var for c in self.constants],
                    dict=True
                )
            )

        # prepare the prompts
        if prompts:
            if isinstance(prompts, str):
                prompts = [prompts]
            self.prompts = [exprh.process_prompt(p, self.matrices) for p in prompts]

        # prepare the images
        if img:
            self.img = img
            self.img.preprocess(constants, pass_img)

    def gen_placeholders(self):
        """Returns a mapping between value placeholders and values to replace them.
        Randomizes every question's values. Called in the __next__ method.
        """
        zero, one = sympy.symbols("_zero"), sympy.symbols("_one")
        predefs = {
            "degrees": sympy.pi/180,
            zero: 0,
            one: 1
        }
        sol = { rel.var: rel.default().subs(predefs) for rel in self.constants }
        sol.update(predefs)
        if hasattr(self, "relations"):
            sub = { var: val.subs(sol) for var, val in self.relations.items() } # placeholder values defined relative to others
            sol.update(sub)
        mats = { sympy.MatrixSymbol(str(m.var), 0, 0): m.default() for m in self.matrices }
        return sol, mats

    def map_placeholders(self, prompt, substitutions):
        """Returns the prompt after permuting and substituting values into the 
        template prompt input.

        :param prompt: A tuple containing the text (words or latex) and expression strings associated with a single prompt.
        :type prompt: tuple
        :param substitutions: A mapping between value placeholders and values to replace them.
        :type substitutions: dict
        :returns: The prompt-string with the expression-strings turned into filled in latex strings,
            and a list of sympy objects representing the sympy equivalents of the expression-strings.
        """
        expression_strings, solver_args = [], [] 
        text, expressions = prompt # destructuring the prompt
        for expr in expressions:
            if self.permute:
                expr = QuestionGenerator.permute(expr)
            expr = expr.subs(substitutions[1])
            solver_arg = exprh.subs(
                expr,
                substitutions[0]
            )
            solver_args.append(solver_arg)
            e = clatex(solver_arg, **latex_params)
            expression_strings.append(exprh.replace(e))
        text = text.copy()
        for i in range(len(expression_strings)):
            text.insert(2 * i + 1, expression_strings[i])
        mapped_prompt = exprh.final_replace(" ".join(text))
        return mapped_prompt, solver_args

    def __next__(self):
        # constants
        substitutions = self.gen_placeholders()
        solver_args = []
        if self.pass_constants:
            solver_args.append({ str(var): val for var, val in substitutions[0].items() })
            solver_args.append({ str(var): val for var, val in substitutions[1].items() })

        # prompts
        prompt_string = None
        if self.prompts:
            prompt = random.choice(self.prompts)
            prompt_string, prompt_solver_args = self.map_placeholders(prompt, substitutions)
            solver_args.extend(prompt_solver_args)

        # image
        img = Image.none
        if self.img:
            img, img_solver_args = self.img.map_placeholders(substitutions[0])
            solver_args.extend(img_solver_args)

        # answer
        solution = self.solver(*solver_args)
        if type(solution) != tuple:
            solution = (solution, None)
        ans, img_ans = solution
        if isinstance(ans, Image):
            img_ans, ans = ans, img_ans
        if not (ans is None or type(ans) == str):
            ans = exprh.final_replace(exprh.replace(clatex(ans, **latex_params)))
        if img_ans:
            img_ans.complete()

        return question_as_json(prompt_string, img, ans, img_ans, self.directions, self.sub_topic)

    def __iter__(self):
        return self