import lark

from firepit import query
from firepit.query import Query


grammar = """
    ?start: pipeline

    ?pipeline: table
             | pipeline "|" stage

    ?stage: // aggregate
          | filter
          //| group
          | limit
          | order
          | offset
          | projection
          //| count

    table: "table" table_name

    ?table_name: NAME

    //filter: "where" predicate
    filter: "filter" cond_list

    cond_list: cond ("," cond)*

    predicate: disj

    disj: conj
        | disj "or" conj

    conj: cond
        | conj "and" cond

    cond: column OP value
         //| "(" disjunction ")"

    ?column: NAME

    order: "sort" sort_spec_list

    sort_spec_list: sort_spec ("," sort_spec)*

    sort_spec: column (direction)?

    direction: "asc"i -> asc
             | "desc"i -> desc

    limit: "limit" integer

    offset: "offset" integer

    projection: ("proj"|"project"|"projection") column_list

    column_list: column ("," column)*

    integer: NUMBER

    OP: /([<>!]?=|[<>])/

    ?value: NUMBER -> integer
          | STRING -> qstr

    //aggregate: "aggregate" (agg_func)?

    //agg_func: agg_func_name "(" column ")"

    ////agg_func_name: "COUNT" | "SUM" | "MIN" | "MAX" | "AVG"
    //?agg_func_name: NAME


    %import common.CNAME -> NAME
    %import common.NUMBER -> NUMBER
    %import common.ESCAPED_STRING -> STRING
    %import common.WS

    %ignore WS
"""


@lark.v_args(inline=True)    # Affects the signatures of the methods
class Compiler(lark.Transformer):
    def __init__(self):
        self.vars = {}

    def pipeline(self, qry, stage):
        if not isinstance(qry, Query):
            tmp = qry
            qry = query.Query()
            qry.append(tmp)
        qry.append(stage)
        return qry

    def table(self, name):
        return query.Table(name)

    def filter(self, preds):
        return query.Filter(preds)

    def cond_list(self, *conds):
        return conds

    def cond(self, col, op, val):
        return query.Predicate(col, op, val)

    def projection(self, args):
        return query.Projection(args)

    def column_list(self, *cols):
        return cols

    def operator(self, op):
        return op

    def order(self, specs):
        return query.Order(specs)

    def sort_spec_list(self, *specs):
        return list(specs)

    def sort_spec(self, col, asc=query.Order.ASC):
        return (col.value, asc)

    def limit(self, val):
        return query.Limit(val)

    def offset(self, val):
        return query.Offset(val)

    def integer(self, val):
        return int(val)

    def qstr(self, name, value):
        return (name.value, value.value.strip('"'))

    def asc(self):
        return query.Order.ASC

    def desc(self):
        return query.Order.DESC


class ParseError(Exception):
    pass


class Parser:
    def __init__(self):
        self.parser = lark.Lark(grammar, parser='lalr', transformer=Compiler())

    def parse(self, pipeline):
        try:
            return self.parser.parse(pipeline)
        except lark.exceptions.LarkError as e:
            raise ParseError(str(e)) from e


if __name__ == '__main__':
    import sys
    parser = Parser()
    pipeline = parser.parse(sys.argv[1])
    qry, vals = pipeline.render('%s')
    print('QUERY: ', qry)
    print('VALUES:', vals)
