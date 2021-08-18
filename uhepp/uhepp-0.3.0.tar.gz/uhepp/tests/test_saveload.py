
import unittest
from uhepp import UHeppHist, Stack, StackItem, RatioItem, VLine, HLine, \
                  Yield, from_jsons, Graph

class HistSaveLoadTestCase(unittest.TestCase):
    """Test that histogram properties are stored and reloaded"""

    def test_date(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        date = h.date 
        self.assertIsInstance(date, str)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.date, date)

    def test_filename(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.filename = "super_plot_m"

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.filename, "super_plot_m")

    def test_energy(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.energy = 13.43

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.energy, 13.43)

    def test_lumi(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.lumi = 138.9

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.lumi, 138.9)

    def test_author(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.author = "Frank Sauerburger"

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.author, "Frank Sauerburger")

    def test_producer(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.producer = "vim"

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.producer, "vim")

    def test_code_revision(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.code_revision = "c5b2547527f10af815b0414d7b43ad6c60a172fe"

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.code_revision,
                         "c5b2547527f10af815b0414d7b43ad6c60a172fe")

    def test_event_selection(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.event_selection = "some cuts"

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.event_selection, "some cuts")

    def test_tags(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.tags = {
            "region": "SR",
            "category": "VBF",
            "channel": "lephad",
        }

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.tags["region"], "SR")
        self.assertEqual(h.tags["category"], "VBF")
        self.assertEqual(h.tags["channel"], "lephad")

    def test_brand(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.brand = "not ATLAS"

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.brand, "not ATLAS")

    def test_brand_label(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.brand_label = "Work in progress"

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.brand_label, "Work in progress")

    def test_brand_subtext(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.subtext = "s = 3, l = 5"

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.subtext, "s = 3, l = 5")

    def test_symbol(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.symbol, "m")

    def test_variable(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.variable = "Mass"

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.variable, "Mass")

    def test_unit(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.unit = "MeV"

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.unit, "MeV")

    def test_x_log(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])

        for value in [True, False]:
            h.x_log = value

            json = h.to_jsons()
            h = from_jsons(json)

            self.assertEqual(h.x_log, value)

    def test_bin_edges(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.bin_edges, [-1, -0.5, 0, 0.5, 1])

    def test_rebin(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.rebin_edges = [-1, 0, 1]

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.rebin_edges, [-1, 0, 1])

    def test_include_underflow(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])

        for value in [True, False]:
            h.include_underflow = value

            json = h.to_jsons()
            h = from_jsons(json)

            self.assertEqual(h.include_underflow, value)

    def test_include_overflow(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])

        for value in [True, False]:
            h.include_overflow = value

            json = h.to_jsons()
            h = from_jsons(json)

            self.assertEqual(h.include_overflow, value)

    def test_stack_type(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        si = StackItem(["p0", "p3"], 'datadata')
        h.stacks.append(Stack([si], bartype='points'))

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.stacks[0].bartype, 'points')

    def test_stack_error(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        si = StackItem(["p0", "p3"], 'datadata')
        h.stacks.append(Stack([si], error='env'))

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.stacks[0].error, 'env')

    def test_stack_yield(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        si = StackItem(["p0", "p3"], 'datadata')
        h.stacks.append(Stack([si]))

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.stacks[0].content[0].yield_names, ["p0", "p3"])

    def test_stack_label(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        si = StackItem(["p0", "p3"], 'datadata')
        h.stacks.append(Stack([si]))

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.stacks[0].content[0].label, "datadata")

    def test_stack_style(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        si = StackItem(["p0", "p3"], 'datadata', color='r')
        h.stacks.append(Stack([si]))

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.stacks[0].content[0].style["color"], "#ff0000")

    def test_y_min(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.y_min = 1013

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.y_min, 1013)

    def test_y_max(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.y_max = 1013

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.y_max, 1013)

    def test_log(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        for value in [True, False]:
            h.y_log = value

            json = h.to_jsons()
            h = from_jsons(json)

            self.assertEqual(h.y_log, value)

    def test_y_label(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.y_label = "Ratio (a.u.)"

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.y_label, "Ratio (a.u.)")

    def test_v_lines_x(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        line = VLine(750)
        h.v_lines.append(line)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.v_lines[0].pos_x, 750)

    def test_v_lines_stretch(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        line = VLine(750)
        line.stretch = (0, 10)
        h.v_lines.append(line)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.v_lines[0].stretch, [0, 10])

    def test_v_lines_color(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        line = VLine(750)
        line.color = 'r'
        h.v_lines.append(line)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.v_lines[0].color, "#ff0000")

    def test_h_lines_x(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        line = HLine(300)
        h.h_lines.append(line)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.h_lines[0].pos_y, 300)

    def test_h_lines_stretch(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        line = HLine(300)
        line.stretch = (0, 10)
        h.h_lines.append(line)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.h_lines[0].stretch, [0, 10])

    def test_h_lines_color(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        line = HLine(300)
        line.color = 'r'
        h.h_lines.append(line)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.h_lines[0].color, "#ff0000")

    def test_ratio_type(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        ri = RatioItem(["p0"], ["p3"], bartype='points')
        h.ratio.append(ri)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.ratio[0].bartype, 'points')

    def test_ratio_error(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        ri = RatioItem(["p0"], ["p3"], error='env')
        h.ratio.append(ri)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.ratio[0].error, 'env')

    def test_ratio_den_error(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        ri = RatioItem(["p0"], ["p3"], den_error='env')
        h.ratio.append(ri)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.ratio[0].den_error, 'env')

    def test_ratio_numerator(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        ri = RatioItem(["p0"], ["p3"])
        h.ratio.append(ri)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.ratio[0].numerator, ['p0'])

    def test_ratio_denominator(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        ri = RatioItem(["p0"], ["p3"])
        h.ratio.append(ri)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.ratio[0].denominator, ['p3'])

    def test_ratio_style(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        ri = RatioItem(["p0"], ["p3"], color='b')
        h.ratio.append(ri)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.ratio[0].color, '#0000ff')

    def test_ratio_axis_min(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.ratio_min = 0.1

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.ratio_min, 0.1)

    def test_ratio_axis_max(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.ratio_max = 2.5

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.ratio_max, 2.5)

    def test_ratio_axis_log(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        for value in [True, False]:
            h.ratio_log = value

            json = h.to_jsons()
            h = from_jsons(json)

            self.assertEqual(h.ratio_log, value)

    def test_ratio_label(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.ratio_label = "X over Y"

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.ratio_label, "X over Y")

    def test_yield_base(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        y = Yield([1, 2, 3])
        h.yields["this"] = y

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(list(h.yields["this"]), [1, 2, 3]) 

    def test_yield_stat(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        y = Yield([1, 2, 3], [0.1, 0.2, 0.3])
        h.yields["this"] = y

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.yields["this"].stat, [0.1, 0.2, 0.3])

    def test_yield_syst(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        y = Yield([1, 2, 3], syst=[0.1, 0.2, 0.3])
        h.yields["this"] = y

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.yields["this"].syst, [0.1, 0.2, 0.3])

    def test_yield_var_up(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        y = Yield([1, 2, 3], var_up={'up': [0.1, 0.2, 0.3]})
        h.yields["this"] = y

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.yields["this"].var_up("up"), [0.1, 0.2, 0.3])

    def test_yield_var_down(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        y = Yield([1, 2, 3], var_down={'down': [0.1, 0.2, 0.3]})
        h.yields["this"] = y

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.yields["this"].var_down("down"), [0.1, 0.2, 0.3])

    def test_graph_x(self):
        h = UHeppHist("m", [0, 3])
        graph = Graph([0, 1, 2, 3], [0, 1, 4, 9])
        h.graphs.append(graph)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.graphs[0].x_values, [0, 1, 2, 3])

    def test_graph_y(self):
        h = UHeppHist("m", [0, 3])
        graph = Graph([0, 1, 2, 3], [0, 1, 4, 9])
        h.graphs.append(graph)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.graphs[0].y_values, [0, 1, 4, 9])

    def test_graph_x_errors(self):
        h = UHeppHist("m", [0, 3])
        graph = Graph([0, 1, 2, 3], [0, 1, 4, 9])
        graph.x_errors = [0.1, 0.1, 0.1, 0.2]
        h.graphs.append(graph)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.graphs[0].x_errors, [0.1, 0.1, 0.1, 0.2])

    def test_graph_y_errors(self):
        h = UHeppHist("m", [0, 3])
        graph = Graph([0, 1, 2, 3], [0, 1, 4, 9])
        graph.y_errors = [0.1, 0.1, 0.1, 0.2]
        h.graphs.append(graph)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.graphs[0].y_errors, [0.1, 0.1, 0.1, 0.2])

    def test_graph_label(self):
        h = UHeppHist("m", [0, 3])
        graph = Graph([0, 1, 2, 3], [0, 1, 4, 9])
        graph.label = "Hello"
        h.graphs.append(graph)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.graphs[0].label, "Hello")

    def test_graph_type(self):
        h = UHeppHist("m", [0, 3])
        graph = Graph([0, 1, 2, 3], [0, 1, 4, 9])
        graph.graphtype = "line"
        h.graphs.append(graph)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.graphs[0].graphtype, "line")

    def test_graph_style(self):
        h = UHeppHist("m", [0, 3])
        graph = Graph([0, 1, 2, 3], [0, 1, 4, 9])
        graph.color = 'r'
        h.graphs.append(graph)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.graphs[0].color, "#ff0000")

    def test_unit_in_brackets_True(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.unit_in_brackets = True

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.unit_in_brackets, True)

    def test_unit_in_brackets_False(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        h.unit_in_brackets = False

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.unit_in_brackets, False)

    def test_x_errorbar_stack_True(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        si = StackItem(["p0", "p3"], 'datadata')
        h.stacks.append(Stack([si], x_errorbar=True))

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.stacks[0].x_errorbar, True)

    def test_x_errorbar_stack_False(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        si = StackItem(["p0", "p3"], 'datadata')
        h.stacks.append(Stack([si], x_errorbar=False))

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.stacks[0].x_errorbar, False)

    def test_x_errorbar_ratio_True(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        ri = RatioItem(["p0"], ["p3"], x_errorbar=True)
        h.ratio.append(ri)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.ratio[0].x_errorbar, True)

    def test_x_errorbar_ratio_False(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        ri = RatioItem(["p0"], ["p3"], x_errorbar=False)
        h.ratio.append(ri)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.ratio[0].x_errorbar, False)

    def test_keep_zero_stack_True(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        si = StackItem(["p0", "p3"], 'datadata')
        h.stacks.append(Stack([si], keep_zero=True))

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.stacks[0].keep_zero, True)

    def test_keep_zero_stack_False(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        si = StackItem(["p0", "p3"], 'datadata')
        h.stacks.append(Stack([si], keep_zero=False))

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.stacks[0].keep_zero, False)

    def test_keep_zero_ratio_True(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        ri = RatioItem(["p0"], ["p3"], keep_zero=True)
        h.ratio.append(ri)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.ratio[0].keep_zero, True)

    def test_keep_zero_ratio_False(self):
        h = UHeppHist("m", [-1, -0.5, 0, 0.5, 1])
        ri = RatioItem(["p0"], ["p3"], keep_zero=False)
        h.ratio.append(ri)

        json = h.to_jsons()
        h = from_jsons(json)

        self.assertEqual(h.ratio[0].keep_zero, False)
