class NBAGamesSimulator():
  def __init__(self, pg_name, pg_minutes, pg_year, sg_name, sg_minutes, sg_year, sf_name, sf_minutes, sf_year, pf_name, pf_minutes, pf_year, c_name, c_minutes, c_year, sxth_name, sxth_minutes, sxth_year, sxth_pos, r1_name, r1_minutes, r1_year, r1_pos, r2_name, r2_minutes, r2_year, r2_pos, r3_name, r3_minutes, r3_year, r3_pos, r4_name, r4_minutes, r4_year, r4_pos, r5_name, r5_minutes, r5_year, r5_pos, r6_name, r6_minutes, r6_year, r6_pos, opp_pg_name, opp_pg_minutes, opp_pg_year, opp_sg_name, opp_sg_minutes, opp_sg_year, opp_sf_name, opp_sf_minutes, opp_sf_year, opp_pf_name, opp_pf_minutes, opp_pf_year, opp_c_name, opp_c_minutes, opp_c_year, opp_sxth_name, opp_sxth_minutes, opp_sxth_year, opp_sxth_pos, opp_r1_name, opp_r1_minutes, opp_r1_year, opp_r1_pos, opp_r2_name, opp_r2_minutes, opp_r2_year, opp_r2_pos, opp_r3_name, opp_r3_minutes, opp_r3_year, opp_r3_pos, opp_r4_name, opp_r4_minutes, opp_r4_year, opp_r4_pos, opp_r5_name, opp_r5_minutes, opp_r5_year, opp_r5_pos, opp_r6_name, opp_r6_minutes, opp_r6_year, opp_r6_pos):
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from sklearn.neural_network import MLPRegressor
    import warnings
    self.df  = pd.read_csv('https://github.com/tarsur909/SF_NBA/blob/main/data/final_player_tables.csv?raw=true')
    #pg
    self.pg_name = pg_name
    self.pg_minutes = pg_minutes
    self.pg_year = pg_year
    pg_pos = 'PG'
    self.pg_pos = pg_pos
    pg_df1 = self.df[self.df.Pos == 'PG']
    pg_df2 = self.df[self.df.Pos == 'SG-PG']
    pg_df3 = self.df[self.df.Pos == 'SF-PG']
    pg_df4 = self.df[self.df.Pos == 'G']
    pg_df = pd.concat([pg_df1, pg_df2, pg_df3, pg_df4])
    self.pg_df = pg_df[pg_df.Player == self.pg_name]
    #sg
    self.sg_name = sg_name
    self.sg_minutes = sg_minutes
    self.sg_year = sg_year
    sg_pos = 'SG'
    self.sg_pos = sg_pos
    sg_df1 = self.df[self.df.Pos == 'SG']
    sg_df2 = self.df[self.df.Pos == 'SG-PG']
    sg_df3 = self.df[self.df.Pos == 'SF-SG']
    sg_df4 = self.df[self.df.Pos == 'G']
    sg_df = pd.concat([sg_df1, sg_df2, sg_df3, sg_df4])
    self.sg_df = sg_df[sg_df.Player == self.sg_name]
    #sf
    self.sf_name = sf_name
    self.sf_minutes = sf_minutes
    self.sf_year = sf_year
    sf_pos = 'SF'
    self.sf_pos = sf_pos
    sf_df1 = self.df[self.df.Pos == 'SF']
    sf_df2 = self.df[self.df.Pos == 'SF-SG']
    sf_df3 = self.df[self.df.Pos == 'SF-PG']
    sf_df4 = self.df[self.df.Pos == 'F']
    sf_df5 = self.df[self.df.Pos == 'PF-SF']
    sf_df6 = self.df[self.df.Pos == 'C-SF']
    sf_df7 = self.df[self.df.Pos == 'C-F']
    sf_df = pd.concat([sf_df1, sf_df2, sf_df3, sf_df4, sf_df5, sf_df6, sf_df7])
    self.sf_df = sf_df[sf_df.Player == self.sf_name]
    #pf
    self.pf_name = pf_name
    self.pf_minutes = pf_minutes
    self.pf_year = pf_year
    pf_pos = 'PF'
    self.pf_pos = pf_pos
    pf_df1 = self.df[self.df.Pos == 'PF']
    pf_df2 = self.df[self.df.Pos == 'F']
    pf_df3 = self.df[self.df.Pos == 'PF-C']
    pf_df4 = self.df[self.df.Pos == 'C-PF']
    pf_df5 = self.df[self.df.Pos == 'C-F']
    pf_df6 = self.df[self.df.Pos == 'PF-SF']
    pf_df = pd.concat([pf_df1, pf_df2, pf_df3, pf_df4, pf_df5, pf_df6])
    self.pf_df = pf_df[pf_df.Player == self.pf_name]
    #c
    self.c_name = c_name
    self.c_minutes = c_minutes
    self.c_year = c_year
    c_pos = 'C'
    self.c_pos = c_pos
    c_df1 = self.df[self.df.Pos == 'C']
    c_df2 = self.df[self.df.Pos == 'C-F']
    c_df3 = self.df[self.df.Pos == 'PF-C']
    c_df4 = self.df[self.df.Pos == 'C-PF']
    c_df5 = self.df[self.df.Pos == 'C-SF']
    c_df = pd.concat([c_df1, c_df2, c_df3, c_df4, c_df5])
    self.c_df = c_df[c_df.Player == self.c_name]
    #6th man
    self.sxth_name = sxth_name
    self.sxth_minutes = sxth_minutes
    self.sxth_year = sxth_year
    self.sxth_pos = sxth_pos
    if sxth_pos == 'PG':
      sxth_df = pg_df
      self.sxth_df = sxth_df[sxth_df.Player == self.sxth_name]
    elif sxth_pos == 'SG':
      sxth_df = sg_df
      self.sxth_df = sxth_df[sxth_df.Player == self.sxth_name]
    elif sxth_pos == 'SF':
      sxth_df = sf_df
      self.sxth_df = sxth_df[sxth_df.Player == self.sxth_name]
    elif sxth_pos == 'PF':
      sxth_df = pf_df
      self.sxth_df = sxth_df[sxth_df.Player == self.sxth_name]
    elif sxth_pos == 'C':
      sxth_df = c_df
      self.sxth_df = sxth_df[sxth_df.Player == self.sxth_name]
    #r1
    self.r1_name = r1_name
    self.r1_minutes = r1_minutes
    self.r1_year = r1_year
    self.r1_pos = r1_pos
    if r1_pos == 'PG':
      r1_df = pg_df
      self.r1_df = r1_df[r1_df.Player == self.r1_name]
    elif r1_pos == 'SG':
      r1_df = sg_df
      self.r1_df = r1_df[r1_df.Player == self.r1_name]
    elif r1_pos == 'SF':
      r1_df = sf_df
      self.r1_df = r1_df[r1_df.Player == self.r1_name]
    elif r1_pos == 'PF':
      r1_df = pf_df
      self.r1_df = r1_df[r1_df.Player == self.r1_name]
    elif r1_pos == 'C':
      r1_df = c_df
      self.r1_df = r1_df[r1_df.Player == self.r1_name]
    #r2
    self.r2_name = r2_name
    self.r2_minutes = r2_minutes
    self.r2_year = r2_year
    self.r2_pos = r2_pos
    if r2_pos == 'PG':
      r2_df = pg_df
      self.r2_df = r2_df[r2_df.Player == self.r2_name]
    elif r2_pos == 'SG':
      r2_df = sg_df
      self.r2_df = r2_df[r2_df.Player == self.r2_name]
    elif r2_pos == 'SF':
      r2_df = sf_df
      self.r2_df = r2_df[r2_df.Player == self.r2_name]
    elif r2_pos == 'PF':
      r2_df = pf_df
      self.r2_df = r2_df[r2_df.Player == self.r2_name]
    elif r2_pos == 'C':
      r2_df = c_df
      self.r2_df = r2_df[r2_df.Player == self.r2_name]
     #r3
    self.r3_name = r3_name
    self.r3_minutes = r3_minutes
    self.r3_year = r3_year
    self.r3_pos = r3_pos
    if r3_pos == 'PG':
      r3_df = pg_df
      self.r3_df = r3_df[r3_df.Player == self.r3_name]
    elif r3_pos == 'SG':
      r3_df = sg_df
      self.r3_df = r3_df[r3_df.Player == self.r3_name]
    elif r3_pos == 'SF':
      r3_df = sf_df
      self.r3_df = r3_df[r3_df.Player == self.r3_name]
    elif r3_pos == 'PF':
      r3_df = pf_df
      self.r3_df = r3_df[r3_df.Player == self.r3_name]
    elif r3_pos == 'C':
      r3_df = c_df
      self.r3_df = r3_df[r3_df.Player == self.r3_name]
    #r4
    self.r4_name = r4_name
    self.r4_minutes = r4_minutes
    self.r4_year = r4_year
    self.r4_pos = r4_pos
    if r4_pos == 'PG':
      r4_df = pg_df
      self.r4_df = r4_df[r4_df.Player == self.r4_name]
    elif r4_pos == 'SG':
      r4_df = sg_df
      self.r4_df = r4_df[r4_df.Player == self.r4_name]
    elif r4_pos == 'SF':
      r4_df = sf_df
      self.r4_df = r4_df[r4_df.Player == self.r4_name]
    elif r4_pos == 'PF':
      r4_df = pf_df
      self.r4_df = r4_df[r4_df.Player == self.r4_name]
    elif r4_pos == 'C':
      r4_df = c_df
      self.r4_df = r4_df[r4_df.Player == self.r4_name]
    #r5
    self.r5_name = r5_name
    self.r5_minutes = r5_minutes
    self.r5_year = r5_year
    self.r5_pos = r5_pos
    if r5_pos == 'PG':
      r5_df = pg_df
      self.r5_df = r5_df[r5_df.Player == self.r5_name]
    elif r5_pos == 'SG':
      r5_df = sg_df
      self.r5_df = r5_df[r5_df.Player == self.r5_name]
    elif r5_pos == 'SF':
      r5_df = sf_df
      self.r5_df = r5_df[r5_df.Player == self.r5_name]
    elif r5_pos == 'PF':
      r5_df = pf_df
      self.r5_df = r5_df[r5_df.Player == self.r5_name]
    elif r5_pos == 'C':
      r5_df = c_df
      self.r5_df = r5_df[r5_df.Player == self.r5_name]
    #r6
    self.r6_name = r6_name
    self.r6_minutes = r6_minutes
    self.r6_year = r6_year
    self.r6_pos = r6_pos
    if r6_pos == 'PG':
      r6_df = pg_df
      self.r6_df = r6_df[r6_df.Player == self.r6_name]
    elif r6_pos == 'SG':
      r6_df = sg_df
      self.r6_df = r6_df[r6_df.Player == self.r6_name]
    elif r6_pos == 'SF':
      r6_df = sf_df
      self.r6_df = r6_df[r6_df.Player == self.r6_name]
    elif r6_pos == 'PF':
      r6_df = pf_df
      self.r6_df = r6_df[r6_df.Player == self.r6_name]
    elif r6_pos == 'C':
      r6_df = c_df
      self.r6_df = r6_df[r6_df.Player == self.r6_name]
    postlst = [pg_pos, sg_pos, sf_pos, pf_pos, c_pos, sxth_pos, r1_pos, r2_pos, r3_pos, r4_pos, r5_pos, r6_pos]
    mintlst = [pg_minutes, sg_minutes, sf_minutes, pf_minutes, c_minutes, sxth_minutes, r1_minutes, r2_minutes, r3_minutes, r4_minutes, r5_minutes, r6_minutes]
    pgminlst = []
    sgminlst = []
    sfminlst = []
    pfminlst = []
    cminlst = []
    for x,y in zip(postlst, mintlst):
      if x == 'PG':
        pgminlst.append(y)
      elif x == 'SG':
        sgminlst.append(y)
      elif x == 'SF':
        sfminlst.append(y)
      elif x == 'PF':
        pfminlst.append(y)
      elif x == 'C':
        cminlst.append(y)
    if sum(pgminlst) != 48:
      warnings.warn('Number of minutes must total 48.')
    if sum(sgminlst) != 48:
      warnings.warn('Number of minutes must total 48.')
    if sum(sfminlst) != 48:
      warnings.warn('Number of minutes must total 48.')
    if sum(pfminlst) != 48:
      warnings.warn('Number of minutes must total 48.')
    if sum(cminlst) != 48:
      warnings.warn('Number of minutes must total 48.')
        #opp_pg
    self.opp_pg_name = opp_pg_name
    self.opp_pg_minutes = opp_pg_minutes
    self.opp_pg_year = opp_pg_year
    opp_pg_pos = 'PG'
    self.opp_pg_pos = opp_pg_pos
    opp_pg_df1 = self.df[self.df.Pos == 'PG']
    opp_pg_df2 = self.df[self.df.Pos == 'SG-PG']
    opp_pg_df3 = self.df[self.df.Pos == 'SF-PG']
    opp_pg_df4 = self.df[self.df.Pos == 'G']
    opp_pg_df = pd.concat([opp_pg_df1, opp_pg_df2, opp_pg_df3, opp_pg_df4])
    self.opp_pg_df = opp_pg_df[opp_pg_df.Player == self.opp_pg_name]
    #opp_sg
    self.opp_sg_name = opp_sg_name
    self.opp_sg_minutes = opp_sg_minutes
    self.opp_sg_year = opp_sg_year
    opp_sg_pos = 'SG'
    self.opp_sg_pos = opp_sg_pos
    opp_sg_df1 = self.df[self.df.Pos == 'SG']
    opp_sg_df2 = self.df[self.df.Pos == 'SG-PG']
    opp_sg_df3 = self.df[self.df.Pos == 'SF-SG']
    opp_sg_df4 = self.df[self.df.Pos == 'G']
    opp_sg_df = pd.concat([opp_sg_df1, opp_sg_df2, opp_sg_df3, opp_sg_df4])
    self.opp_sg_df = opp_sg_df[opp_sg_df.Player == self.opp_sg_name]
    #sf
    self.opp_sf_name = opp_sf_name
    self.opp_sf_minutes = opp_sf_minutes
    self.opp_sf_year = opp_sf_year
    opp_sf_pos = 'SF'
    self.opp_sf_pos = opp_sf_pos
    opp_sf_df1 = self.df[self.df.Pos == 'SF']
    opp_sf_df2 = self.df[self.df.Pos == 'SF-SG']
    opp_sf_df3 = self.df[self.df.Pos == 'SF-PG']
    opp_sf_df4 = self.df[self.df.Pos == 'F']
    opp_sf_df5 = self.df[self.df.Pos == 'PF-SF']
    opp_sf_df6 = self.df[self.df.Pos == 'C-SF']
    opp_sf_df7 = self.df[self.df.Pos == 'C-F']
    opp_sf_df = pd.concat([opp_sf_df1, opp_sf_df2, opp_sf_df3, opp_sf_df4, opp_sf_df5, opp_sf_df6, opp_sf_df7])
    self.opp_sf_df = opp_sf_df[opp_sf_df.Player == self.opp_sf_name]
    #opp_pf
    self.opp_pf_name = opp_pf_name
    self.opp_pf_minutes = opp_pf_minutes
    self.opp_pf_year = opp_pf_year
    opp_pf_pos = 'PF'
    self.opp_pf_pos = opp_pf_pos
    opp_pf_df1 = self.df[self.df.Pos == 'PF']
    opp_pf_df2 = self.df[self.df.Pos == 'F']
    opp_pf_df3 = self.df[self.df.Pos == 'PF-C']
    opp_pf_df4 = self.df[self.df.Pos == 'C-PF']
    opp_pf_df5 = self.df[self.df.Pos == 'C-F']
    opp_pf_df6 = self.df[self.df.Pos == 'PF-SF']
    opp_pf_df = pd.concat([opp_pf_df1, opp_pf_df2, opp_pf_df3, opp_pf_df4, opp_pf_df5, opp_pf_df6])
    self.opp_pf_df = opp_pf_df[opp_pf_df.Player == self.opp_pf_name]
    #c
    self.opp_c_name = opp_c_name
    self.opp_c_minutes = opp_c_minutes
    self.opp_c_year = opp_c_year
    opp_c_pos = 'C'
    self.opp_c_pos = opp_c_pos
    opp_c_df1 = self.df[self.df.Pos == 'C']
    opp_c_df2 = self.df[self.df.Pos == 'C-F']
    opp_c_df3 = self.df[self.df.Pos == 'PF-C']
    opp_c_df4 = self.df[self.df.Pos == 'C-PF']
    opp_c_df5 = self.df[self.df.Pos == 'C-SF']
    opp_c_df = pd.concat([opp_c_df1, opp_c_df2, opp_c_df3, opp_c_df4, opp_c_df5])
    self.opp_c_df = opp_c_df[opp_c_df.Player == self.opp_c_name]
    #6th man
    self.opp_sxth_name = opp_sxth_name
    self.opp_sxth_minutes = opp_sxth_minutes
    self.opp_sxth_year = opp_sxth_year
    self.opp_sxth_pos = opp_sxth_pos
    if opp_sxth_pos == 'PG':
      opp_sxth_df = opp_pg_df
      self.opp_sxth_df = opp_sxth_df[opp_sxth_df.Player == self.opp_sxth_name]
    elif opp_sxth_pos == 'SG':
      opp_sxth_df = opp_sg_df
      self.opp_sxth_df = opp_sxth_df[opp_sxth_df.Player == self.opp_sxth_name]
    elif opp_sxth_pos == 'SF':
      opp_sxth_df = opp_sf_df
      self.opp_sxth_df = opp_sxth_df[opp_sxth_df.Player == self.opp_sxth_name]
    elif opp_sxth_pos == 'PF':
      opp_sxth_df = opp_pf_df
      self.opp_sxth_df = opp_sxth_df[opp_sxth_df.Player == self.opp_sxth_name]
    elif opp_sxth_pos == 'C':
      opp_sxth_df = opp_c_df
      self.opp_sxth_df = opp_sxth_df[opp_sxth_df.Player == self.opp_sxth_name]
    #opp_r1
    self.opp_r1_name = opp_r1_name
    self.opp_r1_minutes = opp_r1_minutes
    self.opp_r1_year = opp_r1_year
    self.opp_r1_pos = opp_r1_pos
    if opp_r1_pos == 'PG':
      opp_r1_df = opp_pg_df
      self.opp_r1_df = opp_r1_df[opp_r1_df.Player == self.opp_r1_name]
    elif opp_r1_pos == 'SG':
      opp_r1_df = opp_sg_df
      self.opp_r1_df = opp_r1_df[opp_r1_df.Player == self.opp_r1_name]
    elif opp_r1_pos == 'SF':
      opp_r1_df = opp_sf_df
      self.opp_r1_df = opp_r1_df[opp_r1_df.Player == self.opp_r1_name]
    elif opp_r1_pos == 'PF':
      opp_r1_df = opp_pf_df
      self.opp_r1_df = opp_r1_df[opp_r1_df.Player == self.opp_r1_name]
    elif opp_r1_pos == 'C':
      opp_r1_df = opp_c_df
      self.opp_r1_df = opp_r1_df[opp_r1_df.Player == self.opp_r1_name]
    #opp_r2
    self.opp_r2_name = opp_r2_name
    self.opp_r2_minutes = opp_r2_minutes
    self.opp_r2_year = opp_r2_year
    self.opp_r2_pos = opp_r2_pos
    if opp_r2_pos == 'PG':
      opp_r2_df = opp_pg_df
      self.opp_r2_df = opp_r2_df[opp_r2_df.Player == self.opp_r2_name]
    elif opp_r2_pos == 'SG':
      opp_r2_df = opp_sg_df
      self.opp_r2_df = opp_r2_df[opp_r2_df.Player == self.opp_r2_name]
    elif opp_r2_pos == 'SF':
      opp_r2_df = opp_sf_df
      self.opp_r2_df = opp_r2_df[opp_r2_df.Player == self.opp_r2_name]
    elif opp_r2_pos == 'PF':
      opp_r2_df = opp_pf_df
      self.opp_r2_df = opp_r2_df[opp_r2_df.Player == self.opp_r2_name]
    elif opp_r2_pos == 'C':
      opp_r2_df = opp_c_df
      self.opp_r2_df = opp_r2_df[opp_r2_df.Player == self.opp_r2_name]
     #opp_r3
    self.opp_r3_name = opp_r3_name
    self.opp_r3_minutes = opp_r3_minutes
    self.opp_r3_year = opp_r3_year
    self.opp_r3_pos = opp_r3_pos
    if opp_r3_pos == 'PG':
      opp_r3_df = opp_pg_df
      self.opp_r3_df = opp_r3_df[opp_r3_df.Player == self.opp_r3_name]
    elif opp_r3_pos == 'SG':
      opp_r3_df = opp_sg_df
      self.opp_r3_df = opp_r3_df[opp_r3_df.Player == self.opp_r3_name]
    elif opp_r3_pos == 'SF':
      opp_r3_df = opp_sf_df
      self.opp_r3_df = opp_r3_df[opp_r3_df.Player == self.opp_r3_name]
    elif opp_r3_pos == 'PF':
      opp_r3_df = opp_pf_df
      self.opp_r3_df = opp_r3_df[opp_r3_df.Player == self.opp_r3_name]
    elif opp_r3_pos == 'C':
      opp_r3_df = opp_c_df
      self.opp_r3_df = opp_r3_df[opp_r3_df.Player == self.opp_r3_name]
    #opp_r4
    self.opp_r4_name = opp_r4_name
    self.opp_r4_minutes = opp_r4_minutes
    self.opp_r4_year = opp_r4_year
    self.opp_r4_pos = opp_r4_pos
    if opp_r4_pos == 'PG':
      opp_r4_df = opp_pg_df
      self.opp_r4_df = opp_r4_df[opp_r4_df.Player == self.opp_r4_name]
    elif opp_r4_pos == 'SG':
      opp_r4_df = opp_sg_df
      self.opp_r4_df = opp_r4_df[opp_r4_df.Player == self.opp_r4_name]
    elif opp_r4_pos == 'SF':
      opp_r4_df = opp_sf_df
      self.opp_r4_df = opp_r4_df[opp_r4_df.Player == self.opp_r4_name]
    elif opp_r4_pos == 'PF':
      opp_r4_df = opp_pf_df
      self.opp_r4_df = opp_r4_df[opp_r4_df.Player == self.opp_r4_name]
    elif opp_r4_pos == 'C':
      opp_r4_df = opp_c_df
      self.opp_r4_df = opp_r4_df[opp_r4_df.Player == self.opp_r4_name]
    #opp_r5
    self.opp_r5_name = opp_r5_name
    self.opp_r5_minutes = opp_r5_minutes
    self.opp_r5_year = opp_r5_year
    self.opp_r5_pos = opp_r5_pos
    if opp_r5_pos == 'PG':
      opp_r5_df = opp_pg_df
      self.opp_r5_df = opp_r5_df[opp_r5_df.Player == self.opp_r5_name]
    elif opp_r5_pos == 'SG':
      opp_r5_df = opp_sg_df
      self.opp_r5_df = opp_r5_df[opp_r5_df.Player == self.opp_r5_name]
    elif opp_r5_pos == 'SF':
      opp_r5_df = opp_sf_df
      self.opp_r5_df = opp_r5_df[opp_r5_df.Player == self.opp_r5_name]
    elif opp_r5_pos == 'PF':
      opp_r5_df = opp_pf_df
      self.opp_r5_df = opp_r5_df[opp_r5_df.Player == self.opp_r5_name]
    elif opp_r5_pos == 'C':
      opp_r5_df = opp_c_df
      self.opp_r5_df = opp_r5_df[opp_r5_df.Player == self.opp_r5_name]
    #opp_r6
    self.opp_r6_name = opp_r6_name
    self.opp_r6_minutes = opp_r6_minutes
    self.opp_r6_year = opp_r6_year
    self.opp_r6_pos = opp_r6_pos
    if opp_r6_pos == 'PG':
      opp_r6_df = opp_pg_df
      self.opp_r6_df = opp_r6_df[opp_r6_df.Player == self.opp_r6_name]
    elif opp_r6_pos == 'SG':
      opp_r6_df = opp_sg_df
      self.opp_r6_df = opp_r6_df[opp_r6_df.Player == self.opp_r6_name]
    elif opp_r6_pos == 'SF':
      opp_r6_df = opp_sf_df
      self.opp_r6_df = opp_r6_df[opp_r6_df.Player == self.opp_r6_name]
    elif opp_r6_pos == 'PF':
      opp_r6_df = opp_pf_df
      self.opp_r6_df = opp_r6_df[opp_r6_df.Player == self.opp_r6_name]
    elif opp_r6_pos == 'C':
      opp_r6_df = opp_c_df
      self.opp_r6_df = opp_r6_df[opp_r6_df.Player == self.opp_r6_name]
    postlst = [opp_pg_pos, opp_sg_pos, opp_sf_pos, opp_pf_pos, opp_c_pos, opp_sxth_pos, opp_r1_pos, opp_r2_pos, opp_r3_pos, opp_r4_pos, opp_r5_pos, opp_r6_pos]
    mintlst = [opp_pg_minutes, opp_sg_minutes, opp_sf_minutes, opp_pf_minutes, opp_c_minutes, opp_sxth_minutes, opp_r1_minutes, opp_r2_minutes, opp_r3_minutes, opp_r4_minutes, opp_r5_minutes, opp_r6_minutes]
    opp_pgminlst = []
    opp_sgminlst = []
    opp_sfminlst = []
    opp_pfminlst = []
    opp_cminlst = []
    for x,y in zip(postlst, mintlst):
      if x == 'PG':
        opp_pgminlst.append(y)
      elif x == 'SG':
        opp_sgminlst.append(y)
      elif x == 'SF':
        opp_sfminlst.append(y)
      elif x == 'PF':
        opp_pfminlst.append(y)
      elif x == 'C':
        opp_cminlst.append(y)
    if sum(opp_pgminlst) != 48:
      warnings.warn('Number of minutes must total 48.')
    if sum(opp_sgminlst) != 48:
      warnings.warn('Number of minutes must total 48.')
    if sum(opp_sfminlst) != 48:
      warnings.warn('Number of minutes must total 48.')
    if sum(opp_pfminlst) != 48:
      warnings.warn('Number of minutes must total 48.')
    if sum(opp_cminlst) != 48:
      warnings.warn('Number of minutes must total 48.')

  def simulate(self, reg = 'lreg', hyp_tuning = False, verbose = 0, n_iter = 100, cv = 3, random_state = 42, n_jobs = -1):
    import pandas as pd
    from scipy.stats import uniform
    from sklearn.linear_model import LinearRegression
    from sklearn.linear_model import Ridge
    from sklearn.linear_model import Lasso
    from sklearn.model_selection import RandomizedSearchCV
    col = ['PTS', 'AST', 'TRB', 'ORB', 'DRB', 'FG', 'FGA', 'FG%', 'FT', 'FTA', 'FT%', '3P', '3PA', '3P%', 'STL', 'BLK', 'PF', 'TOV']


    #pg simulation
    X = self.pg_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.pg_df[col]
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    pg_predict = reg.predict([[1, self.pg_minutes, self.pg_year, self.pg_df[self.pg_df.year == self.pg_year]['PER'].mean(), self.opp_pg_df[self.opp_pg_df.year == self.opp_pg_year]['Tm DRtg'].mean()]])
    if pg_predict[:,0] < 0:
      pg_predict[:,0] = 0
    else:
     pg_predict[:,0] = pg_predict[:,0]
    self.pg_data = [self.pg_name, 'PG', pg_predict]
    pglst = []
    for i in self.pg_data:
      try: 
        i = i.squeeze()
        for z in i:
          pglst.append(z)
      except:
        pglst.append(i) 
    self.pg_data = pglst
    temp_pg_data = [round(x) for x in self.pg_data[2:]]
    temp_pg_data.insert(0,self.pg_data[0])
    temp_pg_data.insert(1,self.pg_data[1])
    self.pg_data = temp_pg_data


    #sg simulation
    X = self.sg_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.sg_df[col]
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg = reg
    reg.fit(X, y)
    sg_predict = reg.predict([[1, self.sg_minutes, self.sg_year, self.sg_df[self.sg_df.year == self.sg_year]['PER'].mean(), self.opp_sg_df[self.opp_sg_df.year == self.opp_sg_year]['Tm DRtg'].mean()]])
    if sg_predict[:,0]  < 0:
      sg_predict[:,0]  = 0
    else:
     sg_predict[:,0]  = sg_predict[:,0] 
    self.sg_data = [self.sg_name, 'SG', sg_predict]
    sglst = []
    for i in self.sg_data:
      try: 
        i = i.squeeze()
        for z in i:
          sglst.append(z)
      except:
        sglst.append(i) 
    self.sg_data = sglst
    temp_sg_data = [round(x) for x in self.sg_data[2:]]
    temp_sg_data.insert(0,self.sg_data[0])
    temp_sg_data.insert(1,self.sg_data[1])
    self.sg_data = temp_sg_data

    #sf simulation
    X = self.sf_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.sf_df[col]
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg = reg
    reg.fit(X, y)
    sf_predict = reg.predict([[1, self.sf_minutes, self.sf_year, self.sf_df[self.sf_df.year == self.sf_year]['PER'].mean(), self.opp_sf_df[self.opp_sf_df.year == self.opp_sf_year]['Tm DRtg'].mean()]])
    if sf_predict[:,0]  < 0:
      sf_predict[:,0]  = 0
    else:
     sf_predict[:,0]  = sf_predict[:,0] 
    self.sf_data = [self.sf_name, 'SF', sf_predict]
    sflst = []
    for i in self.sf_data:
      try: 
        i = i.squeeze()
        for z in i:
          sflst.append(z)
      except:
        sflst.append(i) 
    self.sf_data = sflst
    temp_sf_data = [round(x) for x in self.sf_data[2:]]
    temp_sf_data.insert(0,self.sf_data[0])
    temp_sf_data.insert(1,self.sf_data[1])
    self.sf_data = temp_sf_data

    #pf simulation
    X = self.pf_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.pf_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    pf_predict = reg.predict([[1, self.pf_minutes, self.pf_year, self.pf_df[self.pf_df.year == self.pf_year]['PER'].mean(), self.opp_pf_df[self.opp_pf_df.year == self.opp_pf_year]['Tm DRtg'].mean()]])
    if pf_predict[:,0]  < 0:
      pf_predict[:,0]  = 0
    else:
     pf_predict[:,0] = pf_predict[:,0] 
    self.pf_data = [self.pf_name, 'PF', pf_predict]
    pflst = []
    for i in self.pf_data:
      try: 
        i = i.squeeze()
        for z in i:
          pflst.append(z)
      except:
        pflst.append(i) 
    self.pf_data = pflst
    temp_pf_data = [round(x) for x in self.pf_data[2:]]
    temp_pf_data.insert(0,self.pf_data[0])
    temp_pf_data.insert(1,self.pf_data[1])
    self.pf_data = temp_pf_data

    #c simulation
    X = self.c_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.c_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    c_predict = reg.predict([[1, self.c_minutes, self.c_year, self.c_df[self.c_df.year == self.c_year]['PER'].mean(), self.opp_c_df[self.opp_c_df.year == self.opp_c_year]['Tm DRtg'].mean()]])
    if c_predict[:,0]  < 0:
      c_predict = 0
    else:
     c_predict[:,0]   = c_predict[:,0] 
    self.c_data = [self.c_name, 'C', c_predict]
    clst = []
    for i in self.c_data:
      try: 
        i = i.squeeze()
        for z in i:
          clst.append(z)
      except:
        clst.append(i) 
    self.c_data = clst
    temp_c_data = [round(x) for x in self.c_data[2:]]
    temp_c_data.insert(0,self.c_data[0])
    temp_c_data.insert(1,self.c_data[1])
    self.c_data = temp_c_data

        #sxth simulation
    X = self.sxth_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.sxth_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    sxth_predict = reg.predict([[1, self.sxth_minutes, self.sxth_year, self.sxth_df[self.sxth_df.year == self.sxth_year]['PER'].mean(), self.opp_sxth_df[self.opp_sxth_df.year == self.opp_sxth_year]['Tm DRtg'].mean()]])
    if sxth_predict[:,0]  < 0:
      sxth_predict = 0
    else:
     sxth_predict[:,0]   = sxth_predict[:,0] 
    self.sxth_data = [self.sxth_name, self.sxth_pos, sxth_predict]
    sxthlst = []
    for i in self.sxth_data:
      try: 
        i = i.squeeze()
        for z in i:
          sxthlst.append(z)
      except:
        sxthlst.append(i) 
    self.sxth_data = sxthlst
    temp_sxth_data = [round(x) for x in self.sxth_data[2:]]
    temp_sxth_data.insert(0,self.sxth_data[0])
    temp_sxth_data.insert(1,self.sxth_data[1])
    self.sxth_data = temp_sxth_data

            #r1 simulation
    X = self.r1_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.r1_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    r1_predict = reg.predict([[1, self.r1_minutes, self.r1_year, self.r1_df[self.r1_df.year == self.r1_year]['PER'].mean(), self.opp_r1_df[self.opp_r1_df.year == self.opp_r1_year]['Tm DRtg'].mean()]])
    if r1_predict[:,0]  < 0:
      r1_predict = 0
    else:
     r1_predict[:,0]   = r1_predict[:,0] 
    self.r1_data = [self.r1_name, self.r1_pos, r1_predict]
    r1lst = []
    for i in self.r1_data:
      try: 
        i = i.squeeze()
        for z in i:
          r1lst.append(z)
      except:
        r1lst.append(i) 
    self.r1_data = r1lst
    temp_r1_data = [round(x) for x in self.r1_data[2:]]
    temp_r1_data.insert(0,self.r1_data[0])
    temp_r1_data.insert(1,self.r1_data[1])
    self.r1_data = temp_r1_data

                #r2 simulation
    X = self.r2_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.r2_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    r2_predict = reg.predict([[1, self.r2_minutes, self.r2_year, self.r2_df[self.r2_df.year == self.r2_year]['PER'].mean(), self.opp_r2_df[self.opp_r2_df.year == self.opp_r2_year]['Tm DRtg'].mean()]])
    if r2_predict[:,0]  < 0:
      r2_predict = 0
    else:
     r2_predict[:,0]   = r2_predict[:,0] 
    self.r2_data = [self.r2_name, self.r2_pos, r2_predict]
    r2lst = []
    for i in self.r2_data:
      try: 
        i = i.squeeze()
        for z in i:
          r2lst.append(z)
      except:
        r2lst.append(i) 
    self.r2_data = r2lst
    temp_r2_data = [round(x) for x in self.r2_data[2:]]
    temp_r2_data.insert(0,self.r2_data[0])
    temp_r2_data.insert(1,self.r2_data[1])
    self.r2_data = temp_r2_data

    #r3 simulation
    X = self.r3_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.r3_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    r3_predict = reg.predict([[1, self.r3_minutes, self.r3_year, self.r3_df[self.r3_df.year == self.r3_year]['PER'].mean(), self.opp_r3_df[self.opp_r3_df.year == self.opp_r3_year]['Tm DRtg'].mean()]])
    if r3_predict[:,0]  < 0:
      r3_predict = 0
    else:
     r3_predict[:,0]   = r3_predict[:,0] 
    self.r3_data = [self.r3_name, self.r3_pos, r3_predict]
    r3lst = []
    for i in self.r3_data:
      try: 
        i = i.squeeze()
        for z in i:
          r3lst.append(z)
      except:
        r3lst.append(i) 
    self.r3_data = r3lst
    temp_r3_data = [round(x) for x in self.r3_data[2:]]
    temp_r3_data.insert(0,self.r3_data[0])
    temp_r3_data.insert(1,self.r3_data[1])
    self.r3_data = temp_r3_data

    #r4 simulation
    X = self.r4_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.r4_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    r4_predict = reg.predict([[1, self.r4_minutes, self.r4_year, self.r4_df[self.r4_df.year == self.r4_year]['PER'].mean(), self.opp_r4_df[self.opp_r4_df.year == self.opp_r4_year]['Tm DRtg'].mean()]])
    if r4_predict[:,0]  < 0:
      r4_predict = 0
    else:
     r4_predict[:,0]   = r4_predict[:,0] 
    self.r4_data = [self.r4_name, self.r4_pos, r4_predict]
    r4lst = []
    for i in self.r4_data:
      try: 
        i = i.squeeze()
        for z in i:
          r4lst.append(z)
      except:
        r4lst.append(i) 
    self.r4_data = r4lst
    temp_r4_data = [round(x) for x in self.r4_data[2:]]
    temp_r4_data.insert(0,self.r4_data[0])
    temp_r4_data.insert(1,self.r4_data[1])
    self.r4_data = temp_r4_data

    #r5 simulation
    X = self.r5_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.r5_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    r5_predict = reg.predict([[1, self.r5_minutes, self.r5_year, self.r5_df[self.r5_df.year == self.r5_year]['PER'].mean(), self.opp_r5_df[self.opp_r5_df.year == self.opp_r5_year]['Tm DRtg'].mean()]])
    if r5_predict[:,0]  < 0:
      r5_predict = 0
    else:
     r5_predict[:,0]   = r5_predict[:,0] 
    self.r5_data = [self.r5_name, self.r5_pos, r5_predict]
    r5lst = []
    for i in self.r5_data:
      try: 
        i = i.squeeze()
        for z in i:
          r5lst.append(z)
      except:
        r5lst.append(i) 
    self.r5_data = r5lst
    temp_r5_data = [round(x) for x in self.r5_data[2:]]
    temp_r5_data.insert(0,self.r5_data[0])
    temp_r5_data.insert(1,self.r5_data[1])
    self.r5_data = temp_r5_data

    #r6 simulation
    X = self.r6_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.r6_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    r6_predict = reg.predict([[1, self.r6_minutes, self.r6_year, self.r6_df[self.r6_df.year == self.r6_year]['PER'].mean(), self.opp_r6_df[self.opp_r6_df.year == self.opp_r6_year]['Tm DRtg'].mean()]])
    if r6_predict[:,0]  < 0:
      r6_predict = 0
    else:
     r6_predict[:,0]   = r6_predict[:,0] 
    self.r6_data = [self.r6_name, self.r6_pos, r6_predict]
    r6lst = []
    for i in self.r6_data:
      try: 
        i = i.squeeze()
        for z in i:
          r6lst.append(z)
      except:
        r6lst.append(i) 
    self.r6_data = r6lst
    temp_r6_data = [round(x) for x in self.r6_data[2:]]
    temp_r6_data.insert(0,self.r6_data[0])
    temp_r6_data.insert(1,self.r6_data[1])
    self.r6_data = temp_r6_data
        #opp_pg simulation
    X = self.opp_pg_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.opp_pg_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    opp_pg_predict = reg.predict([[1, self.opp_pg_minutes, self.opp_pg_year, self.opp_pg_df[self.opp_pg_df.year == self.opp_pg_year]['PER'].mean(),  self.pg_df[self.pg_df.year == self.pg_year]['Tm DRtg'].mean()]])
    if opp_pg_predict[:,0] < 0:
      opp_pg_predict[:,0] = 0
    else:
     opp_pg_predict[:,0] = opp_pg_predict[:,0]
    self.opp_pg_data = [self.opp_pg_name, 'PG', opp_pg_predict]
    opp_pglst = []
    for i in self.opp_pg_data:
      try: 
        i = i.squeeze()
        for z in i:
          opp_pglst.append(z)
      except:
        opp_pglst.append(i) 
    self.opp_pg_data = opp_pglst
    temp_opp_pg_data = [round(x) for x in self.opp_pg_data[2:]]
    temp_opp_pg_data.insert(0,self.opp_pg_data[0])
    temp_opp_pg_data.insert(1,self.opp_pg_data[1])
    self.opp_pg_data = temp_opp_pg_data


    #opp_sg simulation
    X = self.opp_sg_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.opp_sg_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    opp_sg_predict = reg.predict([[1, self.opp_sg_minutes, self.opp_sg_year, self.opp_sg_df[self.opp_sg_df.year == self.opp_sg_year]['PER'].mean(), self.sg_df[self.sg_df.year == self.sg_year]['Tm DRtg'].mean()]])
    if opp_sg_predict[:,0]  < 0:
      opp_sg_predict[:,0]  = 0
    else:
     opp_sg_predict[:,0]  = opp_sg_predict[:,0] 
    self.opp_sg_data = [self.opp_sg_name, 'SG', opp_sg_predict]
    opp_sglst = []
    for i in self.opp_sg_data:
      try: 
        i = i.squeeze()
        for z in i:
          opp_sglst.append(z)
      except:
        opp_sglst.append(i) 
    self.opp_sg_data = opp_sglst
    temp_opp_sg_data = [round(x) for x in self.opp_sg_data[2:]]
    temp_opp_sg_data.insert(0,self.opp_sg_data[0])
    temp_opp_sg_data.insert(1,self.opp_sg_data[1])
    self.opp_sg_data = temp_opp_sg_data

    #sf simulation
    X = self.opp_sf_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.opp_sf_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    opp_sf_predict = reg.predict([[1, self.opp_sf_minutes, self.opp_sf_year, self.opp_sf_df[self.opp_sf_df.year == self.opp_sf_year]['PER'].mean(), self.sf_df[self.sf_df.year == self.sf_year]['Tm DRtg'].mean()]])
    if opp_sf_predict[:,0]  < 0:
      opp_sf_predict[:,0]  = 0
    else:
     opp_sf_predict[:,0]  = opp_sf_predict[:,0] 
    self.opp_sf_data = [self.opp_sf_name, 'SF', opp_sf_predict]
    sflst = []
    for i in self.opp_sf_data:
      try: 
        i = i.squeeze()
        for z in i:
          sflst.append(z)
      except:
        sflst.append(i) 
    self.opp_sf_data = sflst
    temp_opp_sf_data = [round(x) for x in self.opp_sf_data[2:]]
    temp_opp_sf_data.insert(0,self.opp_sf_data[0])
    temp_opp_sf_data.insert(1,self.opp_sf_data[1])
    self.opp_sf_data = temp_opp_sf_data

    #opp_pf simulation
    X = self.opp_pf_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.opp_pf_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    opp_pf_predict = reg.predict([[1, self.opp_pf_minutes, self.opp_pf_year, self.opp_pf_df[self.opp_pf_df.year == self.opp_pf_year]['PER'].mean(), self.pf_df[self.pf_df.year == self.pf_year]['Tm DRtg'].mean()]])
    if opp_pf_predict[:,0]  < 0:
      opp_pf_predict[:,0]  = 0
    else:
     opp_pf_predict[:,0] = opp_pf_predict[:,0] 
    self.opp_pf_data = [self.opp_pf_name, 'PF', opp_pf_predict]
    opp_pflst = []
    for i in self.opp_pf_data:
      try: 
        i = i.squeeze()
        for z in i:
          opp_pflst.append(z)
      except:
        opp_pflst.append(i) 
    self.opp_pf_data = opp_pflst
    temp_opp_pf_data = [round(x) for x in self.opp_pf_data[2:]]
    temp_opp_pf_data.insert(0,self.opp_pf_data[0])
    temp_opp_pf_data.insert(1,self.opp_pf_data[1])
    self.opp_pf_data = temp_opp_pf_data

    #c simulation
    X = self.opp_c_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.opp_c_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    opp_c_predict = reg.predict([[1, self.opp_c_minutes, self.opp_c_year, self.opp_c_df[self.opp_c_df.year == self.opp_c_year]['PER'].mean(), self.c_df[self.c_df.year == self.c_year]['Tm DRtg'].mean() ]])
    
    if opp_c_predict[:,0]  < 0:
      opp_c_predict = 0
    else:
     opp_c_predict[:,0]   = opp_c_predict[:,0] 
    self.opp_c_data = [self.opp_c_name, 'C', opp_c_predict]
    clst = []
    for i in self.opp_c_data:
      try: 
        i = i.squeeze()
        for z in i:
          clst.append(z)
      except:
        clst.append(i) 
    self.opp_c_data = clst
    temp_opp_c_data = [round(x) for x in self.opp_c_data[2:]]
    temp_opp_c_data.insert(0,self.opp_c_data[0])
    temp_opp_c_data.insert(1,self.opp_c_data[1])
    self.opp_c_data = temp_opp_c_data

        #opp_opp_sxth simulation
    X = self.opp_sxth_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.opp_sxth_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    opp_sxth_predict = reg.predict([[1, self.opp_sxth_minutes, self.opp_sxth_year, self.opp_sxth_df[self.opp_sxth_df.year == self.opp_sxth_year]['PER'].mean(), self.sxth_df[self.sxth_df.year == self.sxth_year]['Tm DRtg'].mean()]])
    if opp_sxth_predict[:,0]  < 0:
      opp_sxth_predict = 0
    else:
     opp_sxth_predict[:,0]   = opp_sxth_predict[:,0] 
    self.opp_sxth_data = [self.opp_sxth_name, self.opp_sxth_pos, opp_sxth_predict]
    opp_sxthlst = []
    for i in self.opp_sxth_data:
      try: 
        i = i.squeeze()
        for z in i:
          opp_sxthlst.append(z)
      except:
        opp_sxthlst.append(i) 
    self.opp_sxth_data = opp_sxthlst
    temp_opp_sxth_data = [round(x) for x in self.opp_sxth_data[2:]]
    temp_opp_sxth_data.insert(0,self.opp_sxth_data[0])
    temp_opp_sxth_data.insert(1,self.opp_sxth_data[1])
    self.opp_sxth_data = temp_opp_sxth_data

            #opp_r1 simulation
    X = self.opp_r1_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.opp_r1_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    opp_r1_predict = reg.predict([[1, self.opp_r1_minutes, self.opp_r1_year, self.opp_r1_df[self.opp_r1_df.year == self.opp_r1_year]['PER'].mean(), self.r1_df[self.r1_df.year == self.r1_year]['Tm DRtg'].mean()]])
    if opp_r1_predict[:,0]  < 0:
      opp_r1_predict = 0
    else:
     opp_r1_predict[:,0]   = opp_r1_predict[:,0] 
    self.opp_r1_data = [self.opp_r1_name, self.opp_r1_pos, opp_r1_predict]
    opp_r1lst = []
    for i in self.opp_r1_data:
      try: 
        i = i.squeeze()
        for z in i:
          opp_r1lst.append(z)
      except:
        opp_r1lst.append(i) 
    self.opp_r1_data = opp_r1lst
    temp_opp_r1_data = [round(x) for x in self.opp_r1_data[2:]]
    temp_opp_r1_data.insert(0,self.opp_r1_data[0])
    temp_opp_r1_data.insert(1,self.opp_r1_data[1])
    self.opp_r1_data = temp_opp_r1_data

                #opp_r2 simulation
    X = self.opp_r2_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.opp_r2_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    opp_r2_predict = reg.predict([[1, self.opp_r2_minutes, self.opp_r2_year, self.opp_r2_df[self.opp_r2_df.year == self.opp_r2_year]['PER'].mean(), self.r2_df[self.r2_df.year == self.r2_year]['Tm DRtg'].mean()]])
    if opp_r2_predict[:,0]  < 0:
      opp_r2_predict = 0
    else:
     opp_r2_predict[:,0]   = opp_r2_predict[:,0] 
    self.opp_r2_data = [self.opp_r2_name, self.opp_r2_pos, opp_r2_predict]
    opp_r2lst = []
    for i in self.opp_r2_data:
      try: 
        i = i.squeeze()
        for z in i:
          opp_r2lst.append(z)
      except:
        opp_r2lst.append(i) 
    self.opp_r2_data = opp_r2lst
    temp_opp_r2_data = [round(x) for x in self.opp_r2_data[2:]]
    temp_opp_r2_data.insert(0,self.opp_r2_data[0])
    temp_opp_r2_data.insert(1,self.opp_r2_data[1])
    self.opp_r2_data = temp_opp_r2_data

    #opp_r3 simulation
    X = self.opp_r3_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.opp_r3_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    opp_r3_predict = reg.predict([[1, self.opp_r3_minutes, self.opp_r3_year, self.opp_r3_df[self.opp_r3_df.year == self.opp_r3_year]['PER'].mean(), self.r3_df[self.r3_df.year == self.r3_year]['Tm DRtg'].mean()]])
    if opp_r3_predict[:,0]  < 0:
      opp_r3_predict = 0
    else:
     opp_r3_predict[:,0]   = opp_r3_predict[:,0] 
    self.opp_r3_data = [self.opp_r3_name, self.opp_r3_pos, opp_r3_predict]
    opp_r3lst = []
    for i in self.opp_r3_data:
      try: 
        i = i.squeeze()
        for z in i:
          opp_r3lst.append(z)
      except:
        opp_r3lst.append(i) 
    self.opp_r3_data = opp_r3lst
    temp_opp_r3_data = [round(x) for x in self.opp_r3_data[2:]]
    temp_opp_r3_data.insert(0,self.opp_r3_data[0])
    temp_opp_r3_data.insert(1,self.opp_r3_data[1])
    self.opp_r3_data = temp_opp_r3_data

    #opp_r4 simulation
    X = self.opp_r4_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.opp_r4_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    opp_r4_predict = reg.predict([[1, self.opp_r4_minutes, self.opp_r4_year, self.opp_r4_df[self.opp_r4_df.year == self.opp_r4_year]['PER'].mean(), self.r4_df[self.r4_df.year == self.r4_year]['Tm DRtg'].mean()]])
    if opp_r4_predict[:,0]  < 0:
      opp_r4_predict = 0
    else:
     opp_r4_predict[:,0]   = opp_r4_predict[:,0] 
    self.opp_r4_data = [self.opp_r4_name, self.opp_r4_pos, opp_r4_predict]
    opp_r4lst = []
    for i in self.opp_r4_data:
      try: 
        i = i.squeeze()
        for z in i:
          opp_r4lst.append(z)
      except:
        opp_r4lst.append(i) 
    self.opp_r4_data = opp_r4lst
    temp_opp_r4_data = [round(x) for x in self.opp_r4_data[2:]]
    temp_opp_r4_data.insert(0,self.opp_r4_data[0])
    temp_opp_r4_data.insert(1,self.opp_r4_data[1])
    self.opp_r4_data = temp_opp_r4_data

    #opp_r5 simulation
    X = self.opp_r5_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.opp_r5_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    opp_r5_predict = reg.predict([[1, self.opp_r5_minutes, self.opp_r5_year, self.opp_r5_df[self.opp_r5_df.year == self.opp_r5_year]['PER'].mean(), self.r5_df[self.r5_df.year == self.r5_year]['Tm DRtg'].mean()]])
    if opp_r5_predict[:,0]  < 0:
      opp_r5_predict = 0
    else:
     opp_r5_predict[:,0]   = opp_r5_predict[:,0] 
    self.opp_r5_data = [self.opp_r5_name, self.opp_r5_pos, opp_r5_predict]
    opp_r5lst = []
    for i in self.opp_r5_data:
      try: 
        i = i.squeeze()
        for z in i:
          opp_r5lst.append(z)
      except:
        opp_r5lst.append(i) 
    self.opp_r5_data = opp_r5lst
    temp_opp_r5_data = [round(x) for x in self.opp_r5_data[2:]]
    temp_opp_r5_data.insert(0,self.opp_r5_data[0])
    temp_opp_r5_data.insert(1,self.opp_r5_data[1])
    self.opp_r5_data = temp_opp_r5_data

    #opp_r6 simulation
    X = self.opp_r6_df[['GS', 'MP', 'year', 'PER', 'Opp DRtg']]
    y = self.opp_r6_df[col]
    reg = reg
    if reg == 'lreg':
      reg = LinearRegression()
    elif reg == 'lasso':
      reg = Lasso()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Lasso(**rand_search.best_params_)
    elif reg == 'ridge':
      reg = Ridge()
      if hyp_tuning is True:
        random_grid = {'alpha': uniform()}
        rand_search = RandomizedSearchCV(estimator = reg, param_distributions = random_grid, n_iter = n_iter, cv = cv, verbose= verbose, random_state= random_state, n_jobs = n_jobs)
        rand_search.fit(X, y)
        reg = Ridge(**rand_search.best_params_)
    reg.fit(X, y)
    opp_r6_predict = reg.predict([[1, self.opp_r6_minutes, self.opp_r6_year, self.opp_r6_df[self.opp_r6_df.year == self.opp_r6_year]['PER'].mean(), self.r6_df[self.r6_df.year == self.r6_year]['Tm DRtg'].mean()]])
    if opp_r6_predict[:,0]  < 0:
      opp_r6_predict = 0
    else:
     opp_r6_predict[:,0]   = opp_r6_predict[:,0] 
    self.opp_r6_data = [self.opp_r6_name, self.opp_r6_pos, opp_r6_predict]
    opp_r6lst = []
    for i in self.opp_r6_data:
      try: 
        i = i.squeeze()
        for z in i:
          opp_r6lst.append(z)
      except:
        opp_r6lst.append(i) 
    self.opp_r6_data = opp_r6lst
    temp_opp_r6_data = [round(x) for x in self.opp_r6_data[2:]]
    temp_opp_r6_data.insert(0,self.opp_r6_data[0])
    temp_opp_r6_data.insert(1,self.opp_r6_data[1])
    self.opp_r6_data = temp_opp_r6_data


    #creating the simulation results dataframe
  def results(self, table = None):
    import pandas as pd
    col = ['PTS', 'AST', 'TRB', 'ORB', 'DRB', 'FG', 'FGA', 'FG%', 'FT', 'FTA', 'FT%', '3P', '3PA', '3P%', 'STL', 'BLK', 'PF', 'TOV']
    if table is None:
      total = self.pg_data[2] +  self.sg_data[2] +  self.sf_data[2] +  self.pf_data[2] + self.c_data[2] + self.sxth_data[2] +  self.r1_data[2] +  self.r2_data[2] +  self.r3_data[2] + self.r4_data[2] + self.r5_data[2] + self.r6_data[2]
      opp_total = self.opp_pg_data[2] +  self.opp_sg_data[2] +  self.opp_sf_data[2] +  self.opp_pf_data[2] + self.opp_c_data[2] + self.opp_sxth_data[2] +  self.opp_r1_data[2] +  self.opp_r2_data[2] +  self.opp_r3_data[2] + self.opp_r4_data[2] + self.opp_r5_data[2] + self.opp_r6_data[2]
      return print("Total Score:", int(total), int(opp_total))
    elif table == 'team_1_dataframe':
      total_pt = self.pg_data[2] +  self.sg_data[2] +  self.sf_data[2] +  self.pf_data[2] + self.c_data[2] + self.sxth_data[2] +  self.r1_data[2] +  self.r2_data[2] +  self.r3_data[2] + self.r4_data[2] + self.r5_data[2] + self.r6_data[2]
      total_ast = self.pg_data[3] +  self.sg_data[3] +  self.sf_data[3] +  self.pf_data[3] + self.c_data[3] + self.sxth_data[3] +  self.r1_data[3] +  self.r2_data[3] +  self.r3_data[3] + self.r4_data[3] + self.r5_data[3] + self.r6_data[3]
      #total_trb = self.pg_data[4] +  self.sg_data[4] +  self.sf_data[4] +  self.pf_data[4] + self.c_data[4] + self.sxth_data[4] +  self.r1_data[4] +  self.r2_data[4] +  self.r3_data[4] + self.r4_data[4] + self.r5_data[4] + self.r6_data[4]
      total_orb = self.pg_data[5] +  self.sg_data[5] +  self.sf_data[5] +  self.pf_data[5] + self.c_data[5] + self.sxth_data[5] +  self.r1_data[5] +  self.r2_data[5] +  self.r3_data[5] + self.r4_data[5] + self.r5_data[5] + self.r6_data[5]
      total_drb = self.pg_data[6] +  self.sg_data[6] +  self.sf_data[6] +  self.pf_data[6] + self.c_data[6] + self.sxth_data[6] +  self.r1_data[6] +  self.r2_data[6] +  self.r3_data[6] + self.r4_data[6] + self.r5_data[6] + self.r6_data[6]
      total_trb = total_orb + total_drb
      total_fg = self.pg_data[7] +  self.sg_data[7] +  self.sf_data[7] +  self.pf_data[7] + self.c_data[7] + self.sxth_data[7] +  self.r1_data[7] +  self.r2_data[7] +  self.r3_data[7] + self.r4_data[7] + self.r5_data[7] + self.r6_data[7]
      total_fga = self.pg_data[8] +  self.sg_data[8] +  self.sf_data[8] +  self.pf_data[8] + self.c_data[8] + self.sxth_data[8] +  self.r1_data[8] +  self.r2_data[8] +  self.r3_data[8] + self.r4_data[8] + self.r5_data[8] + self.r6_data[8]
      #total_fgp = self.pg_data[9] +  self.sg_data[9] +  self.sf_data[9] +  self.pf_data[9] + self.c_data[9] + self.sxth_data[9] +  self.r1_data[9] +  self.r2_data[9] +  self.r3_data[9] + self.r4_data[9] + self.r5_data[9] + self.r6_data[9]
      total_fgp = total_fg/total_fga * 100
      total_ft = self.pg_data[10] +  self.sg_data[10] +  self.sf_data[10] +  self.pf_data[10] + self.c_data[10] + self.sxth_data[10] +  self.r1_data[10] +  self.r2_data[10] +  self.r3_data[10] + self.r4_data[10] + self.r5_data[10] + self.r6_data[10]
      total_fta = self.pg_data[11] +  self.sg_data[11] +  self.sf_data[11] +  self.pf_data[11] + self.c_data[11] + self.sxth_data[11] +  self.r1_data[11] +  self.r2_data[11] +  self.r3_data[11] + self.r4_data[11] + self.r5_data[11] + self.r6_data[11]
      #total_ftp = self.pg_data[12] +  self.sg_data[12] +  self.sf_data[12] +  self.pf_data[12] + self.c_data[12] + self.sxth_data[12] +  self.r1_data[12] +  self.r2_data[12] +  self.r3_data[12] + self.r4_data[12] + self.r5_data[12] + self.r6_data[12]
      total_ftp = total_ft/total_fta * 100
      total_3p = self.pg_data[13] +  self.sg_data[13] +  self.sf_data[13] +  self.pf_data[13] + self.c_data[13] + self.sxth_data[13] +  self.r1_data[13] +  self.r2_data[13] +  self.r3_data[13] + self.r4_data[13] + self.r5_data[13] + self.r6_data[13]
      total_3pa = self.pg_data[14] +  self.sg_data[14] +  self.sf_data[14] +  self.pf_data[14] + self.c_data[14] + self.sxth_data[14] +  self.r1_data[14] +  self.r2_data[14] +  self.r3_data[14] + self.r4_data[14] + self.r5_data[14] + self.r6_data[14]
      #total_3pp = self.pg_data[15] +  self.sg_data[15] +  self.sf_data[15] +  self.pf_data[15] + self.c_data[15] + self.sxth_data[15] +  self.r1_data[15] +  self.r2_data[15] +  self.r3_data[15] + self.r4_data[15] + self.r5_data[15] + self.r6_data[15]
      total_3pp = total_3p/total_3pa * 100
      total_stl = self.pg_data[16] +  self.sg_data[16] +  self.sf_data[16] +  self.pf_data[16] + self.c_data[16] + self.sxth_data[16] +  self.r1_data[16] +  self.r2_data[16] +  self.r3_data[16] + self.r4_data[16] + self.r5_data[16] + self.r6_data[16]
      total_blk = self.pg_data[17] +  self.sg_data[17] +  self.sf_data[17] +  self.pf_data[17] + self.c_data[17] + self.sxth_data[17] +  self.r1_data[17] +  self.r2_data[17] +  self.r3_data[17] + self.r4_data[17] + self.r5_data[17] + self.r6_data[17]
      total_pf = self.pg_data[18] +  self.sg_data[18] +  self.sf_data[18] +  self.pf_data[18] + self.c_data[18] + self.sxth_data[18] +  self.r1_data[18] +  self.r2_data[18] +  self.r3_data[18] + self.r4_data[18] + self.r5_data[18] + self.r6_data[18]
      total_tov = self.pg_data[19] +  self.sg_data[19] +  self.sf_data[19] +  self.pf_data[19] + self.c_data[19] + self.sxth_data[19] +  self.r1_data[19] +  self.r2_data[19] +  self.r3_data[19] + self.r4_data[19] + self.r5_data[19] + self.r6_data[19]
      data = [self.pg_data, self.sg_data, self.sf_data, self.pf_data, self.c_data, self.sxth_data, self.r1_data, self.r2_data, self.r3_data, self.r4_data, self.r5_data, self.r6_data]
      columns = ['Name', 'Position', 'PTS', 'AST', 'TRB', 'ORB', 'DRB', 'FG', 'FGA', 'FG%', 'FT', 'FTA', 'FT%', '3P', '3PA', '3P%', 'STL', 'BLK', 'PF', 'TOV']
      predictions_df = pd.DataFrame(data, columns = columns)
      for i in columns[2:]:
        predictions_df[i] = [0 if x < 0 else x for x in predictions_df[i]]
      predictions_df['TRB'] = predictions_df['ORB'] + predictions_df['DRB']
      fgalst = []
      ftalst = []
      threeptalst = []
      for x,y in zip(predictions_df['FG'], predictions_df['FGA']):
        if x > y:
          y = x
        else:
          y = y
        fgalst.append(y)
      for x,y in zip(predictions_df['FT'], predictions_df['FTA']):
        if x > y:
          y = x
        else:
          y = y
        ftalst.append(y)
      for x,y in zip(predictions_df['3P'], predictions_df['3PA']):
        if x > y:
          y = x
        else:
          y = y
        threeptalst.append(y)
      predictions_df['FGA'] = fgalst
      predictions_df['FTA'] = ftalst
      predictions_df['3PA'] = threeptalst
      predictions_df['FG%'] = round(predictions_df['FG']/predictions_df['FGA'] * 100)
      predictions_df['FT%'] = round(predictions_df['FT']/predictions_df['FTA'] * 100)
      predictions_df['3P%'] = round(predictions_df['3P']/predictions_df['3PA'] * 100)
      predictions_df['FG%'] = [0 if x == 'NaN' else x for x in predictions_df['FG%']]
      predictions_df['FT%'] = [0 if x == 'NaN' else x for x in predictions_df['FT%']]
      predictions_df['3P%'] = [0 if x == 'NaN' else x for x in predictions_df['3P%']]
        
      self.minutes_lst = [self.pg_minutes, self.sg_minutes, self.sf_minutes, self.pf_minutes, self.c_minutes, self.sxth_minutes, self.r1_minutes, self.r2_minutes, self.r3_minutes, self.r4_minutes, self.r5_minutes, self.r6_minutes]
      self.year_lst = [self.pg_year, self.sg_year, self.sf_year, self.pf_year, self.c_year, self.sxth_year, self.r1_year, self.r2_year, self.r3_year, self.r4_year, self.r5_year, self.r6_year]
      predictions_df.insert(2, "Minutes", self.minutes_lst, True)
      predictions_df.insert(1, "Year", self.year_lst, True)
      predictions_df['Year'] = predictions_df['Year'].astype('int')
      predictions_df = predictions_df.sort_values(by=['PTS'], ascending = False)
      predictions_df = predictions_df.append({'Name': 'Total/Average', 'Year': round(sum(self.year_lst)/12), 'Position': '', 'Minutes': 240, 'PTS': round(total_pt), 'AST': round(total_ast), 'TRB': round(total_trb), 'ORB': round(total_orb), 'DRB': round(total_drb), 'FG': round(total_fg), 'FGA': round(total_fga),'FG%': round(total_fgp/5), 'FT': round(total_ft),'FTA': round(total_fta), 'FT%': round(total_ftp/5), '3P': round(total_3p),'3PA': round(total_3pa), '3P%': round(total_3pp/5), 'STL': round(total_stl), 'BLK': round(total_blk),  'PF': round(total_pf), 'TOV': round(total_tov)}, ignore_index = True)
      return predictions_df
    elif table == 'team_2_dataframe':
      opp_total_pt = self.opp_pg_data[2] +  self.opp_sg_data[2] +  self.opp_sf_data[2] +  self.opp_pf_data[2] + self.opp_c_data[2] + self.opp_sxth_data[2] +  self.opp_r1_data[2] +  self.opp_r2_data[2] +  self.opp_r3_data[2] + self.opp_r4_data[2] + self.opp_r5_data[2] + self.opp_r6_data[2]
      opp_total_ast = self.opp_pg_data[3] +  self.opp_sg_data[3] +  self.opp_sf_data[3] +  self.opp_pf_data[3] + self.opp_c_data[3] + self.opp_sxth_data[3] +  self.opp_r1_data[3] +  self.opp_r2_data[3] +  self.opp_r3_data[3] + self.opp_r4_data[3] + self.opp_r5_data[3] + self.opp_r6_data[3]
      opp_total_trb = self.opp_pg_data[4] +  self.opp_sg_data[4] +  self.opp_sf_data[4] +  self.opp_pf_data[4] + self.opp_c_data[4] + self.opp_sxth_data[4] +  self.opp_r1_data[4] +  self.opp_r2_data[4] +  self.opp_r3_data[4] + self.opp_r4_data[4] + self.opp_r5_data[4] + self.opp_r6_data[4]
      opp_total_orb = self.opp_pg_data[5] +  self.opp_sg_data[5] +  self.opp_sf_data[5] +  self.opp_pf_data[5] + self.opp_c_data[5] + self.opp_sxth_data[5] +  self.opp_r1_data[5] +  self.opp_r2_data[5] +  self.opp_r3_data[5] + self.opp_r4_data[5] + self.opp_r5_data[5] + self.opp_r6_data[5]
      opp_total_drb = self.opp_pg_data[6] +  self.opp_sg_data[6] +  self.opp_sf_data[6] +  self.opp_pf_data[6] + self.opp_c_data[6] + self.opp_sxth_data[6] +  self.opp_r1_data[6] +  self.opp_r2_data[6] +  self.opp_r3_data[6] + self.opp_r4_data[6] + self.opp_r5_data[6] + self.opp_r6_data[6]
      opp_total_fg = self.opp_pg_data[7] +  self.opp_sg_data[7] +  self.opp_sf_data[7] +  self.opp_pf_data[7] + self.opp_c_data[7] + self.opp_sxth_data[7] +  self.opp_r1_data[7] +  self.opp_r2_data[7] +  self.opp_r3_data[7] + self.opp_r4_data[7] + self.opp_r5_data[7] + self.opp_r6_data[7]
      opp_total_fga = self.opp_pg_data[8] +  self.opp_sg_data[8] +  self.opp_sf_data[8] +  self.opp_pf_data[8] + self.opp_c_data[8] + self.opp_sxth_data[8] +  self.opp_r1_data[8] +  self.opp_r2_data[8] +  self.opp_r3_data[8] + self.opp_r4_data[8] + self.opp_r5_data[8] + self.opp_r6_data[8]
      opp_total_fgp = self.opp_pg_data[9] +  self.opp_sg_data[9] +  self.opp_sf_data[9] +  self.opp_pf_data[9] + self.opp_c_data[9] + self.opp_sxth_data[9] +  self.opp_r1_data[9] +  self.opp_r2_data[9] +  self.opp_r3_data[9] + self.opp_r4_data[9] + self.opp_r5_data[9] + self.opp_r6_data[9]
      opp_total_ft = self.opp_pg_data[10] +  self.opp_sg_data[10] +  self.opp_sf_data[10] +  self.opp_pf_data[10] + self.opp_c_data[10] + self.opp_sxth_data[10] +  self.opp_r1_data[10] +  self.opp_r2_data[10] +  self.opp_r3_data[10] + self.opp_r4_data[10] + self.opp_r5_data[10] + self.opp_r6_data[10]
      opp_total_fta = self.opp_pg_data[11] +  self.opp_sg_data[11] +  self.opp_sf_data[11] +  self.opp_pf_data[11] + self.opp_c_data[11] + self.opp_sxth_data[11] +  self.opp_r1_data[11] +  self.opp_r2_data[11] +  self.opp_r3_data[11] + self.opp_r4_data[11] + self.opp_r5_data[11] + self.opp_r6_data[11]
      opp_total_ftp = self.opp_pg_data[12] +  self.opp_sg_data[12] +  self.opp_sf_data[12] +  self.opp_pf_data[12] + self.opp_c_data[12] + self.opp_sxth_data[12] +  self.opp_r1_data[12] +  self.opp_r2_data[12] +  self.opp_r3_data[12] + self.opp_r4_data[12] + self.opp_r5_data[12] + self.opp_r6_data[12]
      opp_total_3p = self.opp_pg_data[13] +  self.opp_sg_data[13] +  self.opp_sf_data[13] +  self.opp_pf_data[13] + self.opp_c_data[13] + self.opp_sxth_data[13] +  self.opp_r1_data[13] +  self.opp_r2_data[13] +  self.opp_r3_data[13] + self.opp_r4_data[13] + self.opp_r5_data[13] + self.opp_r6_data[13]
      opp_total_3pa = self.opp_pg_data[14] +  self.opp_sg_data[14] +  self.opp_sf_data[14] +  self.opp_pf_data[14] + self.opp_c_data[14] + self.opp_sxth_data[14] +  self.opp_r1_data[14] +  self.opp_r2_data[14] +  self.opp_r3_data[14] + self.opp_r4_data[14] + self.opp_r5_data[14] + self.opp_r6_data[14]
      opp_total_3pp = self.opp_pg_data[15] +  self.opp_sg_data[15] +  self.opp_sf_data[15] +  self.opp_pf_data[15] + self.opp_c_data[15] + self.opp_sxth_data[15] +  self.opp_r1_data[15] +  self.opp_r2_data[15] +  self.opp_r3_data[15] + self.opp_r4_data[15] + self.opp_r5_data[15] + self.opp_r6_data[15]
      opp_total_stl = self.opp_pg_data[16] +  self.opp_sg_data[16] +  self.opp_sf_data[16] +  self.opp_pf_data[16] + self.opp_c_data[16] + self.opp_sxth_data[16] +  self.opp_r1_data[16] +  self.opp_r2_data[16] +  self.opp_r3_data[16] + self.opp_r4_data[16] + self.opp_r5_data[16] + self.opp_r6_data[16]
      opp_total_blk = self.opp_pg_data[17] +  self.opp_sg_data[17] +  self.opp_sf_data[17] +  self.opp_pf_data[17] + self.opp_c_data[17] + self.opp_sxth_data[17] +  self.opp_r1_data[17] +  self.opp_r2_data[17] +  self.opp_r3_data[17] + self.opp_r4_data[17] + self.opp_r5_data[17] + self.opp_r6_data[17]
      opp_total_opp_pf = self.opp_pg_data[18] +  self.opp_sg_data[18] +  self.opp_sf_data[18] +  self.opp_pf_data[18] + self.opp_c_data[18] + self.opp_sxth_data[18] +  self.opp_r1_data[18] +  self.opp_r2_data[18] +  self.opp_r3_data[18] + self.opp_r4_data[18] + self.opp_r5_data[18] + self.opp_r6_data[18]
      opp_total_tov = self.opp_pg_data[19] +  self.opp_sg_data[19] +  self.opp_sf_data[19] +  self.opp_pf_data[19] + self.opp_c_data[19] + self.opp_sxth_data[19] +  self.opp_r1_data[19] +  self.opp_r2_data[19] +  self.opp_r3_data[19] + self.opp_r4_data[19] + self.opp_r5_data[19] + self.opp_r6_data[19]
      opp_data = [self.opp_pg_data, self.opp_sg_data, self.opp_sf_data, self.opp_pf_data, self.opp_c_data, self.opp_sxth_data, self.opp_r1_data, self.opp_r2_data, self.opp_r3_data, self.opp_r4_data, self.opp_r5_data, self.opp_r6_data]
      #opp_predictions_df = pd.DataFrame(data, columns = ['Name', 'Position', 'PTS', 'AST', 'TRB', 'ORB', 'DRB', 'FG', 'FGA', 'FG%', 'FT', 'FTA', 'FT%', '3P', '3PA', '3P%', 'STL', 'BLK', 'PF', 'TOV'])

      columns = ['Name', 'Position', 'PTS', 'AST', 'TRB', 'ORB', 'DRB', 'FG', 'FGA', 'FG%', 'FT', 'FTA', 'FT%', '3P', '3PA', '3P%', 'STL', 'BLK', 'PF', 'TOV']
      opp_predictions_df = pd.DataFrame(opp_data, columns = columns)
      for i in columns[2:]:
        opp_predictions_df[i] = [0 if x < 0 else x for x in opp_predictions_df[i]]
      opp_predictions_df['TRB'] = opp_predictions_df['ORB'] + opp_predictions_df['DRB']
      fgalst = []
      ftalst = []
      threeptalst = []
      for x,y in zip(opp_predictions_df['FG'], opp_predictions_df['FGA']):
        if x > y:
          y = x
        else:
          y = y
        fgalst.append(y)
      for x,y in zip(opp_predictions_df['FT'], opp_predictions_df['FTA']):
        if x > y:
          y = x
        else:
          y = y
        ftalst.append(y)
      for x,y in zip(opp_predictions_df['3P'], opp_predictions_df['3PA']):
        if x > y:
          y = x
        else:
          y = y
        threeptalst.append(y)
      opp_predictions_df['FGA'] = fgalst
      opp_predictions_df['FTA'] = ftalst
      opp_predictions_df['3PA'] = threeptalst
      opp_predictions_df['FG%'] = round(opp_predictions_df['FG']/opp_predictions_df['FGA'] * 100)
      opp_predictions_df['FT%'] = round(opp_predictions_df['FT']/opp_predictions_df['FTA'] * 100)
      opp_predictions_df['3P%'] = round(opp_predictions_df['3P']/opp_predictions_df['3PA'] * 100)
      opp_predictions_df['FG%'] = [0 if x == 'NaN' else x for x in opp_predictions_df['FG%']]
      opp_predictions_df['FT%'] = [0 if x == 'NaN' else x for x in opp_predictions_df['FT%']]
      opp_predictions_df['3P%'] = [0 if x == 'NaN' else x for x in opp_predictions_df['3P%']]
      self.opp_minutes_lst = [self.opp_pg_minutes, self.opp_sg_minutes, self.opp_sf_minutes, self.opp_pf_minutes, self.opp_c_minutes, self.opp_sxth_minutes, self.opp_r1_minutes, self.opp_r2_minutes, self.opp_r3_minutes, self.opp_r4_minutes, self.opp_r5_minutes, self.opp_r6_minutes]
      self.opp_year_lst = [self.opp_pg_year, self.opp_sg_year, self.opp_sf_year, self.opp_pf_year, self.opp_c_year, self.opp_sxth_year, self.opp_r1_year, self.opp_r2_year, self.opp_r3_year, self.opp_r4_year, self.opp_r5_year, self.opp_r6_year]
      opp_predictions_df.insert(2, "Minutes", self.opp_minutes_lst, True)
      opp_predictions_df.insert(1, "Year", self.opp_year_lst, True)
      opp_predictions_df['Year'] = opp_predictions_df['Year'].astype('int')
      opp_predictions_df = opp_predictions_df.sort_values(by=['PTS'], ascending = False)
      opp_predictions_df = opp_predictions_df.append({'Name': 'Total/Average', 'Year': round(sum(self.opp_year_lst)/12), 'Position': '', 'Minutes': 240, 'PTS': round(opp_total_pt), 'AST': round(opp_total_ast), 'TRB': round(opp_total_trb), 'ORB': round(opp_total_orb), 'DRB': round(opp_total_drb), 'FG': round(opp_total_fg), 'FGA': round(opp_total_fga),'FG%': round(opp_total_fgp/5), 'FT': round(opp_total_ft),'FTA': round(opp_total_fta), 'FT%': round(opp_total_ftp/5), '3P': round(opp_total_3p),'3PA': round(opp_total_3pa), '3P%': round(opp_total_3pp/5), 'STL': round(opp_total_stl), 'BLK': round(opp_total_blk),  'PF': round(opp_total_opp_pf), 'TOV': round(opp_total_tov)}, ignore_index = True)
      
      return opp_predictions_df
