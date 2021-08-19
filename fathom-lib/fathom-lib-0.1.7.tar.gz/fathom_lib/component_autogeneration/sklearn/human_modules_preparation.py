from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Node:
    key: str
    terminal: Any
    children: Dict[str, "Node"]
    path: List[str]

    def dump(self):
        return {
            "key": self.key,
            "children": list([node.dump() for node in self.children.values()]),
        }

    def count_children(self):
        if self.terminal:
            return 1
        else:
            return sum([node.count_children() for node in self.children.values()])

    def extract_terminals(self):
        children = list(self.children.values())
        print(children)
        terminals = []
        while len(children) > 0:
            # add nodes
            current_node = children.pop()
            if current_node.terminal:
                terminals.append(current_node)

            for child in current_node.children.values():
                children.append(child)
        return terminals


class Trie:
    def __init__(self):
        self.trie = Node("root", None, {}, [])

    def add_module(self, module: List[str]):
        current_trie = self.trie
        for i, submodule in enumerate(module):
            terminal = i == len(module) - 1
            if submodule not in current_trie.children:
                if terminal:
                    current_trie.children[submodule] = Node(
                        submodule, terminal, {}, current_trie.path
                    )
                else:
                    current_trie.children[submodule] = Node(
                        submodule, terminal, {}, current_trie.path + [submodule]
                    )
            current_trie = current_trie.children[submodule]
        return self


def collapse_one_children_modules(modules):
    # generate tree
    trie = Trie()
    modules_split = [module.split(".") for module in modules]
    for module in modules_split:
        trie.add_module(module)
    print(trie.trie.children)

    print(trie.trie.dump())
    print(trie.trie.count_children())
    for terminal in trie.trie.extract_terminals():
        print(terminal)


def collapse_simple(modules):
    current_modules = modules[:]
    modules_split = [tuple(module.split(".")[:-1]) for module in modules]
    classes = [module.split(".")[-1] for module in modules]
    print(modules_split)
    d = dict(zip(modules, modules_split))
    freq_cnt = Counter(modules_split)
    found = False
    print("FREQ", freq_cnt)
    for key, freq in freq_cnt.items():
        if freq == 1:
            print("TO REMOVE", key)
            found = True
            # find every module with this prefix
            for i, module_split in enumerate(modules_split):
                if module_split == key:
                    current_modules[i] = ".".join(
                        list(module_split[: (len(key) - 1)]) + [classes[i]]
                    )
    return current_modules, found


def collapse_simple_repeat(modules):
    while True:
        modules, found = collapse_simple(modules)
        print("here", modules)
        if not found:
            break
    return modules


if __name__ == "__main__":
    """
    This is experimental code aimed at simplifying the package structure that we import
    """
    # this structure should be collapsed to
    # - pyod
    #    - models
    #         - sod
    #           - ClassA
    #           - ClassB
    #         - mcd
    #           - ClassC
    # recursively collapse packages with 1 children class

    collapse_one_children_modules(
        [
            "pyod.models.sod.a.ClassA",
            "pyod.models.sod.a.ClassB",
            "pyod.models.mcd.ClassC",
        ]
    )
    modules = [
        "pyod.models.sod.ClassA",
        "pyod.models.sod.ClassB",
        "pyod.models.mcd.ClassC",
    ]
    for orig_module, collapsed_module in zip(modules, collapse_simple_repeat(modules)):
        print(orig_module, collapsed_module)
