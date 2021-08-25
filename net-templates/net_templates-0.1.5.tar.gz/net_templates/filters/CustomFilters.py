from net_models.models import models_map
from net_models.models.BaseModels import BaseNetModel
from pydantic.typing import Union, Dict, List, Literal
from net_templates.filters import BaseFilter


class CustomFilters(BaseFilter):

    def to_model(self, data: Union[Dict, List], model: str, many=True, serialize=True, dict_params=None) -> Union[dict, list]:
        model_data = None
        model_class: BaseNetModel = models_map.get(model)
        if model_class is None:
            msg = f"Unknown model: '{model}'. Current models are: '{models_map}'."
            self.logger.error(msg=msg)
            raise ValueError(msg)
        if many is False:
            if isinstance(data, dict):
                if serialize:
                    if dict_params is not None:
                        model_data = model_class.parse_obj(data).serial_dict(**dict_params)
                    else:
                        model_data = model_class.parse_obj(data).serial_dict()
                else:
                    model_data = model_class.parse_obj(data)
            else:
                msg = f"Got unexpected type of data. Expected dict, got {type(data)}."
                self.logger.error(msg=msg)
                raise TypeError(msg)

        elif many is True:
            if isinstance(data, list):
                if serialize:
                    if dict_params is not None:
                        model_data = [model_class.parse_obj(x).serial_dict(**dict_params) for x in data]
                    else:
                        model_data = [model_class.parse_obj(x).serial_dict() for x in data]
                else:
                    model_data = [model_class.parse_obj(x) for x in data]
            else:
                msg = f"Got unexpected type of data. Expected list, got {type(data)}."
                self.logger.error(msg=msg)
                raise TypeError(msg)
        return model_data

    def validate_data(self, data: Union[dict, list], model: str, many=False) -> bool:
        try:
            model_data = self.to_model(data=data, model=model, many=many, serialize=False)
        except Exception as e:
            msg = f"Got Exception while validating data with model 'model'. Exception: {repr(e)}."
            self.logger.error(msg=msg)
            return False
        if model_data is None:
            return False
        elif isinstance(model_data, BaseNetModel):
            return True
        elif isinstance(model_data, list):
            if all([isinstance(x, BaseNetModel) for x in model_data]):
                return True
            else:
                return False
        else:
            msg = f"Unexpected type - 'model_data' is {type(model_data)}. {model_data}"
            raise TypeError(msg)



    def to_vlan_range(self, vlans: Union[List[int], Literal["none", "all"]]) -> str:

        if isinstance(vlans, str):
            if vlans == "none":
                return "none"
            elif vlans == "all":
                return "all"
            else:
                raise ValueError(f"Invalid string value: {vlans}")
        min_diff = 1
        # Assume vlans is List[int]
        vlans = sorted(list(set(vlans)))
        parts = []
        current_entry = [None, None]
        for vlan in vlans:
            if current_entry[0] is None:
                current_entry[0] = vlan
            elif current_entry[1] is None:
                if current_entry[0] + 1 == vlan:
                    current_entry[1] = vlan
                else:
                    # Flush
                    parts.append(str(current_entry[0]))
                    current_entry = [vlan, None]
            else:
                if current_entry[1] + 1 == vlan:
                    current_entry[1] = vlan
                else:
                    # Flush
                    if (current_entry[1] - current_entry[0]) > min_diff:
                        parts.append(f"{current_entry[0]}-{current_entry[1]}")
                    else:
                        parts.extend(map(str, current_entry))
                    current_entry = [vlan, None]
        # Flush remainder
        if not any(current_entry):
            pass
        elif all(current_entry):
            if (current_entry[1] - current_entry[0]) > min_diff:
                parts.append(f"{current_entry[0]}-{current_entry[1]}")
            else:
                parts.extend(map(str, current_entry))
                current_entry = [None, None]
        else:
            parts.append(str(current_entry[0]))
        vlan_range = ",".join(parts)
        if vlan_range == "":
            return "none"
        elif vlan_range == "1-4094":
            return "all"

        return vlan_range

    def str_to_obj(self, string: str):
        return eval(string)