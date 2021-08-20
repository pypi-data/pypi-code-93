from dataclasses import dataclass
@dataclass
class OptimizationNotebookConfig:
    notebook_folder: str
    notebook_name: str
    input_parameters: dict
    output_parameters: list
    input_artefacts: dict
    output_artefacts: dict

    def __str__(self):
        return "notebook_folder: %s\n" \
               "notebook_name: %s\n" \
               "input_parameters: %s\n" \
               "output_parameters: %s\n" \
               "input_artefacts: %s\n" \
               "output_artefacts: %s" % (self.notebook_folder,
                                         self.notebook_name,
                                         self.input_parameters,
                                         self.output_parameters,
                                         self.input_artefacts,
                                         self.output_artefacts)
