import unittest

from moped import Compound, Model, Reaction


class CobraInterfaceTests(unittest.TestCase):
    def create_minimal_toy_model(self):
        compounds = (
            Compound(base_id="S", compartment="CYTOSOL", formula={"C": 1}, charge=0),
            Compound(base_id="E", compartment="CYTOSOL", formula={"E": 1}, charge=0),
            Compound(base_id="SE", compartment="CYTOSOL", formula={"C": 1, "E": 1}, charge=0),
            Compound(base_id="P", compartment="CYTOSOL", formula={"C": 1}, charge=0),
        )
        reactions = (
            Reaction(
                id="v1_c",
                base_id="v1",
                stoichiometries={"S_c": -1, "E_c": -1, "SE_c": 1},
                bounds=(-10, 1000),
                sequences={"MONOMER-001": {"GATC"}},
            ),
            Reaction(
                id="v2_c",
                base_id="v2",
                stoichiometries={"SE_c": -1, "P_c": 1, "E_c": 1},
                bounds=(0, 1000),
                sequences={"MONOMER-002": {"GATC"}},
            ),
        )
        compartments = {"CYTOSOL": "c", "PERIPLASM": "p", "EXTRACELLULAR": "e"}
        m = Model(compounds=compounds, reactions=reactions, compartments=compartments)
        m.add_transport_reaction(compound_id="S_c", compartment_id="EXTRACELLULAR", bounds=(-1000, 0))
        m.add_influx("S_c", extracellular_compartment_id="EXTRACELLULAR")
        m.add_transport_reaction(compound_id="P_c", compartment_id="EXTRACELLULAR", bounds=(0, 1000))
        m.add_efflux("P_c", extracellular_compartment_id="EXTRACELLULAR")
        m.set_objective({"v1_c": 1, "v2_c": 1})
        return m.copy()

    def test_to_cobra(self):
        m = self.create_minimal_toy_model()
        cm = m.to_cobra()
        self.assertEqual(list(m.compounds), [i.id for i in cm.metabolites])
        self.assertEqual(list(m.reactions), [i.id for i in cm.reactions])
        self.assertEqual(
            m.objective,
            {rec.id: rec.objective_coefficient for rec in cm.reactions if rec.objective_coefficient != 0},
        )

    def test_cobra_metabolite_compartment(self):
        m = self.create_minimal_toy_model()
        cm = m.to_cobra()
        for metabolite in cm.metabolites:
            self.assertEqual(
                m.compartments[m.compounds[metabolite.id].compartment],
                metabolite.compartment,
            )

    def test_cobra_metabolite_in_reaction(self):
        m = self.create_minimal_toy_model()
        cm = m.to_cobra()
        for metabolite in cm.metabolites:
            self.assertEqual(
                sorted(m.compounds[metabolite.id].in_reaction),
                sorted([i.id for i in metabolite.reactions]),
            )

    def test_cobra_metabolite_charge(self):
        m = self.create_minimal_toy_model()
        cm = m.to_cobra()
        for metabolite in cm.metabolites:
            self.assertEqual(m.compounds[metabolite.id].charge, metabolite.charge)

    def test_cobra_metabolite_formula(self):
        m = self.create_minimal_toy_model()
        cm = m.to_cobra()
        for metabolite in cm.metabolites:
            self.assertEqual(
                "".join([k + str(v) for k, v in m.compounds[metabolite.id].formula.items()]),
                metabolite.formula,
            )

    def test_cobra_reaction_stoichiometries(self):
        m = self.create_minimal_toy_model()
        cm = m.to_cobra()
        for reaction in cm.reactions:
            self.assertEqual(
                m.reactions[reaction.id].stoichiometries,
                {k.id: v for k, v in reaction.metabolites.items()},
            )

    def test_cobra_reaction_bounds(self):
        m = self.create_minimal_toy_model()
        cm = m.to_cobra()
        for reaction in cm.reactions:
            self.assertEqual(
                m.reactions[reaction.id].bounds,
                reaction.bounds,
            )

    def test_cobra_reaction_reversibility(self):
        m = self.create_minimal_toy_model()
        cm = m.to_cobra()
        for reaction in cm.reactions:
            self.assertEqual(
                m.reactions[reaction.id].reversible,
                reaction.reversibility,
            )

    def test_back_and_forth(self):
        model = self.create_minimal_toy_model()
        cobra_model = model.to_cobra()
        model_re = Model()
        model_re.read_from_cobra(cobra_model)
        self.assertEqual(model.compounds, model_re.compounds)
        for compound_id in model.compounds:
            compound = model.compounds[compound_id]
            compound_re = model_re.compounds[compound_id]

            self.assertEqual(compound.base_id, compound_re.base_id)
            self.assertEqual(compound.id, compound_re.id)
            self.assertEqual(compound.compartment, compound_re.compartment)
            self.assertEqual(compound.formula, compound_re.formula)
            self.assertEqual(compound.in_reaction, compound_re.in_reaction)

        self.assertEqual(model.reactions, model_re.reactions)
        for reaction_id in model.reactions:
            reaction = model.reactions[reaction_id]
            reaction_re = model_re.reactions[reaction_id]

            self.assertEqual(reaction.id, reaction_re.id)
            self.assertEqual(reaction.base_id, reaction_re.base_id)
            self.assertEqual(reaction.stoichiometries, reaction_re.stoichiometries)
            self.assertEqual(reaction.bounds, reaction_re.bounds)
            # self.assertEqual(reaction.sequences, reaction_re.sequences)

    def test_get_producing_reactions(self):
        model = self.create_minimal_toy_model()
        cobra_model = model.to_cobra()
        cobra_solution = cobra_model.optimize()
        self.assertEqual(
            model.get_producing_reactions(cobra_solution=cobra_solution, compound_id="S_c"),
            {"TR_S_c_e": 1000.0},
        )
        self.assertEqual(
            model.get_producing_reactions(cobra_solution=cobra_solution, compound_id="E_c"),
            {"v2_c": 1000.0},
        )
        self.assertEqual(
            model.get_producing_reactions(cobra_solution=cobra_solution, compound_id="SE_c"),
            {"v1_c": 1000.0},
        )
        self.assertEqual(
            model.get_producing_reactions(cobra_solution=cobra_solution, compound_id="P_c"),
            {"v2_c": 1000.0},
        )
        self.assertEqual(
            model.get_producing_reactions(cobra_solution=cobra_solution, compound_id="S_e"),
            {"EX_S_e": 1000.0},
        )
        self.assertEqual(
            model.get_producing_reactions(cobra_solution=cobra_solution, compound_id="P_e"),
            {"TR_P_c_e": 1000.0},
        )

    def test_get_consuming_reactions(self):
        model = self.create_minimal_toy_model()
        cobra_model = model.to_cobra()
        cobra_solution = cobra_model.optimize()
        self.assertEqual(
            model.get_consuming_reactions(cobra_solution=cobra_solution, compound_id="S_c"),
            {"v1_c": 1000.0},
        )
        self.assertEqual(
            model.get_consuming_reactions(cobra_solution=cobra_solution, compound_id="E_c"),
            {"v1_c": 1000.0},
        )
        self.assertEqual(
            model.get_consuming_reactions(cobra_solution=cobra_solution, compound_id="SE_c"),
            {"v2_c": 1000.0},
        )
        self.assertEqual(
            model.get_consuming_reactions(cobra_solution=cobra_solution, compound_id="P_c"),
            {"TR_P_c_e": 1000.0},
        )
        self.assertEqual(
            model.get_consuming_reactions(cobra_solution=cobra_solution, compound_id="S_e"),
            {"TR_S_c_e": 1000.0},
        )
        self.assertEqual(
            model.get_consuming_reactions(cobra_solution=cobra_solution, compound_id="P_e"),
            {"EX_P_e": 1000.0},
        )

    def test_get_influx_reactions(self):
        m = self.create_minimal_toy_model()
        cobra_model = m.to_cobra()
        cobra_solution = cobra_model.optimize()

        res = m.get_influx_reactions(cobra_solution=cobra_solution, sort_result=False)
        self.assertEqual(res["EX_P_e"], 1000.0)
        self.assertEqual(list(res.keys()), ["EX_P_e"])

        res = m.get_influx_reactions(cobra_solution=cobra_solution, sort_result=True)
        self.assertEqual(res["EX_P_e"], 1000.0)
        self.assertEqual(list(res.keys()), ["EX_P_e"])

    def test_get_efflux_reactions(self):
        m = self.create_minimal_toy_model()
        cobra_model = m.to_cobra()
        cobra_solution = cobra_model.optimize()
        res = m.get_efflux_reactions(cobra_solution=cobra_solution, sort_result=False)
        self.assertEqual(res["EX_S_e"], -1000.0)
        self.assertEqual(list(res.keys()), ["EX_S_e"])

        res = m.get_efflux_reactions(cobra_solution=cobra_solution, sort_result=True)
        self.assertEqual(res["EX_S_e"], -1000.0)
        self.assertEqual(list(res.keys()), ["EX_S_e"])
