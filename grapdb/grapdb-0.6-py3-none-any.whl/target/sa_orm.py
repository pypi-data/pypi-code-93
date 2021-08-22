from pathlib import Path
from ..graph import (
    SCHEMA_NAME,
    Array,
    ColoRef,
    CompositeType,
    DataType,
    Enum,
    Graph,
    Vertex,
)
from code_writer import CodeWriter, fmt_pascal


preamble = """\
from typing import List, Tuple

from sqlalchemy import (  # pylint: disable=E0401,W0611
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    FetchedValue,
    ForeignKeyConstraint,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship  # pylint: disable=E0401 

from .graph_orm_base import (
    Base,
    CompositeArray,
    CompositeType,
    CounterMixin,
    EdgeMixin,
    EntryPointMixin,
    ExtendsMixin,
    Gid,
    TGid,
    VertexMixin,
)
"""

delim = (None, None)


def generate(graph: Graph, path: Path) -> None:
    mod = generate_user_types_module(graph)
    with (path / "graph_orm.py").open("w") as f:
        f.write(mod)
    source = Path(__file__).parent / "rsrc/graph_orm_base.py"
    target = path / "graph_orm_base.py"
    with source.open("r") as source_f, target.open("w") as target_f:
        target_f.write(source_f.read())


def generate_user_types_module(graph: Graph) -> str:
    cw = CodeWriter()
    cw.emit_raw(preamble)
    for enum in graph.enums.values():
        cw.emit()
        cw.emit()
        cw.emit_list(
            [repr(value) for value in enum.values],
            ("[", "]"),
            "_{}_values =".format(enum.name),
        )
        cw.emit("{0} = Enum(*_{0}_values, name='{0}')".format(enum.name))

    for ctype in graph.ctypes.values():
        if ctype.drop:
            continue
        cw.emit()
        cw.emit()
        cw.emit_list(
            [
                f'Column("{field[0]}", {graph_type_to_sa_type(field[1])})'
                for field in ctype.fields
            ],
            ("[", "]"),
            before=f'{fmt_pascal(ctype.name)} = CompositeType("{ctype.name}", ',
            after=f', schema="{SCHEMA_NAME}")',
        )
        cw.emit(f"{fmt_pascal(ctype.name)}T = {graph_type_to_mypy_type(ctype)}")

    for vertex in graph.vertices.values():
        if vertex.drop:
            continue
        cw.emit()
        cw.emit()
        parent_classes = ["Base"]
        # Order of classes is important for Python's MRO as they all implement
        # variants of get_vshard().
        if vertex.entry_point is not None:
            parent_classes.append("EntryPointMixin")
        elif vertex.extends is not None:
            parent_classes.append("ExtendsMixin")
        parent_classes.append("VertexMixin")
        cw.emit(
            "class {}({}):".format(fmt_pascal(vertex.name), ", ".join(parent_classes))
        )
        with cw.indent():
            cw.emit("__tablename__ = '{}'".format(vertex.name))
            table_args = []
            if vertex.entry_point is not None:
                table_args.append(
                    "UniqueConstraint('{}')".format(vertex.entry_point.name)
                )
            if vertex.has_colos():
                if vertex.extends:
                    table_args.append(
                        "ForeignKeyConstraint(['gid'], ['{}.gid'])".format(
                            vertex.extends.name
                        )
                    )
                for col in vertex.extra_cols:
                    if not isinstance(col.data_type, ColoRef):
                        continue
                    table_args.append(
                        "ForeignKeyConstraint(['{}'], ['{}.gid'])".format(
                            col.name, col.data_type.ref.name
                        )
                    )
            if table_args:
                # NOTE: Manually add final comma to ensure that a one-element
                # tuple has a comma after the first element (otherwise, it's
                # not interpreted as a tuple).
                table_args[-1] += ","
                cw.emit_list(
                    table_args, ("", ""), "__table_args__ = (", ")", skip_last_sep=True
                )
            if vertex.entry_point:
                cw.emit("_entry_point = '{}'".format(vertex.entry_point.name))
            else:
                cw.emit("_entry_point = None")
            for col in vertex.extra_cols:
                if col.drop:
                    continue
                dt = graph_type_to_sa_type(col.data_type)
                default_arg = ", server_default=FetchedValue()" if col.default else ""
                nullable_arg = ", nullable=True" if col.nullable else ""
                cw.emit(
                    "{} = Column({}{}{})".format(
                        col.name, dt, default_arg, nullable_arg
                    )
                )
            for col in vertex.extra_cols:
                if not isinstance(col.data_type, ColoRef):
                    continue
                cw.emit(
                    "{0}_ref = relationship('{1}', foreign_keys=[{0}])".format(
                        col.name, fmt_pascal(col.data_type.ref.name)
                    )
                )
            if vertex.extends:
                cw.emit(
                    "{} = relationship('{}', back_populates='{}')".format(
                        vertex.extends.name,
                        fmt_pascal(vertex.extends.name),
                        vertex.name,
                    )
                )
            for extends_backref in vertex.extends_backrefs:
                cw.emit("{} = relationship(".format(extends_backref.name))
                with cw.indent():
                    cw.emit("'{}',".format(fmt_pascal(extends_backref.name)))
                    cw.emit("uselist=False,")
                    cw.emit("back_populates='{}',".format(vertex.name))
                cw.emit(")")
            for counter_backref in vertex.counter_backrefs:
                counter_name = counter_backref.get_full_name()
                with cw.block("{} = relationship(".format(counter_name), ")"):
                    cw.emit("'{}',".format(fmt_pascal(counter_name)))

    for edge in graph.edges.values():
        if edge.drop:
            continue
        cw.emit()
        cw.emit()
        cw.emit("class {}(Base, EdgeMixin):".format(fmt_pascal(edge.name)))
        with cw.indent():
            cw.emit("__tablename__ = '{}'".format(edge.name))
            with cw.block("__table_args__ = (", ")", delim):
                cw.emit(
                    "ForeignKeyConstraint(['src'], ['{}.gid']),".format(
                        edge.src.name,
                    )
                )
                for col in edge.extra_cols:
                    if not isinstance(col.data_type, ColoRef):
                        continue
                    cw.emit(
                        "ForeignKeyConstraint(['{}'], ['{}.gid']),".format(
                            col.name, col.data_type.ref.name
                        )
                    )
            cw.emit("_src_cls = {}".format(fmt_pascal(edge.src.name)))
            cw.emit("_tgt_cls = {}".format(fmt_pascal(edge.tgt.name)))
            for col in edge.extra_cols:
                if col.drop:
                    continue
                dt = graph_type_to_sa_type(col.data_type)
                pk_arg = ", primary_key=True" if col.primary_key else ""
                default_arg = ", server_default=FetchedValue()" if col.default else ""
                nullable_arg = ", nullable=True" if col.nullable else ""
                cw.emit(
                    "{} = Column({}{}{}{})".format(
                        col.name, dt, pk_arg, default_arg, nullable_arg
                    )
                )
            for col in edge.extra_cols:
                if not isinstance(col.data_type, ColoRef):
                    continue
                cw.emit(
                    "{0}_ref = relationship('{1}', foreign_keys=[{0}])".format(
                        col.name, fmt_pascal(col.data_type.ref.name)
                    )
                )
            cw.emit(
                "{} = relationship('{}')".format(
                    edge.src.name, fmt_pascal(edge.src.name)
                )
            )

    for edge in graph.edges.values():
        if not edge.counters:
            continue
        edge_col_lookup = {col.name: col for col in edge.cols}
        for counter in edge.counters:
            cw.emit()
            cw.emit()
            cw.emit(
                "class {}(Base, CounterMixin):".format(
                    fmt_pascal(edge.name + "_counter_" + counter.name)
                )
            )
            with cw.indent():
                cw.emit(
                    "__tablename__ = '{}'".format(
                        edge.name + "_counter_" + counter.name
                    )
                )
                with cw.block("__table_args__ = (", ")"):
                    cw.emit(
                        "ForeignKeyConstraint(['src'], ['{}.gid']),".format(
                            edge.src.name
                        )
                    )
                for col_name in counter.cols:
                    col = edge_col_lookup[col_name]
                    dt = graph_type_to_sa_type(col.data_type)
                    cw.emit("{} = Column({}, primary_key=True)".format(col.name, dt))

    cw.emit()
    cw.emit()
    cw.emit_list(
        [fmt_pascal(v.name) for v in graph.vertices.values() if not v.drop],
        bracket=("[", "]"),
        before="vertex_types = ",
    )
    cw.emit()
    cw.emit_list(
        [fmt_pascal(e.name) for e in graph.edges.values() if not e.drop],
        bracket=("[", "]"),
        before="edge_types = ",
    )
    cw.emit()
    cw.emit_list(
        [
            fmt_pascal(counter.get_full_name())
            for e in graph.edges.values()
            for counter in e.counters
            if not counter.drop
        ],
        bracket=("[", "]"),
        before="counter_types = ",
    )

    return cw.render()


