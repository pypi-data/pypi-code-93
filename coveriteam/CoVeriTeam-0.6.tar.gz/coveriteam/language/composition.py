# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

from coveriteam.language.actor import Actor

# TODO find a better way to do this
from benchexec.result import RESULT_CLASS_FALSE  # noqa: F401,F403,E261
from benchexec.result import RESULT_CLASS_TRUE  # noqa: F401,F403,E261
from coveriteam.language.artifact import *  # noqa: F401,F403,E261
from coveriteam.language import CoVeriLangException
from coveriteam.util import filter_dict, dict_clash, collect_variables
from xml.etree import ElementTree
from textwrap import indent


def infer_types(exp):
    d = {}
    # TODO At the moment it is rudimentory. Putting Artifact for everything
    for name in collect_variables(exp):
        if not name.startswith("RESULT_CLASS"):
            d[name] = Artifact

    return d


class CompositeActor(Actor):
    def name(self):
        try:
            return self._name
        except AttributeError:
            return type(self).__name__

    def set_name(self, name):
        # This is only in the composite actor.
        # The names of the atomic actors come from the actor definition.
        self._name = name

    def forward_artifacts(self, available, renaming, required):
        """
        This function does two things:
        1) Selects the artifacts to be passed to a subcomponent from the available
           artifacts.
        2) Applies renaming if neccessary.
        """
        # TODO at the moment renaming is not considered
        return filter_dict(available, required)


def set_composite_actor_name(actor, name):
    if isinstance(actor, CompositeActor):
        actor.set_name(name)
    else:
        raise CoVeriLangException(
            "Setting name is only supported for composite actors."
        )


class Sequence(CompositeActor):
    def __init__(self, a1: Actor, a2: Actor):
        self.first = a1
        self.second = a2
        self._input_artifacts = self._infer_input_type(a1, a2)
        self._output_artifacts = a2.get_output_artifacts().copy()

    def _act(self, **kwargs):
        kwargs1 = self.forward_artifacts(kwargs, {}, self.first.get_input_artifacts())
        res1 = self.first.act(**kwargs1)
        # This is ugly, but it works
        new_args = filter_dict({**kwargs, **res1}, self.second.get_input_artifacts())
        ret_val = self.second.act(**new_args)
        self.gen_xml_elem(kwargs, ret_val)
        return ret_val

    def __type_check(self):
        a1 = self.a1
        a2 = self.a2
        # At the moment the type checking for sequence is suspended, as the rules have changed.
        # TODO need to check covariance here.
        # TODO This will not check the item but only the names.
        # This should be changed if we do proper type inference.
        """if not a2.get_input_artifacts().items() <= a1.get_output_artifacts().items():"""
        if not a2.get_input_artifacts().keys() <= a1.get_output_artifacts().keys():
            raise CoVeriLangException(
                "Components {} \n and \n {} cannot be composed in sequence."
                "Type check failed.".format(a1, a2)
            )

    def __str__(self):
        return (
            "\nSEQUENCE"
            + self.__get_actor_type_str__()
            + "\n"
            + indent(str(self.first), "\t")
            + "\n"
            + indent(str(self.second), "\t")
        )

    def gen_xml_elem(self, inputs, outputs):
        super().gen_xml_elem(inputs, outputs)
        first = ElementTree.Element("first")
        first.append(self.first.xml_elem)
        second = ElementTree.Element("second")
        second.append(self.second.xml_elem)

        self.xml_elem.append(first)
        self.xml_elem.append(second)

    def _infer_input_type(self, a1, a2):
        ip1 = a1.get_input_artifacts().copy()
        ip2 = a2.get_input_artifacts().copy()
        op1 = a1.get_output_artifacts().copy()

        # TODO check the name clash with two different types

        # First do ip2 -op1, i.e, get the artifacts which cannot be provided
        # by the first actor.
        for k in op1.keys():
            ip2.pop(k, None)
        for k in ip1.keys():
            ip2.pop(k, None)

        return {**ip1, **ip2}


