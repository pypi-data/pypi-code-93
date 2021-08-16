from hyperc.pddl import Predicate, Parameter


class BaseAction:
    def __init__(self, parent, value, *args):
        self.parent, self.value, self.args = parent, value, args

    def precondition(self):
        preconds = list()
        for action in self.value._self_actions:
            preconds.extend(action.precondition())
        return preconds

    def params(self):
        params = list()
        for action in self.value._self_actions:
            params.extend(action.params())
        params.append(Parameter(var=self.value, type=self.value._self_cls()))
        return params

    def effect(self):
        effects = list()
        for action in self.value._self_actions:
            effects.extend(action.effect())
        return effects


class ObjectGetattr(BaseAction):

    def __init__(self, parent, value, *args):
        super().__init__(parent, value, *args)
        self.name = args[0]

    def precondition(self):
        preconds = super().precondition()
        preconds.append(f'({self.parent._self_cls()}-{self.name} {self.parent._self_var()} {self.value._self_var()})')
        return preconds

    def goal(self):
        assert len(self.value._self_actions) == 1
        action = self.value._self_actions[0]
        assert isinstance(action, ObjectEq)  # Hardcoded atm
        return Predicate(fact=f'{self.parent.__class__.__name__}-{self.name}',
                         vars=[self.parent._self_obj(), action.value._self_obj()],
                         negated=False)


class ParamGetattr(BaseAction):

    def __init__(self, parent, value, *args):
        super().__init__(parent, value, *args)
        self.name = args[0]

    def precondition(self):
        preconds = super().precondition()
        preconds.append(f'({self.parent._self_cls()}-{self.name} {self.parent._self_var()} {self.value._self_var()})')
        return preconds

    def goal(self):
        assert len(self.value._self_actions) == 1
        action = self.value._self_actions[0]
        assert isinstance(action, ObjectEq)  # Hardcoded atm
        return Predicate(fact=f'{self.parent.__class__.__name__}-{self.name}',
                         vars=[self.parent._self_obj(), action.value._self_obj()],
                         negated=False)


class ObjectSetattr(BaseAction):

    def __init__(self, parent, value, *args):
        super().__init__(parent, value, *args)
        self.name, self.other = args

    def effect(self):
        effects = super().effect()
        effects.append(
            Predicate(fact=f"{self.parent._self_cls()}-{self.name}", vars=[self.parent._self_obj(),
                                                                           self.other._self_obj()],
                      negated=True))
        effects.append(
            Predicate(fact=f"{self.parent._self_cls()}-{self.name}", vars=[self.parent._self_obj(),
                                                                           self.value._self_obj()]))
        return effects


class ParamSetattr(BaseAction):

    def __init__(self, parent, value, *args):
        super().__init__(parent, value, *args)
        self.name, self.other = args

    def precondition(self):
        preconds = super().precondition()
        preconds.append(
            Predicate(fact=f'{self.parent._self_cls()}-{self.name}', vars=[self.parent._self_var(),
                                                                           self.value._self_var()]))
        return preconds

    def effect(self):
        effects = super().effect()
        effects.append(
            Predicate(fact=f"{self.parent._self_cls()}-{self.name}", vars=[self.parent._self_var(),
                                                                           self.other._self_var()],
                      negated=True))
        effects.append(
            Predicate(fact=f"{self.parent._self_cls()}-{self.name}", vars=[self.parent._self_var(),
                                                                           self.value._self_obj()]))
        return effects


class ObjectEq(BaseAction):
    def precondition(self):
        preconds = super().precondition()
        preconds.append(f'(= {self.parent._self_var()} {self.value._self_obj()})')
        return preconds


class ParamEq(BaseAction):
    def precondition(self):
        preconds = super().precondition()
        preconds.append(f'(= {self.parent._self_var()} {self.value._self_obj()})')
        return preconds
