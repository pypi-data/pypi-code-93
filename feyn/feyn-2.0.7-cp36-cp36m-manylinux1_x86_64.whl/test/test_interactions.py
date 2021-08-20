from sys import intern
import unittest
import numpy as np

import _feyn
import feyn

# This is a test to implement all interaction state logic.
# It is not meant to test, at least for now, the logic of the interations.
class TestInteractions(unittest.TestCase):

    def test_invalid_interaction_fails(self):
        with self.assertRaises(ValueError):
            _feyn.Interaction('non-existing', latticeloc=(0,0,0) )


    def test_add_assign_to_state_is_not_allowed(self):
        with self.assertRaises(AttributeError):
            fail = _feyn.Interaction('cell:add(i,i)->i', latticeloc=(0,0,0))
            fail.state = {}


    def test_lin_state_update(self):
        interaction = _feyn.Interaction('cell:linear(i)->i', latticeloc=(0,0,0))

        d = {"w0": 1, "bias": 3}
        interaction.state._from_dict(d)

        self.assertAlmostEqual(interaction.state.w0, d["w0"])
        self.assertAlmostEqual(interaction.state.bias, d["bias"])


    def xtest_gaussian_interaction_state(self):
        gaussian_interaction = _feyn.Interaction('cell:gaussian(i,i)->i', latticeloc=(0,0,0))
        state = {
            'center0': 0,
            'center1': 1.0,
            'w0': 0.2,
            'w1': 0.3
        }
        gaussian_interaction.state._from_dict(state)

        self.assertAlmostEqual(gaussian_interaction.state.center0, state['center0'])
        self.assertAlmostEqual(gaussian_interaction.state.center1, state['center1'])
        self.assertAlmostEqual(gaussian_interaction.state.w0, state['w0'])
        self.assertAlmostEqual(gaussian_interaction.state.w1, state['w1'])


    def test_handle_interaction_without_properties(self):
        multiply_interaction = _feyn.Interaction('cell:multiply(i,i)->i', latticeloc=(0,0,0))

        with self.assertRaises(AttributeError):
            multiply_interaction.state.random_prop = "cheese"

        # from_dict ok
        try:
            multiply_interaction.state._from_dict({})
            multiply_interaction.state._from_dict({'random_prop': 0})

            self.assertEqual(multiply_interaction.state._to_dict(), {})
        except:
            self.fail("_from_dict should be allowed")

    def xtest_handle_interaction_with_properties(self):
        gaussian_interaction = _feyn.Interaction('cell:gaussian(i)->i', latticeloc=(0,0,0))

        with self.subTest("Set valid property"):
            gaussian_interaction.state.w0 = 2.3
            self.assertAlmostEqual(gaussian_interaction.state.w0, 2.3)

        with self.assertRaises(AttributeError):
            gaussian_interaction.state.random_prop = "cheese"

        # from_dict ok
        try:
            gaussian_interaction.state._from_dict({})
            gaussian_interaction.state._from_dict({'random_prop': 0})
        except:
            self.fail("_from_dict should be allowed")

    def test_category_register_interaction_state(self):
        register_cat_interaction = _feyn.Interaction('in:cat(c)->i', latticeloc=(0,0,0))
        state = {
            'categories': [
                ('red', 0.1),
                ('blue', 0.15),
                ('none', 0.001)
            ]
        }

        register_cat_interaction.state._from_dict(state)

        self.assertListEqual(sorted(state['categories']), sorted(register_cat_interaction.state.categories))


    def test_category_register_interaction_update(self):
        register_cat = _feyn.Interaction('in:cat(c)->i', name='myinput', latticeloc=(0,0,-1))
        register_cat.state.categories = [
            ('red', 0.1),
            ('blue', 0.15),
        ]
        register_cat.state.bias = 0

        out = _feyn.Interaction("out:linear(i)->f", name="out", latticeloc=(1,0,-1))
        out._set_source(0,0)
        out.state.w = 1

        g = feyn.Model(2)
        g[0] = register_cat
        g[1] = out
        o = g.predict({"myinput": np.array(["red", "blue", "purple", 42], dtype=object)})

        newstate = {i[0]: i[1] for i in register_cat.state.categories}

        self.assertAlmostEqual(o[0],0.1)
        self.assertAlmostEqual(o[1],0.15)
        self.assertAlmostEqual(o[2],newstate["purple"])
        self.assertAlmostEqual(o[3],newstate[42])


    def test_interaction_depth(self):
        reg = _feyn.Interaction("in:linear(f)->i", latticeloc=(0,0,-1))
        tanh = _feyn.Interaction("cell:tanh(i)->i", latticeloc=(0,0,0))

        with self.assertRaises(RuntimeError):
            # Depth doesn't work outside of graphs
            reg.depth

        with self.subTest("Depth works in graphs"):
            g = _feyn.Model(2)
            g[0]=reg
            g[1]=tanh
            tanh._set_source(0,reg._index)

            self.assertEqual(reg.depth, -1)
            self.assertEqual(tanh.depth, 0)

        with self.assertRaises(RuntimeError):
            # Depth doesnt work if the interaction has been implicitly removed
            g = _feyn.Model(2)
            g[0]=reg
            g[1]=tanh

            del(g)
            reg.depth
