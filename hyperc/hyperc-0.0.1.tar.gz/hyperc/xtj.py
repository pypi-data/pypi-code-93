from distutils.version import StrictVersion
import re
import os
import sys
import string
import json
import formulas
import formulas.tokens
import formulas.errors
from collections import defaultdict
import formulas.tokens.operand
import dill
import hyperc
import hyperc as hc
import random
import itertools
import types
import logging
import unidecode
import hyperc.settings
progress = logging.getLogger("hyperc_progress")
import hyperc.util
import copy
import collections
RE_ACTION_NAME = re.compile("\[(.+)\]")

XTJ_VERSION = "1.4"

def gen_random_string(N=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

class TableElementMeta(type):
    @hyperc.util.side_effect_decorator
    def __str__(self):
        return self.__table_name__


def str_to_py(sheet_name: str):
    trans_name = unidecode.unidecode(sheet_name).replace(' ', '_').upper()
    trans_name = list(trans_name)
    for i, character in enumerate(trans_name):
        if character not in (string.ascii_uppercase + string.digits + "_"):
            trans_name[i] = "_"
    return f"{''.join(trans_name)}".strip('_')

def sheet_to_py(sheet_name: str):
    return f"tbl_{str_to_py(sheet_name)}"


def _my_build_id(ref, sheet='', excel=''):
    # print("MBI MY BUILD ID")
    if excel:
        sheet = "[%s]%s" % (excel, sheet.replace("''", "'"))
        # print("MBI SHEET", sheet, excel)
        if not formulas.tokens.operand._re_build_id.match(excel):
            sheet = "'%s'" % sheet
            # print("MBI NEW SHEET", sheet)

    # complete_ref = '!'.join(s for s in (("'"+sheet+"'").replace("''","'"), ref) if s)
    complete_ref = '!'.join(s for s in ("'"+sheet+"'", ref) if s)
    complete_ref = re.sub(r"^''\[", "'[", complete_ref)
    if not complete_ref.startswith("''"):
        complete_ref = re.sub(r"''!", "'!", complete_ref)
    # print("MBI Will return", complete_ref)
    return complete_ref

formulas.tokens.operand._build_id = _my_build_id

def get_char_from_index(idx):
    if idx >= len(string.ascii_lowercase):
        raise ValueError(f"Unsupport index {idx} out of length \"{string.ascii_lowercase}\" ")
    return string.ascii_lowercase[idx]

def get_index_from_char(ch):
    char = ch.lower()
    if len(char) > 1:
        raise ValueError(f"Unsupport index {char} out of \"{string.ascii_lowercase}\" ")
    return string.ascii_lowercase.index(char)

def full_tokenize(v):
    try:
        ret = formulas.Parser().ast("="+list(formulas.Parser().ast(v)[1].compile().dsp.nodes.keys())[0].replace(" = -","=-"))[0]
    except formulas.errors.FormulaError as e:
        # print(f"Can't parse {v}: {e}")
        raise e
    return ret

class ColumnTypeInferenceError(Exception):
    pass

def detect_filter_mode(table):
    flts = table["filter"].strip().split(" #")[0].strip().replace("\\#", "#")
    flts = flts.strip().split(" //")[0].strip().replace("\\/", "/")
    if flts.startswith("#") or flts.startswith("//"):
        raise AssertionError("Can't detect mode of null filter")
    if not flts:
        raise AssertionError("Can't detect mode of null filter")
    if not flts.startswith("="):
        flts="="+flts
    ft = full_tokenize(flts)
    modes = set()
    for token in ft:
        if not isinstance(token, formulas.tokens.operand.Range): continue
        if ":" in token.attr.get("ref", "") and token.attr.get("sheet", "") == "" and token.attr.get("excel", "") == "" :
            modes.add("filter")
        elif (":" in token.attr.get("ref", "") and 
                token.attr.get("sheet", "") == table["table_name"].upper() and 
                token.attr.get("excel", "") == ""):
            modes.add("filter")
        elif (":" in token.attr.get("ref", "") and 
                f"[{token.attr.get('excel', '')}]{token.attr.get('sheet', '')}" == table["view_name"].upper()):
            modes.add("filter")
        elif ":" not in token.attr.get("ref", "") and token.attr.get("sheet", "") == "" and token.attr.get("excel", "") == "" :
            modes.add("view")
        elif ":" not in token.attr.get("ref", "") and token.attr.get("sheet", "") == table["table_name"].upper() and token.attr.get("excel", "") == "" :
            modes.add("view")
        elif ":" not in token.attr.get("ref", "") and token.attr.get("sheet", "") == table["table_name"].upper() and \
                f"[{token.attr.get('excel', '')}]{token.attr.get('sheet', '')}" == table["view_name"].upper():
            modes.add("view")
    if not modes: 
        return "view"
    assert len(modes) < 2, f"Mixed row and cell filter is not supported yet - {table['view_name']}"
    return list(modes)[0]


def detect_header(records, table_name, jsdata):
    # if we insert into first row there isn't a header
    
    rownum = 0
    if len(records) == 0: return False
    for rec in records:
        for col, val in rec.items():
            if len(col) > 1: continue
            if type(val) == int:  # Fix for imported values that are integers...
                val = str(val)
            if val.lower() == "true" or val.lower() == "false":
                if rownum == 0:
                    return False
                else:
                    return True
            try:
                int(val)
                if rownum == 0:
                    return False
                else:
                    return True
            except:
                pass
        rownum += 1
        if rownum > 1:
            break
    # TODO: here we don't know. If we're adding to table -> we have a header
    for act_id, act in jsdata["actionData"].items():
        collected_tables = []
        collect_tables(act, collected_tables)
        for step in collected_tables:
            if step["table_name"] != table_name: continue
            if "mode" in step and (step["mode"] == "select_row" or 
                                   step["mode"] == "add_row") :
                return True
    return False

def create_data(jsdata, module):
    objects = {}
    classes = {}
    name_map = {}

    new_mod = module
    session_name = new_mod.__name__

    progress.info("Generating data heap from worksheet")

    table_meta = {}
 
    used_tables = set()

    # filter unused tables
    for action_attr in jsdata['actionData'].values():
        collected_tables = []
        collect_tables(action_attr, collected_tables)
        for table in collected_tables:
            used_tables.add(sheet_to_py(table["table_name"]))

    for table in jsdata["tableInputData"][jsdata["selectedInput"]]["sheets"]:
        #filter unused tables
        if sheet_to_py(table["name"]) not in used_tables:
            continue
        # generate class
        has_header = detect_header(table["records"], table["name"], jsdata)
        if hyperc.settings.DEBUG:
            print("HAS HEADER", table["name"], has_header)
        if has_header:
            start_row = 1
        else:
            start_row = 0
        table_meta[table["name"]] = {"type": "strict", "start_row": start_row}

        py_table_name = sheet_to_py(table["name"])
        # headers[py_table_name] = has_header
        name_map[py_table_name] = table["name"]

        ThisTable = TableElementMeta(py_table_name, (object,), {'__table_name__': table["name"]})
        ThisTable.__annotations__={}
        ThisTable.__annotations__['__table_name__'] = str
        ThisTable.__touched_annotations__ = set()
        ThisTable.__annotations_type_set__ = defaultdict(set)
        new_mod.__dict__[py_table_name] = ThisTable
        classes[py_table_name] = ThisTable
        classes[py_table_name].__qualname__ = f"{session_name}.{py_table_name}"

        table_objects = []

        for rec in table["records"]:
            if has_header and rec["recid"] == 1 :
                continue
            if hyperc.settings.DEBUG:
                print("Doing with", py_table_name, rec)
            rec_obj = ThisTable()
            rec_obj.__row_record__ = copy.copy(rec)
            rec_obj.__recid__ = rec_obj.__row_record__['recid']
            rec_obj.__table_name__ += f'!_{str(rec_obj.__recid__)} {",".join(map(str, rec.values()))}'
            rec_obj.__touched_annotations__ = set()
            ThisTable.__annotations_type_set__ = defaultdict(set)
            rec_obj.__row_record__.pop('w2ui', None)
            table_objects.append(rec_obj)

        objects[py_table_name] = table_objects
    return objects, classes, name_map, table_meta


def try_type(s):
    if s.startswith('"'):
        return str
    try:
        int(s)
        return int
    except:
        pass
    if s.lower() in {"true", "false"}:
        return bool
    return None

class NoRowDefined(KeyError):
    pass

class XTJViewVar():
    def __init__(
            self, var=None, selector=None, view_name=None, table_py_name=None, view_var=None, letter=None,
            table_name=None, parent_object=None, var_map=None, table_var=None, var_context=None, coords=""):
        self.selector = selector
        self.view_name = view_name
        self.table_py_name = table_py_name
        self.view_var = view_var
        self.var = var
        self.table_var = table_var
        self.letter = letter
        self.coords = coords
        self.str_ret = var
        self.table_name = table_name
        self.parent_object = parent_object
        self.touch_num = 0
        self.type_group_set = set()
        if var_map is None:
            self.type_group = None
        else:
            self.new_type_group(var_map)
        self.anchor_in_code = None
        self.var_context = None

    def set_anchor_in_code(self, anchor):
        self.anchor_in_code = anchor

    def new_type_group(self, var_map):
        # random duplicateless Generator
        loop = True
        rnd_len = 1
        while loop:
            loop = False
            type_group = 'type_group_'+''.join(random.choices(string.ascii_uppercase + string.digits, k=rnd_len))
            for k in var_map:
                if var_map[k].type_group == type_group:
                    loop = True
            if not loop:
                self.type_group = type_group
                self.type_group_set.add(type_group)
            rnd_len += 1

    def set_types(self, type):
        self.touch()
        if isinstance(type, set):
            self.parent_object.__annotations_type_set__[self.coords].update(type)
        else:
            self.parent_object.__annotations_type_set__[self.coords].add(type)

    def touch(self):
        self.touch_num += 1

    def isTouched(self):
        if self.touch_num > 0:
            return True
        else:
            return False

    def get_types(self):
        return self.parent_object.__annotations_type_set__[self.coords]


    def __str__(self):
        return self.str_ret

class TypeMapper:

    def __init__(self, table, coords, group, name, types):
        self.table = table
        self.coords = coords
        self.group = group
        self.name = name
        self.visited_group = set()
        self.forward_visited_group = set()
        self.types = types

    def merge_group(self, type_mapper):
        self.group.update(type_mapper.group)
        self.types.update(type_mapper.types)
        type_mapper.group.update(self.group)
        type_mapper.types.update(self.types)

class XL2Py:
    def __init__(self, action, temp, param, view_resolution, classes_dict, view_tables_ref, tables_added_rows,
                 HCT_OBJECTS, HCT_STATIC_OBJECTS, table_meta, is_goal=False, global_view_var_mapper={}, global_table_type_mapper={}):
        self.view_resolution = view_resolution
        self.variable_resolution_map = {}
        self.variable_resolution_map_reverced = {}
        self.variable_resolution_map_obj = global_view_var_mapper
        self.table_type_mapper = global_table_type_mapper
        self.view_tables_ref = view_tables_ref
        self.tables_added_rows = tables_added_rows
        self.HCT_OBJECTS = HCT_OBJECTS
        self.HCT_STATIC_OBJECTS = HCT_STATIC_OBJECTS
        self.is_goal = is_goal

        self.temp_tables = temp
        self.param_tables = param
        self.vars_used = {}
        self.vars_names = []
        self.vars_names_obj = []
        self.vars_types = {}
        self.vars_indexes = {}
        self.classes_dict = classes_dict
        self.view_resolution_ref = {}
        for i, t, view_table in zip(range(len(self.param_tables)), self.param_tables, self.view_resolution):
            self.vars_names.append(f"var_{sheet_to_py(t)}_{i}")
            self.vars_names_obj.append(XTJViewVar(var = f"var_{sheet_to_py(t)}_{i}", table_py_name = sheet_to_py(t), table_name = t))
            self.vars_types[f"var_{sheet_to_py(t)}_{i}"] = self.classes_dict[f"{sheet_to_py(t)}"]
            self.view_resolution_ref[view_table.upper()] = XTJViewVar(
                var=f"var_{sheet_to_py(t)}_{i}", table_py_name=sheet_to_py(t),view_name=view_table, table_name=t)
        
        self.paren_level = 0
        self.functions = []
        self.last_node = None
        self.function_parens = {}
        self.function_parens_args = defaultdict(list)
        self.code = []
        self.cur_var = "var_tbl_TEST"
        self.cur_tbl = ""
        self.sub_step_name = "" # may be the same as self.cur_tbl for main view
        self.cur_add_tbl = []
        self.action = action
        self.remember_types = {}
        self.cur_mode = "filter"  # Means we ignore row index in variables
        self.s_formula = ""
        self.direct_refs = defaultdict(set)
    
    def add_column(self, viewname_u, letter):
        # We use upper dict key because it return excel formulas parser
        xtj_view_var = self.view_resolution_ref[viewname_u]
        self.classes_dict[sheet_to_py(xtj_view_var.table_name)].__touched_annotations__.add(letter.lower())
        print('PREPPING FOR VAR', xtj_view_var.view_name, self.view_resolution, self.vars_names_obj)
        temp_view_var = f"var_{sheet_to_py(xtj_view_var.view_name)}_{letter}"
        param_var = f"{xtj_view_var}.{letter}"
        self.variable_resolution_map_obj[temp_view_var] = XTJViewVar(
            view_name=xtj_view_var.view_name, table_var=str(xtj_view_var),
            var=param_var, letter=letter, coords=letter, table_name=xtj_view_var.table_name,
            parent_object=self.classes_dict[xtj_view_var.table_py_name],
            var_map=self.variable_resolution_map_obj, var_context="changes_row")
        self.variable_resolution_map[temp_view_var] = param_var
        self.variable_resolution_map_reverced[param_var] = temp_view_var

    def get_row_by_recid(self, recid, tbl_name=None, sht_tbl_name=None):
        if sht_tbl_name is None:
            sht_tbl_name = sheet_to_py(tbl_name)
        
        try:
            row = self.HCT_OBJECTS[sht_tbl_name][recid-1] #optimisation, recid usual more then index +1
            if row.__recid__ == recid:
                return row
        except:
            pass
        for r in self.HCT_OBJECTS[sht_tbl_name]:
            print("Checking row:",sht_tbl_name , r)
            if r.__recid__ == recid:
                return r
        if int(recid) == 1:
            raise AssertionError("HyperC does not support referencing table headers yet")  # HyperC does not support referencing table headers yet.
        raise NoRowDefined(f"Row {recid} not found in {tbl_name}")
        

    def add_cell(self, viewname_u, cell_num, cell_letter):
        cell_num = int(cell_num)
        xtj_view_var = self.view_tables_ref[viewname_u] # We use upper dict key because it return excel formulas parser :(
        sht_view_name = sheet_to_py(xtj_view_var.view_name)
        sht_tbl_name = sheet_to_py(xtj_view_var.table_name)
        ob = self.get_row_by_recid(recid=cell_num, tbl_name=xtj_view_var.table_name)
        ob.__touched_annotations__.add(cell_letter.lower())
        letter = f"{cell_letter.lower()}"
        var_name = f"var_{sht_view_name}__hct_direct_ref__{cell_num}_{letter}"
        var_in_code = f"HCT_STATIC_OBJECTS.{sht_tbl_name}_{cell_num}.{letter}"
        self.variable_resolution_map[var_name] = var_in_code
        self.variable_resolution_map_reverced[var_in_code] = var_name
        xtj_view_var = XTJViewVar(
            var=var_in_code, view_name=xtj_view_var.view_name, letter=letter, table_name=xtj_view_var.table_name,
            parent_object=ob, var_map=self.variable_resolution_map_obj, coords=f"{cell_letter.lower()}{cell_num}",  var_context="direct_ref")
        self.variable_resolution_map_obj[var_name] = xtj_view_var
        self.vars_types[var_name] = self.classes_dict[sht_tbl_name]
        self.vars_indexes[var_name] = (cell_num, f"{sht_tbl_name}_{cell_num}")
        # Add selector anchor for views
        if xtj_view_var.anchor_in_code is None:
            if self.view_resolution_ref.get(viewname_u):
                if self.view_resolution_ref[viewname_u].anchor_in_code is not None:
                    select_anchor = self.view_resolution_ref[viewname_u].anchor_in_code
                    xtj_view_var.set_anchor_in_code(select_anchor)
        return xtj_view_var

    def check_resolve_types(self, v1, v2, operator=None):

        type1 = set()
        type2 = set()


        if v1 in self.remember_types:
            type1.add(self.remember_types[v1])
        else:
            if try_type(v1) in {str, int, bool}:
                type1.add(try_type(v1))

        if v2 in self.remember_types:
            type2.add(self.remember_types[v2])
        else:
            if try_type(v2) in {str, int, bool}:
                type1.add(try_type(v2))

        view_var1 = None
        view_var2 = None

        # extract type from coresponding cell or column
        if self.variable_resolution_map_obj is not None:
            if v1 in self.variable_resolution_map:
                view_var1 = self.variable_resolution_map_obj[v1]
            if v1 in self.variable_resolution_map_reverced:
                view_var1 = self.variable_resolution_map_obj[self.variable_resolution_map_reverced[v1]]
            if v2 in self.variable_resolution_map:
                view_var2 = self.variable_resolution_map_obj[v2]
            if v2 in self.variable_resolution_map_reverced:
                view_var2 = self.variable_resolution_map_obj[self.variable_resolution_map_reverced[v2]]

        if operator in ['=', '==']:
            if view_var1 is not None:
                view_var1.set_types(type1)
                view_var1.set_types(type2)
                if view_var2 is not None:
                    view_var1.set_types(view_var2.get_types())
            if view_var2 is not None:
                view_var2.set_types(type1)
                view_var2.set_types(type2)
                if view_var1 is not None:
                    view_var2.set_types(view_var1.get_types())

        if operator in ['-', '+', '/', '*', '>', '<', '<=', '>=']:
            if view_var1 is not None:
                view_var1.set_types(int)
            if view_var2 is not None:
                view_var2.set_types(int)

        # set neighbour
        if view_var1 is not None and view_var2 is not None:
            view_var2.type_group_set.update(view_var1.type_group_set)
            view_var1.type_group_set.update(view_var2.type_group_set)
        if view_var1 is not None:
            if view_var1.type_group not in self.table_type_mapper:
                self.table_type_mapper[view_var1.type_group] = TypeMapper(
                    table=view_var1.parent_object, coords=view_var1.coords, group=view_var1.type_group_set, name=view_var1.type_group, types=view_var1.get_types())
        if view_var2 is not None:
            if view_var2.type_group not in self.table_type_mapper:
                self.table_type_mapper[view_var2.type_group] = TypeMapper(
                    table=view_var2.parent_object, coords=view_var2.coords, group=view_var2.type_group_set, name=view_var2.type_group, types=view_var2.get_types())
        return 


    def save_return(self, ret, type_):
        self.remember_types[ret] = type_
        return ret

    def render_code(self):
        code = ""
        for l in self.code:
            if len(l) > 0:
                if isinstance(l[0], list):
                    for ll in l:
                        code += '    '+' '.join(ll)+"\n"
                else:
                    code += '    '+' '.join(l)+"\n"
        # Now take all direct ref variables and create assertions for warrants
        for drefs in self.direct_refs.values():
            for a, b in itertools.combinations(drefs, r=2):
                # code += f"    assert {a} != {b}\n"
                a_b = sorted([f'{a}',f'{b}'])
                code += f"    ensure_ne({a_b[0]}, {a_b[1]})\n"

        action_vars = ', '.join([f"{v[0]}: {v[1]}" for v in sorted(self.vars_used.items())])

        if len(code) > 0:
            code = f"def {self.action['py_name']}({action_vars}):\n{code}"
        else:
            code = f"def {self.action['py_name']}({action_vars}):\n    pass"
        # code+=f"    print('Running {self.action['name']}')\n"
        return code
#     def f_vlookup(self, what_var, where_var, where_col, is_exact=True):
#         where_obj = where_var[:-2]
#         where_col = chr(ord(where_var[-1]) + where_col - 1)
#         full_where = f"{where_obj}_{where_col}"
#         self.code.append(["assert", self.resolve_variable(what_var), "==", self.resolve_variable(where_var)])
#         return self.resolve_variable(full_where)
    def f_rselect(self, range_, group):
        """
        RSELECT(<range>, <group>) - AI select of most relevant row.
         Can select multiple rows when groups arument is used.
         <range> - address of sheet and range, only column ranges are supported
         <group> - group number. Default is group 1. Each group contains selected row.
        """
        # TODO HERE - basic one group support
        assert group == 1, "Only 1 group supported"
        # TODO Various checks
        # 1. Resolve range to variable that we typically use
        # to supprt more groups we need to scan first and create amount of vars according to this. Alternatvely when a new group number is encountered we can generte more variables  
        # No need to transpile as we alrady have it incoming resolved into variable???
        # Because range already comes as a text variable
        print("RSELECT RETURNIMG", range_)
        return range_
    def f_and(self, *args):
        if len(args) == 2 and self.paren_level > 1:
            v1 = args[0]
            v2 = args[1]
            return self.save_return(f"({self.resolve_variable(v1)} and {self.resolve_variable(v2)})", bool)
        elif self.paren_level == 1:
            for what in args:
                if what.startswith("(") and what.endswith(")"):
                    what = what[1:-1]
                self.code.append(["assert", what, 
                                    f"# {self.s_formula} from {self.cur_tbl} (action {self.action['name']})"])
            return "True"
        else:
            raise TypeError("AND() only supports 2 arguments if used in complex formula")

    def f_eq(self, v1, v2):
        self.check_resolve_types(
            self.resolve_variable(v1, True),
            self.resolve_variable(v2, True),
            operator='==')
        return self.save_return(f"({self.resolve_variable(v1)} == {self.resolve_variable(v2)})", bool)

    def f_ne(self, v1, v2):
        self.check_resolve_types(
            self.resolve_variable(v1, True),
            self.resolve_variable(v2, True),
            operator='!=')
        return self.save_return(f"({self.resolve_variable(v1)} != {self.resolve_variable(v2)})", bool)

    def f_add(self, v1, v2):
        self.check_resolve_types(
            self.resolve_variable(v1, True),
            self.resolve_variable(v2, True),
            operator='+')
        return self.save_return(f"({self.resolve_variable(v1)} + {self.resolve_variable(v2)})", int)

    def f_sub(self, v1, v2):
        self.check_resolve_types(
            self.resolve_variable(v1, True),
            self.resolve_variable(v2, True),
            operator='-')
        return self.save_return(f"({self.resolve_variable(v1)} - {self.resolve_variable(v2)})", int)

    def f_mul(self, v1, v2):
        self.check_resolve_types(self.resolve_variable(v1, True), self.resolve_variable(v2, True), operator='*')
        return self.save_return(f"({self.resolve_variable(v1)} * {self.resolve_variable(v2)})", int)

    def f_div(self, v1, v2):
        self.check_resolve_types(self.resolve_variable(v1, True), self.resolve_variable(v2, True), operator='/')
        return self.save_return(f"({self.resolve_variable(v1)} // {self.resolve_variable(v2)})", int)

    def f_lt(self, v1, v2):
        self.check_resolve_types(
            self.resolve_variable(v1, True),
            self.resolve_variable(v2, True),
            operator='<')
        return self.save_return(f"({self.resolve_variable(v1)} < {self.resolve_variable(v2)})", bool)

    def f_gt(self, v1, v2):
        self.check_resolve_types(self.resolve_variable(v1, True), self.resolve_variable(v2, True),  operator='>')
        return self.save_return(f"({self.resolve_variable(v1)} > {self.resolve_variable(v2)})", bool)

    def f_le(self, v1, v2):
        self.check_resolve_types(
            self.resolve_variable(v1, True),
            self.resolve_variable(v2, True),
            operator='<=')
        return self.save_return(f"({self.resolve_variable(v1)} <= {self.resolve_variable(v2)})", bool)

    def f_ge(self, v1, v2):
        self.check_resolve_types(
            self.resolve_variable(v1, True),
            self.resolve_variable(v2, True),
            operator='>=')
        return self.save_return(f"({self.resolve_variable(v1)} >= {self.resolve_variable(v2)})", bool)

    def transpile_str(self, s, table_name, view_name, context_col, context_row, cur_add_tbl="", cur_mode="filter"):
        assert ((cur_mode=="filter" or cur_mode=="changes_add") and context_row == -1) or (cur_mode=="view" and context_row > 0), \
                                                            "Context row must always be 3 (not %s)" % context_row
        self.cur_tbl  = view_name.strip()

        if not s.startswith("="):
            try:
                int(s)
                s = f"={s}"
            except:
                s = f"=\"{s}\""
        if hyperc.settings.DEBUG:
            print("Transpiling:", s, "mode=", cur_mode)
            print("Transpiling (tokenized):", s, full_tokenize(s), "mode=", cur_mode)
        self.s_formula = s
        self.cur_mode = cur_mode
        if cur_mode == "filter" or cur_mode == "changes_add":
            self.cur_var = f"var_{sheet_to_py(self.cur_tbl)}_{context_col.lower()}"
            if self.cur_var not in self.variable_resolution_map:
                self.add_column(self.cur_tbl.upper(), context_col.lower())
        elif cur_mode == "view":
            var = f"var_{sheet_to_py(self.cur_tbl)}__hct_direct_ref__{context_row}_{context_col.lower()}"
            if var not in self.variable_resolution_map:
                self.add_cell(viewname_u=self.cur_tbl.upper(), cell_num=context_row, cell_letter=context_col.lower())
            self.cur_var = var

        transpiled = self.transpile(full_tokenize(s))
        tkvar = self.resolve_variable(transpiled)
        if hyperc.settings.DEBUG:
            print("Transpiled to ", transpiled, "and", tkvar, "setting for", self.cur_var)
        self.check_resolve_types(
            self.resolve_variable(self.cur_var, True),
            self.resolve_variable(tkvar, True),
            operator="=")
        # if not self.is_goal:

        if cur_mode == "changes_add":
            setattr_var = self.cur_var
        else:
            setattr_var = self.resolve_variable(self.cur_var, True)
        if self.variable_resolution_map_obj[self.cur_var].table_var is not None:
            self.vars_used[self.variable_resolution_map_obj[self.cur_var].table_var] = sheet_to_py(
                str(self.variable_resolution_map_obj[self.cur_var].table_name))
        if not int(os.getenv("HYPERC_ENABLE_SIDEADD", "1")) or "." not in setattr_var or not self.is_goal:
            if cur_mode == "view":
                self.code.append([self.cur_var,"=",tkvar])
                self.code.append(
                [setattr_var, "=", self.cur_var,
                 f"#Set '{self.cur_tbl}'!{context_col}{context_row}{self.s_formula} from {self.cur_tbl} {cur_mode} (action {self.action['name']})"])
            else:
                self.code.append(
                [setattr_var, "=", tkvar,
                 f"#Set '{self.cur_tbl}'!{context_col}{context_row}{self.s_formula} from {self.cur_tbl} {cur_mode} (action {self.action['name']})"])
        else:
            setattr_attrname = setattr_var.split(".")[-1]
            setattr_where = ".".join(setattr_var.split(".")[:-1])
            if cur_mode == "view":
                self.code.append([self.cur_var,"=",tkvar])
                self.code.append(
                [f"side_effect(lambda: setattr({setattr_where}, '{setattr_attrname}', {self.cur_var}))",
                 f"#Set '{self.cur_tbl}'!{context_col}{context_row}{self.s_formula} from {self.cur_tbl} (action {self.action['name']})"])
            else:
                self.code.append(
                [f"side_effect(lambda: setattr({setattr_where}, '{setattr_attrname}', {tkvar}))",
                 f"#Set '{self.cur_tbl}'!{context_col}{context_row}{self.s_formula} from {self.cur_tbl} (action {self.action['name']})"])

    def cell_change(self, table):
        cur_tbl = table["view_name"].strip()
        add_tbl = table["table_name"].strip()
        sht_addtbl_name = sheet_to_py(add_tbl)
        newob_name = f"var_{sht_addtbl_name}_0"
        

        # TODO HERE: don't write the setter at vlookup, but write it here!!
    def add_row(self, table, step_view_name):
        cur_tbl = table["view_name"].strip()
        add_tbl = table["table_name"].strip()
        sht_addtbl_name = sheet_to_py(add_tbl)
        newob_name = f"var_{sht_addtbl_name}_0" 
        self.vars_types[newob_name] = self.classes_dict[sht_addtbl_name]
        init_pars = []
        none_cell = []
        # for k, typ in self.classes_dict[sht_addtbl_name].__annotations__.items():
        for k in table['changes_add'][0].keys():
            k = k.lower()
            if k == '__table_name__':
                continue
            # Check that we have key in add row operation
            key_check = copy.copy(list(table['changes_add'][0].keys()))
            key_check.remove('recid')
            if k.upper() not in key_check:
                continue
            self.add_column(step_view_name.strip().upper(), k)
            # varname = self.resolve_variable(f"var_{sheet_to_py(self.cur_tbl)}_{k}")
            varname = f'var_{sheet_to_py(self.cur_tbl)}_{k}'
            self.check_resolve_types(
                f"{newob_name}.{k}", varname, operator='=')
            init_par_name = f"{newob_name}_{k}_init" 
            init_pars.append(f'hct_p_{k}={init_par_name}')
            # self.code.append([f"{newob_name}.{k}" ,"=", f"{varname}"])
            self.code.append([init_par_name, "=", f"{varname} #select column {k.upper()} from \"{self.cur_tbl}\"  {self.s_formula} (action \"{self.action['name']}\"))"])
        
        init_par_string = ", ".join(init_pars)
        self.code.append(
            [f"{newob_name}", "=",
             f'{sht_addtbl_name}({init_par_string}) # {self.cur_tbl} (action "{self.action["name"]}") '])
        self.code.append([f"side_effect(lambda: HCT_OBJECTS['{sht_addtbl_name}'].append({newob_name})) # \"{self.cur_tbl}\" (action \"{self.action['name']}\")"])
        self.tables_added_rows.add(add_tbl)

    def transpile_filter_str(self, s, context_tbl, cur_mode="filter"):
        self.cur_tbl = context_tbl
        if cur_mode == "remove_row_filter":
            self.cur_mode = "filter"
        else:
            self.cur_mode = cur_mode
        self.s_formula = s
        if not s.startswith("="): 
            s = "="+s
        # print(">>>>> Transpiling filter:", s, full_tokenize(s))
        half_assert = full_tokenize(s)
        assert len(half_assert) > 1, "Filter must contain full statement" # Filter must contain full statement
        full_assert = self.transpile(half_assert)
        if full_assert.startswith("(") and full_assert.endswith(")"):
            full_assert = full_assert[1:-1]
        self.code.append(["assert", full_assert,f"# Filter `{s[1:]}` from {self.cur_tbl} (action {self.action['name']})" ])
        if cur_mode == "remove_row_filter":
            self.code.append(
                ["del", self.view_resolution_ref[self.cur_tbl.upper()].var, f"# Remove row from {self.view_resolution_ref[self.cur_tbl.upper()].table_name} (action {self.action['name']})"])


    def transpile(self, nodes):
        if isinstance(nodes, list):
            ret = ""
            for node in nodes:
                ret = str(self.transpile(node))
            return ret
        else:
            ret = self.transpile_node(nodes)
            self.last_node = nodes
            return ret
    def transpile_node(self, node):
        if isinstance(node, formulas.tokens.operand.Range):
            ret = self.transpile_range(node)
            if self.paren_level in self.function_parens:
                self.function_parens_args[self.paren_level].append(ret)
            return ret
        elif isinstance(node, formulas.tokens.parenthesis.Parenthesis):
            if node.attr["name"] == "(": 
                self.paren_level += 1
#                 print("Opened paren level", self.paren_level)
                if isinstance(self.last_node, formulas.tokens.function.Function):
#                     print("Storing last function:", self.paren_level, self.last_node)
                    self.function_parens[self.paren_level] = "f_"+self.last_node.attr["name"].lower()
                else:
                    self.function_parens[self.paren_level] = "<TBD>"
            else: 
#                 print("Paren close level", self.paren_level)
                if self.paren_level in self.function_parens:
#                     print(self.function_parens[self.paren_level].lower(), self.function_parens_args[self.paren_level])
                    ret = getattr(self, self.function_parens[self.paren_level])(*self.function_parens_args[self.paren_level])
                    self.function_parens_args[self.paren_level] = []
                    self.paren_level -= 1
                    self.function_parens_args[self.paren_level].append(ret)
                    return ret
                self.paren_level -= 1
            assert self.paren_level >= 0, "Too many closing parenthesis! %s" % self.paren_level
            return node.attr["name"]  # TODO: WARNING: this is wrong??
        elif isinstance(node, formulas.tokens.function.Function):
            self.functions.append("f_"+node.attr["name"])
            return node.attr["name"].lower()
        elif isinstance(node, formulas.tokens.operator.Separator):
            if node.attr["name"] != ",": raise ValueError("Can't support separator %s" % node.attr["name"])
            return ", "
        elif isinstance(node, formulas.tokens.operand.Number):
            isint = True
            if node.attr["name"].lower() == "true": # FIX HERE: need to check inference
                ret = True
                isint = False
            elif node.attr["name"].lower() == "false":
                ret = False
                isint = False
            if isint:
                ret = int(node.attr["name"])
            if self.paren_level in self.function_parens:
                self.function_parens_args[self.paren_level].append(ret)
            return ret
        elif isinstance(node, formulas.tokens.operand.String):
            isint = True
            if node.attr["name"].lower() == "true": # FIX HERE: need to check inference
                ret = True
                isint = False
            elif node.attr["name"].lower() == "false":
                ret = False
                isint = False
            if isint:
                ret = node.attr["expr"]
            if self.paren_level in self.function_parens:
                self.function_parens_args[self.paren_level].append(ret)
            return ret
            
        elif isinstance(node, formulas.tokens.operator.OperatorToken):
            if node.attr["name"] == "=":
                self.function_parens[self.paren_level] = 'f_eq'
                return None
            elif node.attr["name"] == "+":
                self.function_parens[self.paren_level] = 'f_add'
                return None
            elif node.attr["name"] == "-":
                self.function_parens[self.paren_level] = 'f_sub'
                return None
            elif node.attr["name"] == "*":
                self.function_parens[self.paren_level] = 'f_mul'
                return None
            elif node.attr["name"] == "/":
                self.function_parens[self.paren_level] = 'f_div'
                return None
            elif node.attr["name"] == "<":
                self.function_parens[self.paren_level] = 'f_lt'
                return None
            elif node.attr["name"] == ">":
                self.function_parens[self.paren_level] = 'f_gt'
                return None
            elif node.attr["name"] == "<=":
                self.function_parens[self.paren_level] = 'f_le'
                return None
            elif node.attr["name"] == ">=":
                self.function_parens[self.paren_level] = 'f_ge'
                return None
            elif node.attr["name"] == "<>":
                self.function_parens[self.paren_level] = 'f_ne'
                return None
            else:
                raise NotImplementedError("Not Implemented Operator: %s" % repr(node))
        else:
            raise NotImplementedError("Not Implemented: %s" % repr(node))
    def transpile_range(self, node: formulas.tokens.operand.Range):
        if hyperc.settings.DEBUG:
            print(node.attr)
        if not 'sheet' in node.attr:
            raise formulas.errors.FormulaError(f"Formula reference without row ID")
        if not node.attr['sheet']:
            cur_tbl_f = formulas.tokens.operand.Range(f"'{self.cur_tbl}'!A1")
            node.attr['sheet'] = cur_tbl_f.attr['sheet']
            node.attr['excel'] = cur_tbl_f.attr['excel']

        full_sheet = f"[{node.attr['excel']}]{node.attr['sheet']}".upper() if len(node.attr['excel']) > 0 else node.attr['sheet'].upper()

        if full_sheet in self.view_tables_ref and not ":" in node.attr.get("ref", ""):
            var_name = f"var_{sheet_to_py(full_sheet)}__hct_direct_ref__{node.attr['r1']}_{node.attr['c1'].lower()}"
            if var_name not in self.variable_resolution_map:
                self.add_cell(full_sheet.upper(), node.attr['r1'], node.attr['c1'].lower())
            return var_name
        else:
            letter = node.attr['c1'].lower()
            var_name = f"var_{sheet_to_py(full_sheet)}_{letter}"
            if var_name not in self.variable_resolution_map:
                self.add_column(full_sheet.upper(), letter)
            return var_name

    def add_var_ref(self, varname):
        "Add global reference to this exact row/col"
        if not varname in self.vars_indexes:
            # print("Checking", varname, "in", self.vars_indexes)
            # print("No row for", varname, "in", self.vars_indexes)
            raise NoRowDefined(f"No row for {varname}")
        var_idx = self.vars_indexes[varname][0]
        if var_idx == -2:
            raise Exception(f'{self.vars_indexes[varname][1]}#')
        var_ref = self.vars_indexes[varname][1]
        row = self.get_row_by_recid(sht_tbl_name=self.vars_types[varname].__name__, recid=var_idx)
        setattr(self.HCT_STATIC_OBJECTS, var_ref, row)
        type(self.HCT_STATIC_OBJECTS).__annotations__[var_ref] = self.vars_types[varname]
        if "__hct_direct_ref__" in varname and varname in self.variable_resolution_map:
            rowvar = ".".join(self.variable_resolution_map[varname].split(".")[:-1])
            self.direct_refs[self.vars_types[varname].__name__].add(rowvar)
    
    def resolve_variable(self, varname, setter=False):
        if not isinstance(varname, str):
            return str(varname)
        if varname.startswith('"') or varname.startswith("("):
            return varname
        try:
            int(varname)
            return varname
        except:
            pass
        if varname == "True" or varname == "False":
            return varname
#         print("Resolving", varname)
#         if varname[4:][:-2] in set([sheet_to_py(x) for x in self.temp_tables]):
#             print("Resolved in temp", varname)
#             varname = varname[:-2]+"_"+varname[-1]
#         elif setter == True:
        if setter and varname[4:][:-2] not in set([sheet_to_py(x) for x in self.temp_tables]):
            if "__hct_direct_ref__" in varname: #self.cur_mode == "view":
                self.add_var_ref(varname)
            # print("VAR CHECK", varname, self.variable_resolution_map)
            if varname not in self.variable_resolution_map:
                assert varname in self.variable_resolution_map, "Reference error: no such table or cell"
            return self.variable_resolution_map[varname]
        if not setter: # varname[4:][:-2] not in set([sheet_to_py(x) for x in self.temp_tables]):
            if varname in self.variable_resolution_map:
                if "__hct_direct_ref__" in varname: #self.cur_mode == "view":
                    self.add_var_ref(varname)
                if self.variable_resolution_map_obj[varname].table_var is not None:
                    self.vars_used[self.variable_resolution_map_obj[varname].table_var] = sheet_to_py(str(self.variable_resolution_map_obj[varname].table_name))
                addl = [
                    varname, "=",
                    f'{self.variable_resolution_map[varname]} # {self.variable_resolution_map_obj[varname].view_name} Resolve variable in column \"{self.variable_resolution_map_obj[varname].letter.upper()}\" from table \"{self.variable_resolution_map_obj[varname].table_name}\"']
                if self.variable_resolution_map_obj[varname].anchor_in_code is not None:
                    if addl not in self.variable_resolution_map_obj[varname].anchor_in_code:
                        self.variable_resolution_map_obj[varname].anchor_in_code.append(addl)
                else:
                    self.code.append(addl)
                self.check_resolve_types(varname,  self.variable_resolution_map[varname], operator='=')
        return varname
    
def act_name_to_py(name):
    return f"hct_{str_to_py(name)}"

def no_row_to_row(s):
    # s = re.sub(r"([A-Z])=\'", r"\g<1>1='", s) 
    # s = re.sub(r"([A-Z])$", r"\g<1>1", s) 
    s = re.sub(r"\'\!([A-Z]+)(\D)", r"'!\g<1>1\2", s)  # 'Select 4 of Trucks'!B+ -> 'Select 4 of Trucks'!B1+
    s = re.sub(r"\'\!([A-Z]+)$", r"'!\g<1>1", s)  # 'Select 4 of Trucks'!B -> 'Select 4 of Trucks'!B1
    # s = re.sub(r"=([A-Z])(\W)", r"=\g<1>1\2", s)  # =A+1 -> =A1+1
    # s = re.sub(r"=([A-Z])(\W)", r"=\g<1>1\2", s)  # =A+1 -> =A1+1
    return s

DEFAULT_VALS = {
    str: "''",
    int: 0,
    bool: True,
    None: None
}

def collect_tables(action_attr, tables):
    if "steps" in action_attr:
        for subact in action_attr["steps"]:
            tables.append(subact)
            collect_tables(subact, tables)
    elif "subactions" in action_attr:
        tables.extend(action_attr["subactions"])

def to_functions(jsdata, classes_dict, objects, module, HCT_OBJECTS, HCT_STATIC_OBJECTS, 
                                table_meta, metadata=None, work_dir=""):
    functions = {}
    goal_action = None
    tables_added_rows = set()
    global_view_var_mapper = {}
    global_table_type_mapper = {}
    if metadata is not None:
        metadata["action_map"] = {}
    progress.info("Transpiling worksheet to Python")

    # try:
    #     os.mkdir(".hc_cache")
    # except:
    #     pass

    for idx, action_attr in jsdata['actionData'].items():
        if hyperc.settings.DEBUG:
            print("- ACTION", action_attr["metadata"]["name"])
        metadata["xtj"]["Action"] = action_attr["metadata"]["name"]
        param_tables = []
        temp_tables = set()
        view_tables_ref = {}  # Contains view_name: table_name records
        view_resolution = []

        # for every possible resolv name, generate?
        # because any can reference any view or filter
        # we hope that the file will contain all tables in action
        collected_tables = []
        collect_tables(action_attr, collected_tables)
        for step in collected_tables: 
            print('ADDRESOLV', step["view_name"].strip())
            view_resolution.append(step["view_name"].strip())
            param_tables.append(step["table_name"].strip())  # pruning powers
            if step['mode'] == 'view':
                view_tables_ref[step["view_name"].strip().upper()] = XTJViewVar(view_name=step["view_name"].strip(), table_name=step["table_name"].strip())
            # TODO same for view here
        # cur_subaction = action_attr["metadata"]["name"]
        cur_subaction = None
        view_flts = ""
        step_view_name = ""
        step_view_filter_mode = "view"


        for table in collected_tables: 
            assert table["filter_mode"] == 'aio', f'"{table["view_name"]}" has incorrect filter mode "{table["filter_mode"]}".\nAIO filter only support #'
            # table does not exist # table is emtpy
            metadata["xtj"]["Step"] = table["view_name"]
            py_table_name = sheet_to_py(table["table_name"])
            assert py_table_name in HCT_OBJECTS or hasattr(HCT_STATIC_OBJECTS, py_table_name), \
                f"Table {table['table_name']} does not exist or is empty for {table['view_name']} in action {action_attr['metadata']['name']}"

        action = {'name': action_attr["metadata"]["name"]}
           
        action['py_name'] = act_name_to_py(action['name'])

        is_goal = False
        if action_attr["metadata"].get("is_required", False):
            assert goal_action is None, "Multiple goal actions not supported!"
        # if not goal_action:
            goal_action = action['py_name']
            metadata["goal_action_idx"] = idx  # TODO: this is temporary
            action['py_name'] = "hyperc_magictable_goal"
            is_goal = True
        
        if metadata is not None:
            metadata["action_map"][action['py_name']] = action_attr["metadata"]["name"]
        
        tp = XL2Py(action=action, temp=temp_tables, param=param_tables, view_resolution=view_resolution,
                   classes_dict=classes_dict, view_tables_ref=view_tables_ref, tables_added_rows=tables_added_rows,
                   HCT_OBJECTS=HCT_OBJECTS, HCT_STATIC_OBJECTS=HCT_STATIC_OBJECTS, is_goal=is_goal,
                   table_meta=table_meta, global_view_var_mapper=global_view_var_mapper,
                   global_table_type_mapper=global_table_type_mapper)
        for table in collected_tables:
            print("doing for", table["view_name"])
            metadata["xtj"]["Step"] = table["view_name"]
            if hyperc.settings.DEBUG:
                print(" --- TABLE", table["view_name"])
            py_table_name = sheet_to_py(table["table_name"])
            if not py_table_name in classes_dict:
                raise ValueError(f"No such table: {table['table_name']}")
            flts = table.get("filter", "").strip().split(" #")[0].strip().replace("\\#", "#")
            flts = flts.strip().split(" //")[0].strip().replace("\\/", "/")
            if flts.startswith("#") or flts.startswith("//"):
                flts = ""
            
            if table["mode"] == "view":
                step_view_name = table['view_name']
                view_flts = table["filter"].strip()
                if flts:
                    step_view_filter_mode = detect_filter_mode(table)
                else: step_view_filter_mode = "view"
                #Set global anchor for View at the top
                if step_view_filter_mode =="view":
                    select_anchor = list()
                    tp.code.append(select_anchor)
                    assert tp.view_resolution_ref[table['view_name'].upper()].anchor_in_code is None
                    tp.view_resolution_ref[table['view_name'].upper()].set_anchor_in_code(select_anchor)
            if table["mode"] == "select_row" and view_flts:
                tp.transpile_filter_str(view_flts, context_tbl=table['view_name'].strip(), cur_mode="filter")
            if flts:
                if table["mode"] == "select_row":
                    tp.transpile_filter_str(flts, context_tbl=table['view_name'].strip(), cur_mode="filter")
                elif table["mode"] == "remove_row_filter":
                    tp.transpile_filter_str(flts, context_tbl=table['view_name'].strip(), cur_mode="remove_row_filter")
                else:
                    tp.transpile_filter_str(flts, context_tbl=table['view_name'].strip(), cur_mode="view")

            for rec in table.get("changes", []):
                print("working on direct change", rec)
                rec_id_notfound = True
                if py_table_name in classes_dict:
                    context_row = int(rec["recid"])  # in case of random table
                else:
                    count = table_meta[table["table_name"]]["start_row"] + 1  # TODO: depends on HEADER ROW
                    for ob in HCT_OBJECTS[sheet_to_py(table["table_name"])]:
                        if ob.__recid__ == rec["recid"]:
                            rec_id_notfound = False
                            if hyperc.settings.DEBUG:
                                print("FOUND RECID", ob.__recid__, "at", count)
                            context_row = count
                            break 
                        count += 1
                if rec_id_notfound:
                    if hyperc.settings.DEBUG:
                        print( f"Can not insert out of range free-form table. Table - \"{table['table_name']}\"\nAction - \"{action_attr['metadata']['name']}\"\nView name - \"{table['view_name']}\" #")
                if context_row == -1:
                    if hyperc.settings.DEBUG:
                        print("Ignoring non-existing rewrite")
                    continue
                for k, v in rec.items():
                    if k == 'recid':
                        continue
                    assert len(k) < 4, f"Action step data column names inconsistency: {k}"
                    metadata["xtj"]["Parsing"] = f"Formula for {k[-1]}{context_row}: {v}"
                    try:
                        tp.transpile_str(v.strip().split(" #")[0].strip().replace("\\#", "#"), 
                                         table_name=table["table_name"], view_name=table["view_name"], context_col=k[-1],
                                     context_row=context_row, cur_mode="view")  
                    except NoRowDefined:
                        if hyperc.settings.DEBUG:
                            print("NoRowDefined")

            for rec in table.get("changes_row", []):  # changes now always mean view mode edit
                print("working on row change", rec)
                assert py_table_name in classes_dict
                context_row = -1
                count = table_meta[table["table_name"]]["start_row"] + 1  # TODO: depends on HEADER ROW
                # TODO here you can set type for free-form table cell
                for k, v in rec.items():
                    if k == 'recid':
                        continue
                    assert len(k) < 4, f"Action step data column names inconsistency: {k}"
                    metadata["xtj"]["Parsing"] = f"Formula for {k[-1]}{context_row}: {v}"
                    print(metadata["xtj"]["Parsing"])
                    tp.transpile_str(
                        v.strip().split(" #")[0].strip().replace("\\#", "#"),
                        table_name=table["table_name"],
                        view_name=table["view_name"],
                        context_col=k[-1],
                        context_row=context_row)

            for rec in table.get("changes_add", []):  # changes_add means add row
                print("working on row change", rec)
                assert py_table_name in classes_dict
                context_row = -1
                count = table_meta[table["table_name"]]["start_row"] + 1  # TODO: depends on HEADER ROW
                # TODO here you can set type for free-form table cell
                for k, v in rec.items():
                    if k == 'recid':
                        continue
                    assert len(k) < 4, f"Action step data column names inconsistency: {k}"
                    metadata["xtj"]["Parsing"] = f"Formula for {k[-1]}{context_row}: {v}"
                    print(metadata["xtj"]["Parsing"])
                    tp.transpile_str(v.strip().split(" #")[0].strip().replace("\\#", "#"),
                                     table_name=table["table_name"], view_name=table["view_name"], context_col=k[-1],
                                     context_row=context_row, cur_mode="changes_add")

            if table.get("changes_add", []):
                tp.add_row(table, step_view_name)
            metadata["xtj"]["Parsing"] = ""

        metadata["xtj"]["Step"] = ""
        # f_code = tp.render_code(mode=table["filter_mode"])
        s_code = tp.render_code()
        if hyperc.settings.DEBUG:
            print(s_code)
        fn = f"{work_dir}/hpy_{action['py_name']}.py"
        open(fn, "w+").write(s_code)
        f_code = compile(s_code, fn, 'exec')
        if hyperc.settings.DEBUG:
            print(f_code)
        # exec(f_code, globals())
        exec(f_code, module.__dict__)
        # functions[tp.action['py_name']] = globals()[tp.action['py_name']]
        functions[tp.action['py_name']] = module.__dict__[tp.action['py_name']]
        functions[tp.action['py_name']].orig_source = s_code
    
    metadata["xtj"]["Action"] = ""
    # Handle exception when table is empty AND nothing is ever added
    # 0. find such a table
    empty_unused_tables = []
    sht_added_tables = set([sheet_to_py(t) for t in tables_added_rows])
    for cls_n in objects:
        if len(objects[cls_n]) == 0 and not cls_n in sht_added_tables:
            empty_unused_tables.append(cls_n)
    for t in empty_unused_tables:
        # 1. remove from classes_dict
        del classes_dict[t]
        # 2. remove from globals
        del module.__dict__[t]

    # Match all group neighbor each other
    # by Breadth-first search now
    not_double_pass = True
    while not_double_pass:
        not_double_pass = False
        for tm in global_table_type_mapper.values():
            while tm.visited_group != tm.group:
                tm.visited_group = tm.group
                tmp_tm_group = copy.copy(tm.group)
                for tm_name in tmp_tm_group:
                    tm.merge_group(global_table_type_mapper[tm_name])
        for tm in global_table_type_mapper.values():
            while tm.forward_visited_group != tm.group:
                tm.forward_visited_group = tm.group
                tmp_tm_group = copy.copy(tm.group)
                for tm_name in tmp_tm_group:
                    tm.merge_group(global_table_type_mapper[tm_name])
            if tm.forward_visited_group != tm.visited_group:
                not_double_pass=True
                
    #LIN_COUNT detect
    max_int = 0
    min_int = 999999
    # set right annotations
    for k in HCT_OBJECTS:
        for table_row in HCT_OBJECTS[k]:
            for letter in table_row.__touched_annotations__:
                val = None
                types = set()
                if letter in table_row.__annotations_type_set__:
                    types.update(table_row.__annotations_type_set__[letter])
                coords = f"{letter}{table_row.__recid__}"
                if coords in table_row.__annotations_type_set__:
                    types.update(table_row.__annotations_type_set__[coords])
                sorted_type=list()
                if bool in types:
                    sorted_type.append(bool)
                if int in types:
                    sorted_type.append(int)
                sorted_type.append(str)
                for t in sorted_type:
                    try:
                        val = hyperc.util.to_type(table_row.__row_record__.get(letter.upper(), ""), t)
                        setattr(table_row, letter.lower(), val)
                        table_row.__annotations__[letter.lower()] = t
                        classes_dict[k].__annotations__[letter.lower()] = t
                        #detect lincount
                        if t is int:
                            if val > 200:
                                continue
                            if val > max_int:
                                max_int = val
                            if val < min_int:
                                min_int = val
                        break
                    except ValueError:
                        continue
            for letter in classes_dict[k].__touched_annotations__:
                if hasattr(table_row, letter):
                    continue
                val = None
                types = set()
                if letter in classes_dict[k].__annotations_type_set__:
                    types.update(classes_dict[k].__annotations_type_set__[letter])
                sorted_type=list()
                if bool in types:
                    sorted_type.append(bool)
                if int in types:
                    sorted_type.append(int)
                sorted_type.append(str)
                for t in sorted_type:
                    try:
                        val = hyperc.util.to_type(table_row.__row_record__.get(letter.upper(), ""), t)
                        setattr(table_row, letter.lower(), val)
                        table_row.__annotations__[letter.lower()] = t
                        classes_dict[k].__annotations__[letter.lower()] = t
                        #detect lincount
                        if t is int:
                            if val > 200:
                                continue
                            if val > max_int:
                                max_int = val
                            if val < min_int:
                                min_int = val
                        break
                    except ValueError:
                        continue
        if len(HCT_OBJECTS[k]) == 0:
            if k in classes_dict:
                for letter in classes_dict[k].__touched_annotations__:
                    #todo maybe should get type from classes_dict[k].__annotations_type_set__ if it possible
                    classes_dict[k].__annotations__[letter.lower()] = str
    
    #lincount set
    if max_int > hyperc.settings.HYPERC_LIN_COUNT:
        hyperc.settings.HYPERC_LIN_COUNT = max_int
    if min_int < hyperc.settings.HYPERC_INT_START:
        hyperc.settings.HYPERC_INT_START = min_int

    # Now generate init's for objects
    for clsv in classes_dict.values():
        init_f_code = []
        init_pars = []
        if hyperc.settings.DEBUG:
            print(f" {clsv} -  {clsv.__annotations__}")
        for par_name, par_type in clsv.__annotations__.items():
            if par_name == '__table_name__': continue
            # Skip None type cell
            if par_type is None:
                par_type = str
                clsv.__annotations__[par_name] = str
            init_f_code.append(f'self.{par_name} = hct_p_{par_name} # cell "{par_name.upper()}" of table "{clsv.__table_name__}"')
            if not par_type in DEFAULT_VALS:
                raise TypeError(f"Could not resolve type for {clsv.__name__}.{par_name} (forgot to init cell?)")
            init_pars.append(f"hct_p_{par_name}:{par_type.__name__}={DEFAULT_VALS[par_type]}")
        if len(init_f_code) == 0 : continue
        full_f_code = '\n    '.join(init_f_code)
        full_f_pars = ",".join(init_pars)
        full_code = f"def hct_f_init(self, {full_f_pars}):\n    {full_f_code}"
        fn = f"{work_dir}/hpy_init_{clsv.__name__}.py"
        open(fn, "w+").write(full_code)
        f_code = compile(full_code, fn, 'exec')
        exec(f_code, globals())
        clsv.__init__ = globals()["hct_f_init"] 
        clsv.__init__.__name__ = "__init__"
    
    # Now generate init for static object
    init_f_code = []
    for attr_name, attr_type in HCT_STATIC_OBJECTS.__class__.__annotations__.items():
        init_f_code.append(f"self.{attr_name} = HCT_STATIC_OBJECTS.{attr_name}")  # if it does not ignore, fix it!
    if init_f_code:
        full_f_code = '\n    '.join(init_f_code)
        full_code = f"def hct_stf_init(self):\n    {full_f_code}"
        fn = f"{work_dir}/hpy_stf_init_{HCT_STATIC_OBJECTS.__class__.__name__}.py"
        open(fn, "w+").write(full_code)
        f_code = compile(full_code, fn, 'exec')
        exec(f_code, module.__dict__)
        HCT_STATIC_OBJECTS.__class__.__init__ = module.__dict__["hct_stf_init"] 
        HCT_STATIC_OBJECTS.__class__.__init__.__name__ = "__init__"
                       
    assert goal_action, "No goal action defined!#"
    return functions


def solve_sheet(jsdata, solver_lock=None, solve_params=None, gen_pddl_only=False, work_dir=None):

    if work_dir is None:
        work_dir = hyperc.util.get_work_dir()

    solve_session_name = "hct_m_solve"
    # solve_session_name = "hct_m_" + gen_random_string()
    new_mod = types.ModuleType(solve_session_name)
    globals()[solve_session_name] = new_mod
    sys.modules[solve_session_name] = new_mod
    new_mod.side_effect = hc.side_effect
    new_mod.ensure_ne = hc.ensure_ne
    new_mod.StaticObject = type("StaticObject", (object, ), {})
    new_mod.StaticObject.__annotations__ = {}
    new_mod.StaticObject.__qualname__ = f"{solve_session_name}.StaticObject"

    solve_params = solve_params or {}
    methods_classes: dict
    objects: dict
    HCT_STATIC_OBJECTS = new_mod.StaticObject()
    new_mod.HCT_STATIC_OBJECTS = HCT_STATIC_OBJECTS

    objects, methods_classes, name_map, table_meta = create_data(jsdata, module=new_mod)  # two dicts
    HCT_OBJECTS = objects
    new_mod.HCT_OBJECTS = HCT_OBJECTS
    if solve_params and "metadata" in solve_params:
        md = solve_params["metadata"]
    else:
        md = {"xtj": {}}
    methods_classes.update(to_functions(jsdata, methods_classes, 
                                objects, module=new_mod, metadata=md,
                                table_meta=table_meta, HCT_OBJECTS=HCT_OBJECTS, HCT_STATIC_OBJECTS=HCT_STATIC_OBJECTS, work_dir=work_dir))

    methods_classes["StaticObject"] = new_mod.StaticObject

    just_classes = list(filter(lambda x: isinstance(x, type), methods_classes.values()))

    # Generate dummy init method for objects
    # obj_init = ""
    # for cls_name, v in methods_classes.items():
    #     if type(v) == type:
    #         obj_init += f"    {cls_name}()\n"

    # full_code = f"def hct_stf_dummy_init():\n{obj_init}\n    assert False"
    # fn = f"{work_dir}/hpy_stf__dummy_init_{HCT_STATIC_OBJECTS.__class__.__name__}.py"
    # open(fn, "w+").write(full_code)
    # f_code = compile(full_code, fn, 'exec')
    # exec(f_code, new_mod.__dict__)
    # methods_classes["static_init"] = new_mod.__dict__["hct_stf_dummy_init"]


    with open(f"{work_dir}/out.json", "w+") as fd:
        fd.write(json.dumps(jsdata, indent=4))
    with open("./objects.pickle", "wb+") as fd:
        dill.dump(objects, fd)
    with open("./classes.pickle", "wb+") as fd:
        classes = {k: v for k,v in methods_classes.items() if isinstance(v, type)}
        dill.dump(classes, fd)

    with open(f"{work_dir}/out.py", "w+") as fd:
        fd.write("import json, hyperc, app, types\nfrom hyperc import side_effect\n\n")
        fd.write(f"jsdata=json.load(open('{work_dir}/out.json'))\n\n")
        fd.write("""HCT_OBJECTS = dict()
objects, methods_classes, name_map = app.create_data(jsdata)  # two dicts
methods_classes.update(app.to_functions(jsdata, methods_classes))

for k,v in methods_classes.items():
    if isinstance(v, type):
        globals()[k] = v



""")

        for k,v in methods_classes.items():
            if hasattr(v, "orig_source"):
                fun_run = v
                if hyperc.settings.DEBUG:
                    print(v.orig_source)
                fd.write(v.orig_source+"\n")
                
                # for i, l in zip(range(1, len(fun_run.orig_source)), fun_run.orig_source.split("\n")):
                    # print(i, l)
        fd.write("""

# for k,v in methods_classes.items():
#     if isinstance(v, types.FunctionType):
#         methods_classes[k] = globals()[k]

# hyperc.solve(hyperc_magictable_goal, globals_=methods_classes)
hyperc.solve(hyperc_magictable_goal)
""")

    # print("CODE", methods_classes["hyperc_magictable_goal"].__code__.co_code)
    import inspect
    # print("TXT", inspect.getsource(methods_classes["hyperc_magictable_goal"]))
    addition_modules = [new_mod]
    plan_or_invariants = hyperc.solve(
        methods_classes["hyperc_magictable_goal"],
        globals_=methods_classes, solver_lock=solver_lock, extra_instantiations=just_classes, **solve_params,
        gen_pddl_only=gen_pddl_only, work_dir=work_dir, addition_modules=addition_modules)
    progress.info("Solved, translating data heap to worksheet")
    if "GENERATE_INVARIANTS" in solve_params['metadata']:
        invarians = []
        for invariant in plan_or_invariants:
            json_tables = defaultdict(list)
            invarians.append(json_tables)
            for arg in invariant:
                if hasattr(arg,'__table_name__'):
                    json_tables[arg.__table_name__.split('!')[0]].append(arg.__row_record__)
        return invarians
    else:
        # jsdata["tableOutputData"] = copy.deepcopy(jsdata["tableInputData"][0]["sheets"])
        jsdata["actionData"][md["goal_action_idx"]]["result"] = copy.deepcopy(jsdata["tableInputData"][0]["sheets"])
        # md["plan_steps"][-1]["function"] = md["goal_action_idx"]  # fix goal action name
        for ob in md["plan_steps"]:
            ob["function"] = md["action_map"][ob["function"]]
        jsdata["actionData"][md["goal_action_idx"]]["plan"] = md["plan_steps"]
        for tbl in jsdata["actionData"][md["goal_action_idx"]]["result"]:
            if len(tbl["records"]) == 0: continue
            if tbl["name"] not in table_meta: continue
            i = table_meta[tbl["name"]]["start_row"]  # first row in data table is always a header row!
            rec_ids = set()
            dup_recids = []
            py_table_name = sheet_to_py(tbl["name"])
            for rec in tbl["records"]:
                if rec["recid"] in rec_ids:
                    if hyperc.settings.DEBUG:
                        print("WARNING! Duplicate record ID!")
                    dup_recids.append(rec["recid"])
                rec_ids.add(rec["recid"])

            if py_table_name in objects:
                for obj in objects[py_table_name]:
                    # if i >= len(objects[sheet_to_py(tbl["name"])]):
                    if i >= len(tbl["records"]):
                        for ri in range(i, i+100):
                            if not ri in rec_ids: break
                        tbl["records"].append({ "recid": ri })
                        rec_ids.add(ri)
                    # print("Scanning object", obj, "in", sheet_to_py(tbl["name"]), dir(obj), tbl["records"])
                    for k in dir(obj):
                        if k.startswith("_"): continue
                        # print("ADDING FOR", tbl["name"], i, k, getattr(obj, k))
                        tbl["records"][i][k.upper()] = str(getattr(obj, k))
                    i += 1

    # print("emitting", jsdata)
    # HCT_OBJECTS = old_hct_objects
    # HCT_STATIC_OBJECTS = old_static_objects
    try:
        del sys.modules[solve_session_name]
    except:
        pass
    try:
        del globals()[solve_session_name]
    except:
        pass
    return jsdata


def run_one(message, metadata=None):
    jsdata = message["data"]
    methods_classes: dict
    objects: dict
    HCT_OBJECTS = defaultdict(list) 

    # TODO HERE: put new mod, create static objects classes, etc...

    session_name = gen_random_string()
    new_mod = types.ModuleType(session_name)
    new_mod.StaticObject = type("StaticObject", (object, ), {})
    new_mod.StaticObject.__annotations__ = {}
    HCT_STATIC_OBJECTS = new_mod.StaticObject()
    new_mod.HCT_OBJECTS = HCT_OBJECTS
    new_mod.HCT_STATIC_OBJECTS = HCT_STATIC_OBJECTS
    new_mod.side_effect = hc.side_effect
    if metadata is None:
        md = {"xtj": {}}
    else:
        md = metadata

    objects, methods_classes, name_map, table_meta = create_data(jsdata, module=new_mod)  # parse entrypoint 
    HCT_OBJECTS = objects
    methods_classes.update(to_functions(jsdata, methods_classes, objects, 
                                        module=new_mod, HCT_OBJECTS=HCT_OBJECTS,
                           table_meta=table_meta, HCT_STATIC_OBJECTS=HCT_STATIC_OBJECTS, metadata=md))

    if jsdata["actionData"][message["action"]]["metadata"]["is_required"]:
        fun_run = methods_classes["hyperc_magictable_goal"]
    else:
        fun_run = methods_classes[act_name_to_py(jsdata["actionData"][message["action"]]["metadata"]["name"])]

    kwargs = {}
    try:
        i = 0
        for k, v in fun_run.__annotations__.items():
            kwargs[k] = objects[v.__name__][int(list(message["selected_rows"].items())[i][1])-1]
            i += 1
    except IndexError:
        raise TypeError(f'Not enough data in table {v.__name__[4:]} to test the action {jsdata["actionData"][message["action"]]["metadata"]["name"]}')
    
    print("Running with")
    aargs = kwargs.items()
    all_lines = []
    if aargs: all_lines = ["Arguments (first rows of tables):"]
    for k, v in aargs:
        print(f"Arg {k}:")
        all_lines.append(f"Arg {k}:")
        for a in string.ascii_lowercase:
            try:
                print(f"  .{a}={getattr(v, a)}")
                all_lines.append(f"  .{a}={getattr(v, a)}")
            except AttributeError:
                print(f"  .{a}=[no data]")
    # all_lines.append("---")

    # fun_run(**kwargs)
    try:
        fun_run(**kwargs)
        all_lines = ["Passed!\nAction can be run with rows provided."]
    except AssertionError as e:
        # for i, l in zip(range(1, len(fun_run.orig_source)), fun_run.orig_source.split("\n")):
        #     print(i, l)
        #     all_lines.append(f"{i} {l}")
        # raise AssertionError(f"Could not satisfy %s" % fun_run.orig_source.split('\n')[e.__traceback__.tb_next.tb_lineno - 1])
        # all_lines.append("---")
        all_lines.append(f"Could not satisfy %s" % (fun_run.orig_source.split('\n')[e.__traceback__.tb_next.tb_lineno - 1]).split("#")[-1])
        # print(e.__traceback__.tb_frame.f_lineno)
        # raise e
    except Exception as e:
        all_lines.append(f"Error {type(e).__name__}: %s" % (fun_run.orig_source.split('\n')[e.__traceback__.tb_next.tb_lineno - 1]).split("#")[-1])
        import traceback
        traceback.print_exc()
    return "\n".join([v.replace("<", "&lt;").replace(">", "&gt;") for v in all_lines]).replace("\n", "<br/>")


class TableWrapper:
    def __init__(self, table_data):
        self.table_data = table_data
        self.table = table_data["records"]
        self.table_name = table_data["name"]
        self.table_id = table_data["id"]
    
    def __getattribute__(self, name):
        if name[0] in string.ascii_uppercase and name[1] in string.digits:
            rowNumber = int(name[1:])-1
            colName = name[0]
            row = self.table[rowNumber]
            for ob in row:
                if ob.endswith(colName):
                    return row[ob]
            raise AttributeError(f"{name} address was not found in table")
        return super().__getattribute__(name)
    
    def __setattr__(self, name, val):
        if name[0] in string.ascii_uppercase and name[1] in string.digits:
            rowNumber = int(name[1:])-1
            colName = name[0]
            row = self.table[rowNumber]
            for ob in row:
                if ob.endswith(colName):
                    row[ob] = val
                    return val
            raise AttributeError(f"{name} address was not found in table")
        return super().__setattr__(name, val)
    
    def append(self, value):
        rowid = len(self.table) + 1
        all_ids = [v["recid"] for v in self.table]
        while rowid in all_ids:
            rowid += 1
        row_record = {"recid": rowid}
        colN = 0
        for col in value:
            d_id = f"{chr(65+colN)}"
            # print("Setting APPEND", d_id, "to", col)
            row_record[d_id] = str(col)  # For text-only records compatilibilty...
            colN += 1
        self.table.append(row_record)
    
    def __iter__(self):
        ltable = []
        for value in self.table:
            colN = 0
            row = []
            for col in value:
                d_id = f"{chr(65+colN)}"
                if not d_id in value: break
                row.append(value[d_id])
                colN += 1
            ltable.append(row)
        return iter(ltable)


class XTJ:
    def __init__(self, fd, goal_name=None, input_name=None, gen_pddl_only = False, work_dir=None):
        if isinstance(fd, dict):
            self.json_data = fd
        else:
            self.json_data = json.load(fd)
        # XTJ version Check
        assert StrictVersion(str(self.json_data['version'])) >= StrictVersion(
            XTJ_VERSION), f"XTJ version should be >= {XTJ_VERSION} but has {self.json_data['version']}"

        # clean up tail blank line
        for inputTable in self.json_data['tableInputData']:
            for sheet in inputTable['sheets']:
                for idx, rec in reversed(list(enumerate(copy.copy(sheet['records'])))):
                    allEmptyRec = True
                    for k, v in rec.items():
                        if k == 'recid':
                            continue
                        if v != '':
                            allEmptyRec = False
                            break
                    if allEmptyRec:
                        del sheet['records'][idx]
                        
        self.tables = {}
        self.tables_ids = {}
        if goal_name is None:
            required_set = False
            for a in self.json_data['actionData'].values():
                if a['metadata'].get('is_required', False):
                    required_set = True
            if not required_set and self.json_data['actionData']:
                self.json_data['actionData'][list(self.json_data['actionData'].keys())[0]]['metadata']['is_required'] = True
        else:
            for a in self.json_data['actionData']:
                if a['metadata']['name'] == goal_name:
                    for ad in self.json_data['actionData']:
                        ad['metadata']['is_required'] = False
                    a['metadata']['is_required'] = True

        input_found = None
        if input_name is None:
            for input in self.json_data["tableInputData"]:
                if input.get('is_required', False):
                    input_found = input
        else:
            for inp in self.json_data["tableInputData"]:
                if inp["name"] == input_name:
                    input_found = input
        if input_found is None:
            input_found = self.json_data["tableInputData"][0]
        for table in input_found["sheets"]:
            self.tables[table["name"]] = table
            self.tables_ids[table["id"]] = table
        self.metadata = {"xtj": {}}
        self.gen_pddl_only = gen_pddl_only
        self.work_dir = work_dir

    
    def solve(self, solve_params=None, metadata=None, solver_lock=None):
        kwargs = solve_params or {}
        if metadata is not None:
            self.metadata = metadata
        if not "xtj" in self.metadata:
            self.metadata["xtj"] = {}
        # print("SOLVING", json.dumps(self.json_data))
        if not "metadata" in kwargs:
            kwargs["metadata"] = self.metadata
        if metadata and solve_params:
            assert kwargs["metadata"] == metadata
        if metadata is not None and "GENERATE_INVARIANTS" in metadata:
            assert "COMMAND" in metadata
            json_data_copy = copy.deepcopy(self.json_data)
            del json_data_copy["actionData"]
            json_data_copy["actionData"] = {}
            json_data_copy["actionData"][metadata["COMMAND"]] = self.json_data["actionData"][metadata["COMMAND"]]
            json_data_copy["actionData"][metadata["COMMAND"]]["metadata"]["is_required"] = True
            json_data_copy["actionData"][metadata["COMMAND"]]['kwargs'] = solve_sheet(json_data_copy, solve_params=kwargs, work_dir=self.work_dir)
            return json_data_copy
        APPENDIX_save = hyperc.settings.APPENDIX
        if hyperc.settings.APPENDIX == "_":
            for action in self.json_data["actionData"].values():
                if action["metadata"].get("is_required"):
                    hyperc.settings.APPENDIX = str_to_py(action["metadata"]["name"])
            hyperc.settings.APPENDIX = f'_{hyperc.settings.APPENDIX}_{str_to_py(self.json_data["tableInputData"][self.json_data["selectedInput"]]["name"])}_'
        if self.work_dir is None:
            self.work_dir = hyperc.util.get_work_dir()
        try:
            xt = solve_sheet(self.json_data, solve_params=kwargs, gen_pddl_only=self.gen_pddl_only, work_dir=self.work_dir, solver_lock=solver_lock)
        finally:
            hyperc.settings.APPENDIX = APPENDIX_save
        hyperc.settings.APPENDIX = APPENDIX_save
        return xt

    def merge_result(self, goal=None, input_name=None):
        ok = False
        result = None
        json_data = copy.deepcopy(self.json_data)
        for action in json_data['actionData'].values():
            if goal is None:
                if action['metadata'].get('is_required', False):
                    result = action['result']
                    ok = True
                    break
            else:
                if goal == action['metadata']['name']:
                    result = action['result']
                    ok = True
                    break
        if goal is None:
            if not ok:
                result = list(json_data['actionData'].values())[0]['result']
        else:
            assert ok, f"Action name {goal} not found"

        ok = False
        if input_name is None:
            json_data["tableInputData"][0]['sheets'] = copy.deepcopy(result)
            ok = True
        else:
            for input in json_data["tableInputData"]:
                if input['name'] == input_name:
                    ok = True
                    input['sheets'] = copy.deepcopy(result)
                    break
        assert ok, f"Input {input_name} not found."
        return XTJ(json_data)

    def __getitem__(self, idx):
        if idx in self.tables:
            return TableWrapper(self.tables[idx])
        if idx in self.tables_ids:
            return TableWrapper(self.tables_ids[idx])
        raise IndexError(f"Table {idx} not found in loaded tables")
    
    def __setitem__(self, idx, val):
        if idx in self.tables_ids:
            idx = self.tables_ids[idx]["name"]
        if not idx in self.tables:
            raise IndexError(f"Table {idx} not found in loaded tables")
        if isinstance(val, list) and not val:
            self.tables[idx]["records"] = []
        elif isinstance(val, list) and val:
            # TODO HERE: if table is random: emit error
            table_id = self.tables[idx]["id"]
            new_header = val[0]
            if self.tables[idx]["records"]:
                orig_header = [] # TODO HERE: fix header row if present!
                first_rec = self.tables[idx]["records"][0]
                has_header = True
                for colN in range(0, len(first_rec)-1):
                    d_id = f"{chr(65+colN)}"
                    if not d_id in first_rec:
                        has_header = False
                        break
                    orig_header.append(first_rec[d_id])
                    colN += 1
                if has_header and orig_header != new_header:
                    raise ValueError(f"Headers don't match: original is {orig_header}, new is {new_header}")
            dim = len(new_header)

            self.tables[idx]["records"] = []
            rowid = 0
            for row in val:
                rowid += 1
                colN = 0
                # assert len(row) == dim, "Array dimensions inconsistscy"
                row_record = {"recid": rowid}
                for col in row:
                    d_id = f"{chr(65+colN)}"
                    # print("Setting", d_id, "to", col)
                    row_record[d_id] = str(col)  # For text-only records compatilibilty...
                    colN += 1
                self.tables[idx]["records"].append(row_record)
        else:
            raise ValueError("Only list is supported")
    
    def asjson(self):
        return json.dumps(self.json_data, indent=4)
    
    def get(self):
        return self.json_data

                    



        