class ITE(CompositeActor):
    """Concerns faced:
    1) the condition might need a variable which is not required by the composing actors.
    -- To avoid this at the moment it is allowd that the inputs could be more than
    required by the composing actors."""

    def __init__(self, cond, a1, a2=None):
        self.__type_check(a1, a2)
        self.cond = cond
        self.first = a1
        self.second = a2
        self._input_artifacts = a1.get_input_artifacts().copy()
        self._output_artifacts = a1.get_output_artifacts().copy()
        self._add_types_from_cond(cond)

    def _act(self, **kwargs):
        # Tried using ast.literal_eval but couldn't use it. Still check it once more
        # noqa because can't pass kwargs to ast.literal_eval
        cond_val = eval(self.cond, globals(), {**kwargs})  # noqa: S307
        if cond_val:
            args_to_pass = self.forward_artifacts(
                kwargs, {}, self.first.get_input_artifacts()
            )
            ret_val = self.first.act(**args_to_pass)
        elif self.second:
            # TODO check if this and the one in if condition are same
            args_to_pass = self.forward_artifacts(
                kwargs, {}, self.second.get_input_artifacts()
            )
            ret_val = self.second.act(**args_to_pass)
        else:
            # In this case the values from the inputs are forwarded.
            ret_val = filter_dict(kwargs, self._output_artifacts)

        self.gen_xml_elem(kwargs, ret_val, cond_val)
        return ret_val

    def __type_check(self, a1, a2):
        # TODO need to check covariance here.
        if not a2:
            if not (
                a1.get_output_artifacts().items() <= a1.get_input_artifacts().items()
            ):
                # In this case we still would like to check if the inputs could be forwarded.
                raise CoVeriLangException(
                    "Type check failed for ITE composition."
                    "Second component is needed. All the outputs cannot be assigned from input."
                )
        elif (
            a1.get_input_artifacts() != a2.get_input_artifacts()
            or a1.get_output_artifacts() != a2.get_output_artifacts()
        ):
            raise CoVeriLangException(
                "Components \n {} \n and \n {} cannot be composed in choice."
                "Type check failed.".format(a1, a2)
            )

    def __str__(self):
        return (
            "\nITE"
            + self.__get_actor_type_str__()
            + "\n"
            + indent(str(self.first), "\t")
            + "\n"
            + indent(str(self.second), "\t")
        )

    def gen_xml_elem(self, inputs, outputs, cond_val):
        super().gen_xml_elem(inputs, outputs)
        cond_elem = ElementTree.Element("condition")
        cond_elem.text = str(cond_val)
        self.xml_elem.append(cond_elem)
        if cond_val:
            self.xml_elem.append(self.first.xml_elem)
        elif self.second:
            self.xml_elem.append(self.second.xml_elem)

    def _add_types_from_cond(self, cond):
        t = infer_types(cond)
        self._input_artifacts = {**t, **self._input_artifacts}


