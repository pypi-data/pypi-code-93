import json5 as json

class InputProcessor(object):
    """WDL流程输入数据处理工具。支持解析、更新、格式化"""

    META_NAME = "workflow_name"
    META_INPUT = "input"
    META_CALL  = "call"

    def __init__(self, filepath: str, indent=2) -> None:
        self.filepath = filepath
        self.indent = indent

        self.meta = {
            self.META_NAME: None,
            self.META_INPUT: {},
            self.META_CALL: {}
        }
        with open(self.filepath) as r:
            self.raw_inputs: dict = json.load(r)
        self._parse()

    def _parse(self):
        input_maps = {}
        for key, value in self.raw_inputs.items():
            sub = key.split('.')

            tmp = input_maps
            for k in sub[:-1]:
                if k not in tmp:
                    tmp[k] = {}
                tmp = tmp[k]

            tmp[sub[-1]] = value

        # 1. 顶层必须只能有一个名字： 只能有一个workflow
        top_levels = list(input_maps.keys())
        if len(top_levels) != 1:
            raise RuntimeError(f"输入数据中WORKFLOW名称不一致，{top_levels}")
        self.meta[self.META_NAME] = top_levels[0]

        # 解析call和inputs
        for key, value in input_maps[top_levels[0]].items():
            # TODO： @2021年3月22日 这里假设字典类型的数据实际指的是下一层调用。但数据本身是否可以是字典类型呢？

            if isinstance(value, dict):
                self.meta[self.META_CALL][key] = value
            else:
                self.meta[self.META_INPUT][key] = value

    @property
    def workflow_name(self):
        return self.meta[self.META_NAME]

    @property
    def inputs(self) -> dict:
        return self.meta[self.META_INPUT]

    @property
    def calls(self) -> list:
        return list(self.meta[self.META_CALL].keys())

    def call_input(self, call_name: str) -> dict:
        return self.meta[self.META_CALL].get(call_name, {})

    # 根据meta数据重新生成input
    def __str__(self) -> str:
        wf = self.workflow_name

        out = {}
        for k,v in self.inputs.items():
            out[f"{wf}.{k}"] = v

        for call_task in self.calls:
            for k, v in self.call_input(call_task).items():
                out[f'{wf}.{call_task}.{k}'] = v

        return json.dumps(out, indent=self.indent, quote_keys=True, trailing_commas=False)

    def update_input(self, key: str, value=None):
        """更新指定key对应的数据，若不提供第二个参数，则删除对应的key

        Args:
            key (str): 待更新或删除的key
            value(any): 当设置为None时，删除key，否则更新key
        """
        if value is None:
            if key in self.meta[self.META_INPUT]:
                del self.meta[self.META_INPUT][key]
        else:
            self.meta[self.META_INPUT][key] = value

    def update_task_input(self, call_name: str, key: str, value=None):
        # 1. 删除key
        if value is None:
            if key in self.meta[self.META_CALL][call_name]:
                del self.meta[self.META_CALL][call_name][key]
        # 2. 更新key
        else:
            self.meta[self.META_CALL][call_name][key] = value
