import unittest

import numpy as np
from numpy.testing import assert_array_almost_equal

import feyn
import _feyn

class TestRegister(unittest.TestCase):

    def test_linear_input_initializes_scalar(self):
        register = _feyn.Interaction('in:linear(f)->i', latticeloc=(0,0,-1), name='myinput')

        out = _feyn.Interaction("out:fixed(i)->f#", latticeloc=(1,0,-1), name="out")
        out._set_source(0,0)

        g = feyn.Model(2)
        g[0] = register
        g[1] = out
        o = g.predict({"myinput": np.array([-4,0])})

        # Initialized the right parameters
        self.assertEqual(register.state.scale, .5)

        # Correctly scaled the input (the output doen't scale)
        assert_array_almost_equal(o, [
            -4*register.state.scale*register.state.w+register.state.bias,
            0*register.state.scale*register.state.w+register.state.bias
            ])


    def test_fixed_input_initializes_scalar(self):
        register = _feyn.Interaction('in:fixed(f#)->i', latticeloc=(0,0,-1), name='myinput')

        out = _feyn.Interaction("out:fixed(i)->f#", latticeloc=(1,0,-1), name="out")
        out._set_source(0,0)

        g = feyn.Model(2)
        g[0] = register
        g[1] = out
        o = g.predict({"myinput": np.array([-4,0])})

        # Initialized the right parameters
        self.assertEqual(register.state.scale, 1)

        # Correctly scaled the input (the output doen't scale)
        assert_array_almost_equal(o, [-4*register.state.w+register.state.bias, register.state.bias])


    def test_register_supports_loss_functions(self):
        register = _feyn.Interaction('out:linear(i)->f', latticeloc=(0,0,-1), name='myinput')
        with self.subTest("valid loss function"):
            register._loss = "absolute_error"

        with self.assertRaises(ValueError):
            register._loss = "uncomfortable_fact"
