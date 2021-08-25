import os
import json
import ipywidgets as widgets
from traitlets import Unicode, List, Tuple, Bool
from pandas.core.frame import DataFrame
from pandas.io.json import build_table_schema
from fathom_lib.workflow import run_workflow, validate_pipeline_fake_data
import warnings

warnings.filterwarnings("ignore")
# See js/lib/plugin.js for the frontend counterpart to this file.

temp_dir = ".\.ipynb_checkpoints"

@widgets.register
class NodeEditorWidget(widgets.DOMWidget):

    _model_name = Unicode('NodeEditorModel').tag(sync=True)
    _model_module = Unicode("ailab-lite").tag(sync=True)
    _model_module_version = Unicode("^0.1.0").tag(sync=True)
    _view_name = Unicode('NodeEditorView').tag(sync=True)
    _view_module = Unicode("ailab-lite").tag(sync=True)
    _view_module_version = Unicode("^0.1.0").tag(sync=True)

    notebook_name = Unicode().tag(sync=True)
    datasets = List().tag(sync=True)
    workflow_definition = Unicode().tag(sync=True)
    validating = Bool().tag(sync=True)
    running = Bool().tag(sync=True)
    saving = Bool().tag(sync=True)
    validation_log = Unicode().tag(sync=True)
    running_log = Unicode().tag(sync=True)

    def __init__(self, **kwargs):
        def schema(n, df):
            # save df to temp directory
            df.to_csv("{}\{}.csv".format(temp_dir, n))
            return {
                "name": n,
                "schema_json": json.dumps(
                    build_table_schema(df, index=False, version=False), allow_nan=False
                )
            }
        def validate_change(change):
            if change.new:
                self.validation_log = ""
                workflow_definition = json.loads(self.workflow_definition)
                try:
                    return_dict = validate_pipeline_fake_data(workflow_definition)
                except Exception as e:
                    print("\033[91m Error {}".format(e))   
                self.validation_log = json.dumps(return_dict)
                self.validating = False

        def run_change(change):
            if change.new:
                data_source_name = ""                
                workflow_definition = json.loads(self.workflow_definition)
                for node in workflow_definition["nodes"]:
                    if workflow_definition["nodes"][node]["name"] == "DataFrame":
                        data_source_name = workflow_definition["nodes"][node]["file_name"]
                logger = "PythonLogger"
                if data_source_name:
                    try:
                        run_workflow(graph_details=workflow_definition, data_source="{}\{}.csv".format(temp_dir, data_source_name), logger_name=logger)
                    except Exception as e:
                        print("\033[91m Error {}".format(e))
                    finally:
                        self.running = False
                else:
                    print("Data source missing")
                self.running = False

        def run_save(change):
            if change.new:
                with open("{}\{}.json".format(temp_dir, self.notebook_name), "w") as f:
                    f.write(self.workflow_definition)
                self.saving = False

        def notebook_name_change(change):
            if change.new:
                if os.path.exists("{}\{}.json".format(temp_dir, self.notebook_name)):
                    with open("{}\{}.json".format(temp_dir, self.notebook_name), "r") as f:
                        self.workflow_definition = f.read()

        env = kwargs.pop("env")
        x = [(n, v) for n, v in env.items() if isinstance(v, DataFrame)]
        datasets = [schema(n, df) for n, df in x]
        kwargs["datasets"] = datasets
        super().__init__(**kwargs)
        

        self.observe(validate_change, "validating")
        self.observe(run_change, "running")
        self.observe(run_save, "saving")
        self.observe(notebook_name_change, "notebook_name")
