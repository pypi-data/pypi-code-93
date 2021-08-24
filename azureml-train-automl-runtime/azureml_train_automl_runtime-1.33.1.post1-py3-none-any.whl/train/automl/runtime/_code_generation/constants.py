# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Code generation related constants."""


class CodeGenConstants:
    TagName = "_aml_system_codegen"
    ScriptFilename = "script.py"
    ScriptRunNotebookFilename = "script_run_notebook.ipynb"
    OutputPath = "outputs/generated_code/"
    ScriptOutputPath = OutputPath + ScriptFilename
    ScriptRunNotebookOutputPath = OutputPath + ScriptRunNotebookFilename
