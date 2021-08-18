from cirs_063 import CIRS_063

def main_cirs063_wad(dcm=None, manual_input=None,\
                    action_name=None, action_params=None):    
    
    if action_name != 'AnalyseCIRS063':
        raise RuntimeError('I can only analyse CIRS 063 phantom!')

    cirs_analysis = CIRS_063.CIRS_063_analyser(dcm)

    return cirs_analysis.WAD_output
    
    
if __name__ == '__main__':
    pass