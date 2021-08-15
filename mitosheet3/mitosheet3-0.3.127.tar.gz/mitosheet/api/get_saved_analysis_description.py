from mitosheet.saved_analyses import read_and_upgrade_analysis
from mitosheet.step_performers import STEP_TYPE_TO_STEP_PERFORMER
import json


def get_saved_analysis_description(event, steps_manager):
    """
    Gets the description of the steps in the saved analysis, and sends
    it back to the frontend

    Sends '' if its unable to read in for any reason (or this analysis does)
    not exist.
    """
    analysis_name = event['analysis_name']
    analysis_steps = read_and_upgrade_analysis(analysis_name)
    
    try:
        if analysis_steps is None:
            return ''
        
        analysis_descriptions = []
        for step_data in analysis_steps['steps_data']:
            step_performer = STEP_TYPE_TO_STEP_PERFORMER[step_data['step_type']]

            # Generate the step description
            step_description = step_performer.describe(
                **step_data['params']
            )

            analysis_descriptions.append({
                'step_type': step_data['step_type'],
                'step_description': step_description
            })

        return json.dumps(analysis_descriptions)
        
    except Exception as e:
        # As not being able to get the steps is not a critical failure, 
        # we return empty data if its not possible.
        return ''