class Iterative(CompositeActor):

    # I think every can be run iteratively. Two cases arise which need to be handled:
    # 1) What if all the outputs are disregarded - It is still a valid composition
    # 2) if outputs are to be fed to inputs but have different names
    def __init__(self, terminationCondition, a: Actor):
        self.__type_check(a)
        self.actor = a
        self.terminationCondition = terminationCondition
        self._input_artifacts = a.get_input_artifacts()
        self._output_artifacts = a.get_output_artifacts()
        # TODO This is making it stateful, might create a problem later.
        self._iteration_count = 0
        self.__child_xml_elems = []
        # TODO Put it in type check too
        self.__artifacts_to_accumulate = (
            a.get_output_artifacts().keys() - a.get_input_artifacts().keys()
        )
        self.__accumulated_artifacts = {}

    def _act(self, **kwargs):
        # TODO Maybe it is a better idea to keep all the objects as they go along.
        # This might solve the xml generation issues.
        res = self.actor.act(**kwargs)
        self.__do_step_iteration_post_process(kwargs, res)
        # BEWARE!! to think if it is OK. This is out of syn with the paper.
        # We have said that inputs are subset of outputs, but here we don't necessarily assume that.

        newargs = {**kwargs, **res}
        if self.__check_termination_condition(kwargs, res):
            updated_args = {**newargs, **self.__accumulated_artifacts}
            ret_val = self.forward_artifacts(
                updated_args, {}, self.actor.get_output_artifacts()
            )
        else:
            args_to_pass = self.forward_artifacts(
                newargs, {}, self.actor.get_input_artifacts()
            )
            ret_val = self.act(**args_to_pass)

        self.gen_xml_elem(
            self.forward_artifacts(newargs, {}, self.actor.get_output_artifacts())
        )
        return ret_val

    def __type_check(self, a):
        """
        In iterative composition the type check only checks if there is at least one
        artifact which can be fed back to the actor.
        Other artifacts retain their initial values.
        """
        if not (a.get_input_artifacts().items() & a.get_output_artifacts().items()):
            raise CoVeriLangException(
                "Component \n {} cannot be composed with itself for iteration. "
                "There is no artifact to feed back in iteration. "
                "Type check failed.".format(a)
            )

    def __check_termination_condition(self, kwargs, res):
        # TODO at the moment I am assuming termination condition to be a common variable in the input and output.
        # Lets see if it is enough or we need to make it more expressive.
        return kwargs[self.terminationCondition] == res[self.terminationCondition]

    def __do_step_iteration_post_process(self, it_input, it_output):
        self.__collect_xml_elems(it_input)

        # Collect artifacts
        for k in self.__artifacts_to_accumulate:
            if k in self.__accumulated_artifacts:
                self.__accumulated_artifacts[k] = self.__accumulated_artifacts[k].join(
                    it_output[k]
                )
            else:
                self.__accumulated_artifacts[k] = it_output[k]

    def __collect_xml_elems(self, inputs):
        if self._iteration_count == 0:
            self.__initial_inputs = inputs
        it_elem = ElementTree.Element(
            "Iteration", {"count": str(self._iteration_count)}
        )
        it_elem.append(self.actor.xml_elem)
        self.__child_xml_elems.append(it_elem)
        self._iteration_count += 1

    def gen_xml_elem(self, outputs):
        super().gen_xml_elem(self.__initial_inputs, outputs)

        for i in self.__child_xml_elems:
            self.xml_elem.append(i)

    def __str__(self):
        return (
            "\nREPEAT"
            + self.__get_actor_type_str__()
            + "\n"
            + indent(str(self.actor), "\t")
        )


class Parallel(CompositeActor):
    def __init__(self, a1: Actor, a2: Actor):
        # TODO uncomment the type check. Removed it only for testing
        self.first = a1
        self.second = a2
        # TODO make a copy
        self._input_artifacts = {**a1.get_input_artifacts(), **a2.get_input_artifacts()}
        self._output_artifacts = {
            **a1.get_output_artifacts(),
            **a2.get_output_artifacts(),
        }

    def _act(self, **kwargs):
        # TODO It might not work as the arguments passed are more than required
        # TODO project the arguments as required
        kwargs1 = self.forward_artifacts(kwargs, {}, self.first.get_input_artifacts())
        kwargs2 = self.forward_artifacts(kwargs, {}, self.second.get_input_artifacts())
        res1 = self.first.act(**kwargs1)
        res2 = self.second.act(**kwargs2)
        ret_val = {**res1, **res2}
        self.gen_xml_elem(kwargs, ret_val)
        return ret_val

    def __type_check(self, a1, a2):
        # It just checks if the inputs and outputs are disjoint.
        # TODO commenting out the input type check as it was causing the problem.
        # Conflict cases: simple validated verifier, and meta val

        # TODO I wonder why is the following working. Inputs should be allowed to be shared.
        if dict_clash(a1.get_input_artifacts(), a2.get_input_artifacts()):
            raise CoVeriLangException(
                "Components \n {} \n and \n {} cannot be composed in parallel."
                "Input names clash. There is an input with the same name and"
                "different artifact type. Type check failed.".format(a1, a2)
            )
        if not a1.get_output_artifacts().keys().isdisjoint(a2.get_output_artifacts()):
            raise CoVeriLangException(
                "Components \n{} \nand \n {} cannot be composed in parallel."
                "Output names should be disjoint. Type check failed.".format(a1, a2)
            )

    def __str__(self):
        return (
            "\nPARALLEL"
            + self.__get_actor_type_str__()
            + "\n"
            + indent(str(self.first), "\t")
            + "\n"
            + indent(str(self.second), "\t")
        )

    def gen_xml_elem(self, inputs, outputs):
        super().gen_xml_elem(inputs, outputs)
        self.xml_elem.append(self.first.xml_elem)
        self.xml_elem.append(self.second.xml_elem)
