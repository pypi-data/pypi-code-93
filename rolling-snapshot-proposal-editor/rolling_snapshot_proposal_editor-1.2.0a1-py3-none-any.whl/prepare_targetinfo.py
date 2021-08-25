def prepare_targetinfo(spreadsheet,read_spreadsheet_csv,targetnumber,json_template):
    from rolling_snapshot_proposal_editor.prepare_targetinfo import _list_tde
    from rolling_snapshot_proposal_editor.prepare_targetinfo import _list_sn_noclass
    from rolling_snapshot_proposal_editor.prepare_targetinfo import _list_sn_ia
    from rolling_snapshot_proposal_editor.prepare_targetinfo import _list_sn_ib
    from rolling_snapshot_proposal_editor.prepare_targetinfo import _list_sn_ii
    ##### spreadsheet = google spreadsheet in csv format
    ##### targetnumber = a string of target number from the spreadsheet of the object to be prepared.
    ##### json_templat = e.g., fixed_target.json
    import pandas as pd
    import json
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    if read_spreadsheet_csv:
        print('Read spreadsheet {0} ...\n'.format(spreadsheet))
        t0 = pd.read_csv(spreadsheet)
    else:
        t0 = spreadsheet
    #####
    print('Grabbing target number {0} ...\n'.format(targetnumber))
    t = t0[t0['Target Number']==targetnumber]
    targetname = t['Name'].to_list()[0]
    ra,dec = float(t['RA'].to_list()[0]),float(t['Dec'].to_list()[0])
    mag = t['Obs. Mag'].to_list()[0]
    targettype = t['Type'].to_list()[0]
    #####
    print('Preparing RADEC string ...\n')
    c = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')
    t = c.to_string('hmsdms')
    ra_str,dec_str = t.split(' ')
    ra_str,dec_str = ra_str.upper(),dec_str.upper()
    dec_str = "\'".join(dec_str.split('M'))
    dec_str = '\"'.join(dec_str.split('S'))
    #####
    print('Finalizing ...\n')
    f = open(json_template,'r')
    targetinfo = json.loads(f.readlines()[0])
    f.close()
    targetinfo['Target_Number'] += str(targetnumber)
    targetinfo['Target_Name'] += targetname
    if targettype in _list_tde():
        targetinfo['Description'] += 'EXT-STAR, TIDAL TAIL'
    elif targettype in _list_sn_noclass():
        targetinfo['Description'] += 'EXT-STAR, SUPERNOVA'
    elif targettype in _list_sn_ia():
        targetinfo['Description'] += 'EXT-STAR, SUPERNOVA TYPE IA'
    elif targettype in _list_sn_ib():
        targetinfo['Description'] += 'EXT-STAR, SUPERNOVA TYPE IB'
    elif targettype in _list_sn_ii():
        targetinfo['Description'] += 'EXT-STAR, SUPERNOVA TYPE II'
    targetinfo['Extended'] += 'NO'
    targetinfo['Position'] += "RA={0} +/- 1\", DEC={1} +/- 1\"".format(ra_str,dec_str)
    targetinfo['Equinox'] += 'J2000'
    targetinfo['Reference_Frame'] += 'ICRS'
    targetinfo['Flux'] += 'V = {0}'.format(mag)
    #####
    print('Return targetinfo ...\n')
    return targetinfo
def _list_tde():
    thelist = {'TDE'}
    return thelist
def _list_sn_noclass():
    thelist = {'SN'}
    return thelist
def _list_sn_ia():
    thelist = {'SN Ia'}
    return thelist
def _list_sn_ib():
    thelist = {'SN Ib'}
    return thelist
def _list_sn_ii():
    thelist = {'SN II', 'SN IIb'}
    return thelist