def graph_type_to_sa_type(data_type: DataType) -> str:
    if isinstance(data_type, (ColoRef, Vertex)):
        return "Gid"
    elif isinstance(data_type, Enum):
        return data_type.name
    elif isinstance(data_type, CompositeType):
        return fmt_pascal(data_type.name)
    elif isinstance(data_type, Array):
        if isinstance(data_type.element_type, CompositeType):
            return "CompositeArray({})".format(
                graph_type_to_sa_type(data_type.element_type)
            )
        else:
            return "ARRAY({})".format(graph_type_to_sa_type(data_type.element_type))
    else:
        return sql_type_to_sa_type(data_type)


def sql_type_to_sa_type(sql_type: str) -> str:
    assert not sql_type.endswith("[]"), sql_type
    sql_type_norm = sql_type.lower()
    if sql_type_norm == "text":
        return "String"
    elif sql_type_norm == "timestamp":
        return "DateTime"
    elif sql_type_norm == "smallint":
        return "SmallInteger"
    else:
        return sql_type


def graph_type_to_mypy_type(data_type: DataType) -> str:
    if isinstance(data_type, (ColoRef, Vertex)):
        return "TGid"
    elif isinstance(data_type, Enum):
        return "str"
    elif isinstance(data_type, CompositeType):
        return "Tuple[{}]".format(
            ", ".join(graph_type_to_mypy_type(field[1]) for field in data_type.fields)
        )
    elif isinstance(data_type, Array):
        return "List[{}]".format(graph_type_to_mypy_type(data_type.element_type))
    else:
        return sql_type_to_mypy_type(data_type)


def sql_type_to_mypy_type(sql_type: str) -> str:
    assert not sql_type.endswith("[]"), sql_type
    sql_type_norm = sql_type.lower()
    if sql_type_norm == "text":
        return "str"
    elif sql_type_norm == "timestamp":
        return "datetime.datetime"
    elif sql_type_norm in ("smallint", "bigint", "integer"):
        return "int"
    else:
        return sql_type
