class TemplateHandler:
    """
    This class handles template files.
    localpath = '/path/to/template/folder/'. If None, this will be the package folder.
    verbal = True if a user wants messages.
    #####
    Usage:
    1: Initialization -- t = TemplateHandler()
    2: Check available template files -- self.templatedict
    3: Read a template file -- t = self.read(templatekey='fixed_target') for example
    """
    def __init__(self,localpath=None,verbal=True):
        import rolling_snapshot_proposal_editor as RNPE
        self.verbal = verbal
        self.localpath_template = localpath if localpath else RNPE.__path__[0] + '/template/'
        self.localpath_demo = localpath if localpath else RNPE.__path__[0] + '/demo/'
        self.templatedict = {'fixed_target':self.localpath_template + 'fixed_target.json',
                             'visits':self.localpath_template + 'visits.json',
                             'exposure':self.localpath_template + 'exposure.json',
                             'visits_G280':self.localpath_template + 'visits_G280.json',
                             'demo_notebook':self.localpath_demo + 'demo_1.1.0.ipynb',
                             'demo_propfile':self.localpath_demo + 'propfile.prop',
                             'demo_sheet':self.localpath_demo + 'sheet.csv'
                            }
        if self.verbal: print("""Use self.templatedict to see available template files. Use, e.g., self.read(templatefile='fixed_target.json') to read.\n""")
    def read(self,templatekey,verbal=True):
        ##### templatekey = e.g., 'fixed_target'
        import json
        t = self.templatedict[templatekey]
        if self.verbal: print('Read {0}.\n'.format(t))
        f = open(t,'r')
        t = json.loads(f.readlines()[0])
        f.close()
        return t
