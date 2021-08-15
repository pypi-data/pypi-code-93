from mitosheet.step_performers.import_steps.simple_import import SimpleImportStepPerformer
from mitosheet.saved_analyses import read_and_upgrade_analysis

def get_import_summary(event):
    """
    Handle import summary is a route that, given the name of an analysis, will
    return the parameters to import steps over the course of the analysis. 

    The data we return is in the format:
    {
        "1": ["file123.csv"], 
        "3": ["file12356.csv"]
    }
    which is a mapping from _step index_ to the files that they import.
    """
    analysis_name = event['analysis_name']
    analysis = read_and_upgrade_analysis(analysis_name)

    imports_only = dict()
    if analysis is not None:
        for step_idx, step_data in enumerate(analysis['steps_data']):
            if step_data['step_type'] == SimpleImportStepPerformer.step_type():
                # NOTE: we make the step indexes strings because JSON insists that
                # all keys are strings anyways
                imports_only[str(step_idx)] = step_data['params']['file_names']

    return imports_only