import trifacta as tf


class TestWfClass:
    # runJob: exercised by tfobjects

    def test_profile(self, wf):
        prof = wf.profile()
        wf.profile()  # exercise the cache line
        assert (len(prof['profilerTypeCheckHistograms']) == 2)
        assert (len(prof['columnTypes']) == 2)
        assert (len(prof['profilerValidValueHistograms']) == 2)

    def test_profile2(self, wf2):
        prof = wf2.profile()
        wf2.profile()  # exercise the cache line
        assert (len(prof['profilerTypeCheckHistograms']) == 2)
        assert (len(prof['columnTypes']) == 2)
        assert (len(prof['profilerValidValueHistograms']) == 2)

    def test_dqBars(self, wf):
        dq = wf.dq_bars()
        cols = set(dq.columns)
        assert (len(dq) == 2)  # one per column of df
        assert (len(cols) == 3)  # VALID, INVALID, EMPTY
        assert (cols == set(['VALID', 'INVALID', 'EMPTY']))

        dq = wf.dq_bars(False)
        cols = set(dq.columns)
        assert (len(dq) == 2)  # one per column of df
        assert (len(cols) == 3)  # VALID, INVALID, EMPTY
        assert (cols == set(['VALID', 'INVALID', 'EMPTY']))

    def test_colTypes(self, wf):
        types = wf.col_types()
        assert (types['type'][0] == 'String')
        assert (types['type'][1] == 'Integer')

    def test_barsDfList(self, wf):
        columns = wf.bars_df_list()
        assert (len(columns) == 2)
        assert (columns[0]['count'].sum() == 3)
        assert (len(columns[0].columns) == 1)
        assert (columns[1]['count'].sum() == 3)
        assert (len(columns[1].columns) == 1)

    def test_summary(self, wf):
        s = wf.summary()
        assert (len(s) == 2)
        assert (set(s.columns) == set(['type', 'roundMin', 'roundMax', 'max', 'min', 'q1', 'q2', 'q3', 'ub', 'c', 'k']))
        assert (s['roundMin'].count() == 1)  # only 1 numeric column
        assert (s['ub'].count() == 1)  # only 1 categorical

    # def test_pdfProfile(self, wf, tmpdir):
    #     filepath = tmpdir.join("output.pdf")
    #     wf.pdfProfile(filepath)
    #     wf.pdfProfile(filepath) # exercise cached case
    #     with open(filepath, "rb") as f:
    #         pdf = pdftotext.PDF(f)
    #     assert(pdf[0][0:6] == 'Report')

    def test_output(self, df, wf, tmpdir):
        assert (wf.output(tmpdir.join("output.csv")).to_csv(header=False) == df.to_csv(header=False))
        wf.cache['outDf'] = None  # reset the df cache to test the tempfile construction
        assert (wf.output().to_csv(header=False) == df.to_csv(header=False))
        assert (wf.output().to_csv(header=False) == df.to_csv(header=False))

    # run last, as it forces recomputing tfobjects on next call
    # REMOVED as it returns 401 for 
    #      {'exception': {'name': 'MissingPersonException', 'message': 'Person is missing'}}
    # def test_open(self, wf):
    #     url = wf.open(True)
    #     r = requests.get(url, auth=tfr.get_auth())
    #     assert(r.status_code == 200)

    def test_multiple(self, wfmany):
        # same as test_profile
        assert (len(wfmany.recipe_names()) == 3)
        prof = wfmany.profile()
        assert (len(prof['profilerTypeCheckHistograms']) == 2)
        assert (len(prof['columnTypes']) == 2)
        assert (len(prof['profilerValidValueHistograms']) == 2)
        prof2 = wfmany.profile(recipe_name=wfmany.recipe_names()[2])
        assert (len(prof2['profilerTypeCheckHistograms']) == 3)
        assert (len(prof2['columnTypes']) == 3)
        assert (len(prof2['profilerValidValueHistograms']) == 3)

    def test_existing(self, wfmany):
        wfnew = tf.wrangle_existing(wfmany.flow_id)
        prof1 = wfmany.profile(recipe_name=wfmany.recipe_names()[1])
        assert (len(prof1['profilerTypeCheckHistograms']) == 2)
        assert (len(prof1['columnTypes']) == 2)
        assert (len(prof1['profilerValidValueHistograms']) == 2)
