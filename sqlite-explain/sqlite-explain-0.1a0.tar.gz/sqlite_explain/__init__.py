from typing import Dict, Any, Tuple
import re


class Explainer:
    _re_named_parameter = re.compile(":([a-zA-Z0-9_]+)")

    def __init__(self, operations):
        self.operations = operations
        self._info = execute_operations(self.operations)

    @property
    def columns(self):
        return self._info["result_row"]

    @property
    def cursors(self):
        return self._info["cursors"]

    @classmethod
    def query(cls, db, sql: str) -> "Explainer":
        possible_params = cls._re_named_parameter.findall(sql)
        explain = "explain {sql}".format(sql=sql)
        results = db.execute(explain, {p: None for p in possible_params})
        return cls(results.fetchall())


def execute_operations(operations, max_iterations=100, trace=None):
    trace = trace or (lambda *args: None)
    registers: Dict[int, Any] = {}
    cursors: Dict[int, Tuple[str, Dict]] = {}
    instruction_pointer = 0
    iterations = 0
    result_row = None
    while True:
        iterations += 1
        if iterations > max_iterations:
            break
        addr, opcode, p1, p2, p3, p4, p5, comment = operations[instruction_pointer]
        trace(instruction_pointer, (addr, opcode, p1, p2, p3, p4, p5, comment))
        if opcode == "Init":
            if p2 != 0:
                instruction_pointer = p2
                continue
            else:
                instruction_pointer += 1
                continue
        elif opcode == "Goto":
            instruction_pointer = p2
            continue
        elif opcode == "Halt":
            break
        elif opcode == "OpenRead":
            cursors[p1] = (
                "database_table",
                {
                    "rootpage": p2,
                    "connection": p3,
                },
            )
        elif opcode == "OpenEphemeral":
            cursors[p1] = (
                "ephemeral",
                {
                    "num_columns": p2,
                    "index_keys": [],
                },
            )
        elif opcode == "MakeRecord":
            registers[p3] = ("MakeRecord", {"registers": list(range(p1 + p2))})
        elif opcode == "IdxInsert":
            record = registers[p2]
            cursors[p1][1]["index_keys"].append(record)
        elif opcode == "Rowid":
            registers[p2] = ("rowid", {"table": p1})
        elif opcode == "Sequence":
            registers[p2] = ("sequence", {"next_from_cursor": p1})
        elif opcode == "Column":
            registers[p3] = ("column", {"cursor": p1, "column_offset": p2})
        elif opcode == "ResultRow":
            p1 = p1
            p2 = p2
            trace("ResultRow: ", list(range(p1, p1 + p2)), registers)
            result_row = [registers.get(i) for i in range(p1, p1 + p2)]
        elif opcode == "Integer":
            registers[p2] = ("Integer", p1)
        elif opcode == "String8":
            registers[p2] = ("String", p4)
        instruction_pointer += 1
    return {"registers": registers, "cursors": cursors, "result_row": result_row}
