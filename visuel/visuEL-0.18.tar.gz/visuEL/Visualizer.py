import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.colors import rgb2hex
import svgwrite
from visuEL.Sampler import CminSampler

class Vis:
    width_in_block = 20
    padding = 5
    square_s = 50

    def __init__(self, mapping_name=None, legend=True, max_n_color=6, max_seq=5000, activities=None):
        self.mapping_name = mapping_name
        self.legend = legend
        self.max_n_color = int(max_n_color)
        self.svg = None
        self.activities = activities
        self.max_seq = max_seq
        self.n_cases = None

    def _load(self, variants):
        sampler = CminSampler(variants, 0)
        self.n_cases = variants.sum()
        sampling = sampler.sample(max_seq=self.max_seq)

        if not self.activities:
            self.activities = self.activity_definition(sampling)
        else:

            last_row = None
            highest_ranking = 0
            for v in self.activities.values():
                if v['ranking']>highest_ranking:
                    highest_ranking = v['ranking']
                    last_row = v
            for k,v in self.activity_definition(sampling).items():
                if k not in self.activities:
                    self.activities[k] = last_row
                    self.activities[k]['o_name'] = k
        self.svg = self._build_svg(sampling)


    def load_variants(self, variants):
        self._load(variants)

    def load_seqs(self, seqs):
        seqs = [[str(y) for y in x] for x in seqs]
        self._load(pd.Series(seqs).value_counts())

    def activity_definition(self, sampling):

        # Count activities
        y = pd.Series([y for x in sampling for y in x]).value_counts().to_frame()

        # Prepare dataframe
        y.columns = ['count']
        y.index.name = 'name'
        y = y.reset_index()
        y = y.sort_values(by=['count','name'], ascending=[False, True])

        # Assign color
        n_color = min(self.max_n_color, y.shape[0])
        palette = plt.get_cmap('magma', n_color+1)
        colors = [rgb2hex(palette(x)) for x in range(n_color)]
        y['color'] = colors[-1]
        y.loc[y.iloc[0:n_color].index, 'color'] = colors

        # Map potential name
        mapping = {x:x for x in y['name'].tolist()}
        if self.mapping_name:
            for k,v in self.mapping_name.items():
                if k in mapping.keys():
                    mapping[k] = v
        y.index = y['name'].tolist()
        y['o_name'] = y['name'].copy()
        y['name'] = y['name'].map(mapping)
        y['ranking'] = np.arange(y.shape[0])

        if y.shape[0] > self.max_n_color:
            y.loc[y.iloc[n_color-1:].index, 'name'] = '+ {} others...'.format(y.shape[0]-n_color+1)
            y.loc[y.iloc[n_color-1:].index, 'color'] = '#eee'
        return y.to_dict(orient='index')

    def _build_svg(self, sampling):
        n = len(sampling)
        if self.legend:
            n += min(self.max_n_color, len(self.activities)) + 2

        height = n*(self.padding+self.square_s) +40
        width = self.width_in_block * self.square_s

        d = svgwrite.Drawing('test.svg', profile='tiny', size=(width, height))
        for row, trace in enumerate(sampling):
            for col, activity in enumerate(trace):
                top = (((row)*self.square_s) + ((row)*self.padding+1)) + 40
                if len(trace) > self.width_in_block:
                    if col == len(trace) - 2:
                        left = (self.width_in_block - 2)*self.square_s
                        r = self.square_s/15
                        d.add(d.circle((left+(self.square_s/2), top+(self.square_s/2)), r, fill='#000000'))
                        d.add(d.circle((left+(self.square_s/2)-(r*3), top+(self.square_s/2)), r, fill='#000000'))
                        d.add(d.circle((left+(self.square_s/2)+(r*3), top+(self.square_s/2)), r, fill='#000000'))
                        continue
                    if col == len(trace)-1:
                        left = (self.width_in_block - 1)*self.square_s
                        d.add(d.rect((left, top), (self.square_s, self.square_s), fill=self.activities[trace[-1]]['color']))
                        continue
                    if col > self.width_in_block - 3:
                        continue
                left = col*self.square_s
                d.add(d.rect((left, top), (self.square_s, self.square_s), fill=self.activities[activity]['color']))

        font_size = self.square_s*0.6
        d.add(d.text('{} cases'.format(self.n_cases),  insert=(0, 25), fill='black', font_size=font_size,))
        if self.legend:

            for i, v in enumerate(self.activities.values()):
                if v['ranking']>=self.max_n_color:
                    continue
                t = (top + ((self.square_s + self.padding)*(v['ranking']+2)))
                d.add(d.rect((0, t), (self.square_s*0.8, self.square_s*0.8), fill=v['color']))
                d.add(d.text(v['name'],  insert=(self.square_s, t+(self.square_s*0.6)), fill='black', font_size=font_size,))
        d.viewbox(0, 0, width, height)
        d.fit(horiz='left', vert='top', scale='meet')
        return d

    def get_svg(self):
        return self.svg.tostring()

    def save_svg(self, path):
        with open(path, 'w') as f:
            f.write(self.get_svg())
