from .asset_painter import *
import seaborn as sns

class PortPainter(object):

    @staticmethod
    def plot_mdd(df):
        def rolling_cur_mdd(x):
            if pd.isnull(x).all():
                return np.nan
            x_max = np.fmax.accumulate(x, axis=0)
            return -(1 - np.nanmin(x[-1] / x_max))
        
        mdd_df = df.rolling(window=df.shape[0],min_periods=2).apply(rolling_cur_mdd, raw=True)
        mdd_df.plot(figsize=(16,12),fontsize=20)
        plt.title('策略当前回撤对比',fontsize=25)
        plt.legend(loc='upper left',fontsize=15, bbox_to_anchor=(1,1))
        plt.grid()
        plt.show()
        return mdd_df

    @staticmethod
    def plot_corr(df):
        sns.set(font_scale=2,font='STKaiti')
        plt.figure(figsize=(14,10))
        sns.heatmap(df.pct_change(1).dropna().corr(),cmap='Blues', annot=True)
        plt.show()
        return df