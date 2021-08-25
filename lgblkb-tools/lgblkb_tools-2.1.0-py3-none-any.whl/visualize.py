import itertools as it

import matplotlib.pyplot as plt
import numpy as np
from box import Box


class Plotter(object):
    def __init__(self, *objs, axis_off=True, as_images=True, **plot_kwargs):
        self.data = list()
        self.axis_off = axis_off
        if objs:
            if as_images:
                self.add_images(*objs).plot(**plot_kwargs).show()
            else:
                self.add_plots(*objs).plot(**plot_kwargs).show()
        pass
    
    def _add_obj(self, obj, ax_callback, plot_kwargs, **kwargs):
        self.data.append(Box(obj=obj, plot_kwargs=plot_kwargs, ax_callback=ax_callback, **kwargs))
        return self
    
    # region Front:
    def add_image(self, obj=None, ax_callback=None, **plot_kwargs):
        return self._add_obj(obj, ax_callback, plot_kwargs, as_image=True, single=True)
    
    def add_images(self, *objs, ax_callback=None, **plot_kwargs):
        for obj in objs:
            self.add_image(obj, ax_callback=ax_callback, **plot_kwargs)
        return self
    
    def add_plot(self, obj=None, ax_callback=None, **plot_kwargs):
        return self._add_obj(obj, ax_callback, plot_kwargs, as_image=False, single=True)
    
    def add_plots(self, *objs, ax_callback=None, **plot_kwargs):
        for obj in objs:
            self.add_plot(obj, ax_callback=ax_callback, **plot_kwargs)
        return self
    
    # endregion
    
    @staticmethod
    def get_grid_dims(obj_count, nrows=None, ncols=None):
        col_count = np.sqrt(obj_count * 16 / 9)
        if nrows is None:
            if ncols:
                nrows = max(1, np.ceil(obj_count / ncols))
            else:
                nrows = max(1, np.round(obj_count / col_count))
        if ncols is None:
            ncols = np.ceil(obj_count / nrows)
        
        pair = list(map(int, [nrows, ncols]))
        # logger.debug('nrows,ncols for %s images: %s',images_count,pair)
        return pair
    
    def plot(self, overlay=False, nrows_cols=None, horizontal=True, lbrtwh=(), **subplot_kwargs):
        if nrows_cols is None:
            if overlay:
                nrows, ncols = 1, 1
            else:
                nrows = subplot_kwargs.pop('nrows', None)
                ncols = subplot_kwargs.pop('ncols', None)
                nrows, ncols = self.get_grid_dims(len(self.data), nrows=nrows, ncols=ncols)
                if len(self.data) > nrows * ncols:
                    raise ValueError(
                        f'Insufficient number of axes ({nrows * ncols}) for {len(self.data)} objects.')
        else:
            nrows, ncols = nrows_cols
        fig, axs = plt.subplots(nrows, ncols, **subplot_kwargs)
        if nrows * ncols == 1:
            axs = [axs]
        else:
            if horizontal:
                axs = axs.flatten()
            else:
                axs = axs.T.flatten()
        
        for ax, datum in it.zip_longest(axs, self.data, fillvalue=axs[0] if overlay else None):
            if self.axis_off: ax.set_axis_off()
            if datum is None:
                fig.delaxes(ax)
                continue
            obj = datum.obj
            if obj is not None:
                if datum.as_image:
                    if datum.single:
                        assert isinstance(datum.plot_kwargs, dict)
                        ax.imshow(obj, **datum.plot_kwargs)
                    else:
                        objs = obj
                        if isinstance(datum.plot_kwargs, dict): datum.plot_kwargs = [datum.plot_kwargs]
                        for obj, plot_kwargs in it.zip_longest(objs, datum.plot_kwargs,
                                                               fillvalue=datum.plot_kwargs[-1]):
                            ax.imshow(obj, **plot_kwargs)
                else:
                    if datum.single:
                        if len(obj.shape) == 2:
                            assert isinstance(datum.plot_kwargs, dict)
                            ax.plot(*obj, **datum.plot_kwargs)
                        else:
                            ax.plot(obj, **datum.plot_kwargs)
                    else:
                        objs = obj
                        if isinstance(datum.plot_kwargs, dict): datum.plot_kwargs = [datum.plot_kwargs]
                        for obj, plot_kwargs in it.zip_longest(objs, datum.plot_kwargs,
                                                               fillvalue=datum.plot_kwargs[-1]):
                            if len(obj.shape) == 2:
                                ax.plot(*obj, **plot_kwargs)
                            else:
                                ax.plot(obj, **plot_kwargs)
            
            if datum.ax_callback is not None: datum.ax_callback(ax)
        
        fig.set_size_inches(18, 10)
        if lbrtwh:
            plt.subplots_adjust(*lbrtwh)
        return self
    
    @staticmethod
    def show(*args, **kwargs):
        return plt.show(*args, **kwargs)
    
    def save(self, savepath, *args, **kwargs):
        plt.savefig(savepath, *args, **kwargs)
        plt.close()
        return self
    
    def __len__(self):
        return len(self.data)


def main():
    pass


if __name__ == '__main__':
    main()
