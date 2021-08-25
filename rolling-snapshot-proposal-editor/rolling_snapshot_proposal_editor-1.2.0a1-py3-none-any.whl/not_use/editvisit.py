class EditVisit:
    """
    This class handles editing visits.
    #####
    Usage:
    ???
    #####
    Ref:
    ???
    """
    def __init__(self,propfile,verbal=True,templatekey='fixed_target',read_propfile=True,read_templatefile=True):
        import rolling_snapshot_proposal_editor as RNPE
        from rolling_snapshot_proposal_editor.templatehandler import TemplateHandler
        self.propfile = propfile
        self.verbal = verbal
        self.templatekey = templatekey
#         self.templatefile = TemplateHandler().read(templatekey=self.templatekey)
#         if read_propfile: 
#             self.prop = self._read_propfile()
#             if self.verbal: print('Access by self.prop. \n')
        if read_templatefile: 
            self.template = self._read_templatefile()
            if self.verbal: print('Access by self.template. \n')
#     def _read_propfile(self):
#         if self.verbal: print('Read propfile.\n')
#         f = open(self.propfile,'r')
#         t = f.readlines()
#         f.close()
#         return t
    def _read_templatefile(self):
        from rolling_snapshot_proposal_editor.templatehandler import TemplateHandler
        TemplateHandler
#         import json
#         if self.verbal: print('Read templatefile.\n')
#         f = open(self.templatefile,'r')
#         t = json.loads(f.readlines()[0])
#         f.close()
        return t
        
# def add_fixed_target(propfile,targetinfo,outname,line_index=None):
#     ##### propfile = path to .prop file to be edited. This file will be open, but will not be changed; changes will be implemented and saved to a new file specified by outname.
#     ##### targetinfo = a template dict of what information to be written.
#     ########## for updating fixed targets, use fixed_target.json for the dict template.
#     ##### outname = path to write the updated .prop file.
#     ##### line_index = 1-indexing of the previous fixed target's last line (i.e., Comments: ...). If None, the code will automatically search for the last line.
#     if not line_index:
#         print('Finding line_index ...\n')
#         line_index = _find_lastline(targetinfo,propfile)
#         print(line_index)
#     #####
#     print('Grabbing the original file ...\n')
#     f = open(propfile,'r')
#     t0 = f.readlines()
#     t1 = t0[:line_index]
#     t3 = t0[line_index:]
#     f.close()
#     #####
#     print('Creating {0} ...\n'.format(outname))
#     f = open(outname,'w')
#     f.writelines(t1)
#     f.writelines('\n')
#     for i in targetinfo:
#         t = targetinfo[i] + '\n'
#         f.writelines(t)
#     f.writelines(t3)
#     f.close()   
#     #####
#     print('Finish ...\n')

# def _find_lastline(template_dict,propfile):
#     ##### Internally used
#     keys = list(template_dict.keys())
#     N = len(keys)
#     #####
#     target_lastline = None
#     f = open(propfile,'r')
#     t = f.readlines()
#     for ii,i in enumerate(t):
#         tt = i.split()
#         try:
#             if tt[0]=='{0}:'.format(keys[0]):
#                 target_lastline = ii+N # 1-indexing
#         except:
#             pass
#     f.close()
#     return target_lastline
            
# def prepare_targetinfo(spreadsheet,read_spreadsheet_csv,targetnumber,json_template):
#     ##### spreadsheet = google spreadsheet in csv format
#     ##### targetnumber = a string of target number from the spreadsheet of the object to be prepared.
#     ##### json_templat = e.g., fixed_target.json
#     import pandas as pd
#     import json
#     from astropy import units as u
#     from astropy.coordinates import SkyCoord
#     if read_spreadsheet_csv:
#         print('Read spreadsheet {0} ...\n'.format(spreadsheet))
#         t0 = pd.read_csv(spreadsheet)
#     else:
#         t0 = spreadsheet
#     #####
#     print('Grabbing target number {0} ...\n'.format(targetnumber))
#     t = t0[t0['Target Number']==targetnumber]
#     targetname = t['Name'].to_list()[0]
#     ra,dec = float(t['RA'].to_list()[0]),float(t['Dec'].to_list()[0])
#     mag = t['Obs. Mag'].to_list()[0]
#     targettype = t['Type'].to_list()[0]
#     #####
#     print('Preparing RADEC string ...\n')
#     c = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')
#     t = c.to_string('hmsdms')
#     ra_str,dec_str = t.split(' ')
#     ra_str,dec_str = ra_str.upper(),dec_str.upper()
#     dec_str = "\'".join(dec_str.split('M'))
#     dec_str = '\"'.join(dec_str.split('S'))
#     #####
#     print('Finalizing ...\n')
#     f = open(json_template,'r')
#     targetinfo = json.loads(f.readlines()[0])
#     f.close()
#     targetinfo['Target_Number'] += targetnumber
#     targetinfo['Target_Name'] += targetname
#     if targettype == 'TDE':
#         targetinfo['Description'] += 'EXT-STAR, TIDAL TAIL'
#     elif targettype == 'SN Ia':
#         targetinfo['Description'] += 'EXT-STAR, SUPERNOVA TYPE IA'
#     elif targettype == 'SN IIb':
#         targetinfo['Description'] += 'EXT-STAR, SUPERNOVA TYPE II'
#     targetinfo['Extended'] += 'NO'
#     targetinfo['Position'] += "RA={0} +/- 1\", DEC={1} +/- 1\"".format(ra_str,dec_str)
#     targetinfo['Equinox'] += 'J2000'
#     targetinfo['Reference_Frame'] += 'ICRS'
#     targetinfo['Flux'] += 'V = {0}'.format(mag)
#     #####
#     print('Return targetinfo ...\n')
#     return targetinfo
        
        
#         self.scopes = scopes
#         self.sheetid = sheetid
#         self.rangename = rangename
#         self.credential = credential
#         self.verbal = verbal
#         if self.verbal: print('Use self.read() to read the sheet.\n')
#     ####################
#     ####################
#     ####################
#     # from https://developers.google.com/sheets/api/quickstart/python    
#     def read(self):
#         import os.path
#         from googleapiclient.discovery import build
#         from google_auth_oauthlib.flow import InstalledAppFlow
#         from google.auth.transport.requests import Request
#         from google.oauth2.credentials import Credentials
#         import pandas as pd
#         #####
#         creds = None
#         # The file token.json stores the user's access and refresh tokens, and is
#         # created automatically when the authorization flow completes for the first
#         # time.
#         if os.path.exists('token.json'):
#             creds = Credentials.from_authorized_user_file('token.json', self.scopes)
#         # If there are no (valid) credentials available, let the user log in.
#         if not creds or not creds.valid:
#             if creds and creds.expired and creds.refresh_token:
#                 creds.refresh(Request())
#             else:
#                 flow = InstalledAppFlow.from_client_secrets_file(
#                     self.credential,self.scopes)
#                 creds = flow.run_local_server(port=0)
#             # Save the credentials for the next run
#             with open('token.json', 'w') as token:
#                 token.write(creds.to_json())

#         service = build('sheets', 'v4', credentials=creds)

#         # Call the Sheets API
#         sheet = service.spreadsheets()
#         result = sheet.values().get(spreadsheetId=self.sheetid,
#                                     range=self.rangename).execute()
#         values = result.get('values', [])

#         ##### organize in pandas
#         df = pd.DataFrame(values)
#         df.columns = df.iloc[0]
#         df.drop(df.index[0],inplace=True)
#         self.df = df
#         if self.verbal: print('Access the sheet by self.df ...\n')
#     ####################
#     ####################
#     ####################
    