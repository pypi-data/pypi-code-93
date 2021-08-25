# [[file:../Empirics/cfe_estimation.org::df_utils][df_utils]]
# Tangled on Wed Aug 25 16:27:31 2021
import numpy as np
from scipy import sparse
import pandas as pd
from warnings import warn

def df_norm(a,b=None,ignore_nan=True,ord=None):
    """
    Provides a norm for numeric pd.DataFrames, which may have missing data.

    If a single pd.DataFrame is provided, then any missing values are replaced with zeros, 
    the norm of the resulting matrix is returned.

    If an optional second dataframe is provided, then missing values are similarly replaced, 
    and the norm of the difference is replaced.

    Other optional arguments:

     - ignore_nan :: If False, missing values are *not* replaced.
     - ord :: Order of the matrix norm; see documentation for numpy.linalg.norm.  
              Default is the Froebenius norm.
    """
    a=a.copy()
    if not b is None:
      b=b.copy()
    else:
      b=pd.DataFrame(np.zeros(a.shape),columns=a.columns,index=a.index)

    if ignore_nan:
        missing=(a.isnull()+0.).replace([1],[np.NaN]) +  (b.isnull()+0.).replace([1],[np.NaN]) 
        a=a+missing
        b=b+missing
    return np.linalg.norm(a.fillna(0).values - b.fillna(0).values)

def df_to_orgtbl(df,tdf=None,sedf=None,conf_ints=None,float_fmt='\\(%5.3f\\)',bonus_stats=None):
    """
    Returns a pd.DataFrame in format which forms an org-table in an emacs buffer.
    Note that headers for code block should include ":results table raw".

    Optional inputs include conf_ints, a pair (lowerdf,upperdf).  If supplied, 
    confidence intervals will be printed in brackets below the point estimate.

    If conf_ints is /not/ supplied but sedf is, then standard errors will be 
    in parentheses below the point estimate.

    If tdf is False and sedf is supplied then stars will decorate significant point estimates.
    If tdf is a df of t-statistics stars will decorate significant point estimates.

    if sedf is supplied, this creates some space for =bonus_stats= to be reported on each row.

    BUGS: Dataframes that have multiindex columns can't be nicely represented as orgmode tables, 
    but we do our best.
    """
    if len(df.shape)==1: # We have a series?
        df = pd.DataFrame(df) 

    # Test for duplicates in index
    if df.index.duplicated().sum()>0:
        warn('Dataframe index contains duplicates.')

    # Test for duplicates in columns
    if df.columns.duplicated().sum()>0:
        warn('Dataframe columns contain duplicates.')

    try: # Look for a multiindex
        levels = len(df.index.levels)
        names = ['' if v is None else v for v in df.index.names]
    except AttributeError: # Single index
        levels = 1
        names = [df.index.name if (df.index.name is not None) else '']

    def column_heading(df):
        try: # Look for multiindex columns
            collevels = len(df.columns.levels)
            colnames = ['' if v is None else v for v in df.columns.names]
        except AttributeError: # Single index
            collevels = 1
            colnames = [df.columns.name if (df.columns.name is not None) else '']

        if collevels == 1:
            s = '| ' + ' | '.join(names) + ' | ' + '|   '.join([str(s) for s in df.columns])+'  |\n|-\n'
        else:
            colhead = np.array(df.columns.tolist()).T
            lastcol = ['']*collevels
            for l,j in enumerate(colhead.T.copy()):
                for k in range(collevels):
                    if lastcol[k] == j[k]: colhead[k,l] = ''
                lastcol = j

            colhead = colhead.tolist()
            s = ''
            for k in range(collevels):
                if k < collevels - 1:
                    s += '| '*levels + ' | '
                else:
                    s += '| ' + ' | '.join(names) + ' | '
                s += ' | '.join(colhead[k]) + '  |\n'
            s += '|-\n'

        return s

    def se_linestart(stats,i):
        if stats is None: 
            return '|'*levels
        else:
            stats = stats.loc[i]
            assert levels >= len(stats), "Too many columns of bonus stats"
            line = ['']*(levels-len(stats)+1)
            line += stats.tolist()
            return ' | '.join(line) 

    s = column_heading(df)

    if (tdf is None) and (sedf is None) and (conf_ints is None):
        lastidx = ['']*levels
        for i in df.index:
            if levels == 1: # Normal index
                s += '| %s  ' % i
            else:
                for k in range(levels):
                    if lastidx[k] != i[k]:
                        s += '| %s ' % i[k]
                    else:
                        s += '| '
            lastidx =i 
    
            for j in df.columns: # Point estimates
                try:
                    entry='| '+float_fmt+' '
                    if np.isnan(df[j][i]):
                        s+='| --- '
                    else:
                        s+=entry % df[j][i]
                except TypeError:
                    s += '| %s ' % str(df[j][i])
            s+='|\n'
        return s
    elif not (tdf is None) and (sedf is None) and (conf_ints is None):
        lastidx = ['']*levels
        for i in df.index:
            if levels == 1: # Normal index
                s += '| %s  ' % i
            else:
                for k in range(levels):
                    if lastidx[k] != i[k]:
                        s += '| %s ' % i[k]
                    else:
                        s += '| '
            lastidx = i 

            for j in df.columns:
                try:
                    stars=(np.abs(tdf[j][i])>1.65) + 0.
                    stars+=(np.abs(tdf[j][i])>1.96) + 0.
                    stars+=(np.abs(tdf[j][i])>2.577) + 0.
                    stars = int(stars)
                    if stars>0:
                        stars='^{'+'*'*stars + '}'
                    else: stars=''
                except KeyError: stars=''
                entry='| '+float_fmt+stars+' '
                if np.isnan(df[j][i]):
                    s+='| --- '
                else:
                    s+=entry % df[j][i]
            s+='|\n'

        return s
    elif not (sedf is None) and (conf_ints is None): # Print standard errors on alternate rows
        if tdf is not False:
            try: # Passed in dataframe?
                tdf.shape
            except AttributeError:  
                tdf=df[sedf.columns]/sedf

        lastidx = ['']*levels
        for i in df.index:
            if levels == 1: # Normal index
                s += '| %s  ' % i
            else:
                for k in range(levels):
                    if lastidx[k] != i[k]:
                        s += '| %s ' % i[k]
                    else:
                        s += '| '
            lastidx = i 

            for j in df.columns: # Point estimates
                if tdf is not False:
                    try:
                        stars=(np.abs(tdf[j][i])>1.65) + 0.
                        stars+=(np.abs(tdf[j][i])>1.96) + 0.
                        stars+=(np.abs(tdf[j][i])>2.577) + 0.
                        stars = int(stars)
                        if stars>0:
                            stars='^{'+'*'*stars + '}'
                        else: stars=''
                    except KeyError: stars=''
                else: stars=''
                entry='| '+float_fmt+stars+'  '
                if np.isnan(df[j][i]):
                    s+='| --- '
                else:
                    s+=entry % df[j][i]
            s+='|\n' + se_linestart(bonus_stats,i)
            for j in df.columns: # Now standard errors
                s+='  '
                try:
                    if np.isnan(df[j][i]): # Pt estimate miss
                        se=''
                    elif np.isnan(sedf[j][i]):
                        se='(---)'
                    else:
                        se='(' + float_fmt % sedf[j][i] + ')' 
                except KeyError: se=''
                entry='| '+se+'  '
                s+=entry 
            s+='|\n'
        return s
    elif not (conf_ints is None): # Print confidence intervals on alternate rows
        if tdf is not False and sedf is not None:
            try: # Passed in dataframe?
                tdf.shape
            except AttributeError:  
                tdf=df[sedf.columns]/sedf
        lastidx = ['']*levels
        for i in df.index:
            if levels == 1: # Normal index
                s += '| %s  ' % i
            else:
                for k in range(levels):
                    if lastidx[k] != i[k]:
                        s += '| %s ' % i[k]
                    else:
                        s += '| ' 
            lastidx = i 

            for j in df.columns: # Point estimates
                if tdf is not False and tdf is not None:
                    try:
                        stars=(np.abs(tdf[j][i])>1.65) + 0.
                        stars+=(np.abs(tdf[j][i])>1.96) + 0.
                        stars+=(np.abs(tdf[j][i])>2.577) + 0.
                        stars = int(stars)
                        if stars>0:
                            stars='^{'+'*'*stars + '}'
                        else: stars=''
                    except KeyError: stars=''
                else: stars=''
                entry='| '+float_fmt+stars+' '
                if type(df[j][i]) is not str and np.isnan(df[j][i]):
                    s+='| --- '
                else:
                    s+=entry % df[j][i]
            s+='|\n' + se_linestart(bonus_stats,i)

            for j in df.columns: # Now confidence intervals
                s+='  '
                try:
                    ci='[' + float_fmt +','+ float_fmt + ']'
                    ci= ci % (conf_ints[0][j][i],conf_ints[1][j][i])
                except KeyError: ci=''
                entry='| '+ci+'  '
                s+=entry 
            s+='|\n'
        return s

def orgtbl_to_df(table, col_name_size=1, format_string=None, index=None, dtype=None):
  """
  Returns a pandas dataframe.
  Requires the use of the header `:colnames no` for preservation of original column names.

  - `table` is an org table which is just a list of lists in python.
  - `col_name_size` is the number of rows that make up the column names.
  - `format_string` is a format string to make the desired column names.
  - `index` is a column label or a list of column labels to be set as the index of the dataframe.
  - `dtype` is type of data to return in DataFrame.  Only one type allowed.
  """
  import pandas as pd

  if col_name_size==0:
    return pd.DataFrame(table)

  colnames = table[:col_name_size]

  if col_name_size==1:
    if format_string:
      new_colnames = [format_string % x for x in colnames[0]]
    else:
      new_colnames = colnames[0]
  else:
    new_colnames = []
    for colnum in range(len(colnames[0])):
      curr_tuple = tuple([x[colnum] for x in colnames])
      if format_string:
        new_colnames.append(format_string % curr_tuple)
      else:
        new_colnames.append(str(curr_tuple))

  df = pd.DataFrame(table[col_name_size:], columns=new_colnames)

  if index:
    df.set_index(index, inplace=True)

  return df

def balance_panel(df):
    """Drop households that aren't observed in all rounds."""
    pnl=df.to_panel()
    keep=pnl.loc[list(pnl.items)[0],:,:].dropna(how='any',axis=1).iloc[0,:]
    df=pnl.loc[:,:,keep.index].to_frame(filter_observations=False)
    df.index.names=pd.core.base.FrozenList(['Year','HH'])

    return df

def drop_missing(X,infinities=False):
    """
    Return tuple of pd.DataFrames in X with any 
    missing observations dropped.  Assumes common index.

    If infinities is false values of plus or minus infinity are 
    treated as missing values.
    """

    foo=pd.concat(X,axis=1)
    if not infinities:
        foo.replace(np.inf,np.nan)
        foo.replace(-np.inf,np.nan)

    foo = foo.dropna(how='any')

    assert len(set(foo.columns))==len(foo.columns) # Column names must be unique!

    Y=[]
    for x in X:
        Y.append(foo.loc[:,pd.DataFrame(x).columns]) 

    return tuple(Y)

def use_indices(df,idxnames):
    return df.reset_index()[idxnames].set_index(df.index)
# df_utils ends here

# [[file:../Empirics/cfe_estimation.org::*Some econometric routines][Some econometric routines:1]]
# Tangled on Wed Aug 25 16:27:31 2021
import xarray as xr
from scipy.linalg import block_diag

def arellano_robust_cov(X,u,clusterby=['t','m'],tol=1e-12):
    """
    Compute clustered estimates of covariance matrix, per Arellano (1987).
    Estimates of variance of fixed effects use OLS estimator.
    """
    X,u = drop_missing([X,u])
    clusters = set(zip(*tuple(use_indices(u,clusterby)[i] for i in clusterby)))
    if  len(clusters)>1:
        # Take out time averages
        ubar = u.groupby(level=clusterby).transform(np.mean)
        Xbar = X.groupby(level=clusterby).transform(np.mean)
    else:
        ubar = u.mean()
        Xbar = X.mean()

    ut = (u - ubar).squeeze()
    Xt = X - Xbar

    # Pull out columns spanned by cluster vars to get var of FEs
    Cvars = Xt.columns[Xt.std()<tol]
    Xvars = Xt.columns[Xt.std()>=tol]
    if len(Cvars):
        _,v = ols(X.loc[:,Cvars],u,return_se=False,return_v=True)

    Xt = Xt.drop(columns=Cvars)

    Xu=Xt.mul(ut,axis=0)

    if len(Xt.shape)==1:
        XXinv=np.array([1./(Xt.T.dot(Xt))])
    else:
        XXinv=np.linalg.inv(Xt.T.dot(Xt))
    Vhat = XXinv.dot(Xu.T.dot(Xu)).dot(XXinv)

    try:
        Allvars = Cvars.values.tolist() + Xvars.values.tolist()
        if len(Cvars):
            V = xr.DataArray(block_diag(v.squeeze('variable').values,Vhat),dims=['k','kp'],coords={'k':Allvars,'kp':Allvars})
        else:
            V = xr.DataArray(Vhat,dims=['k','kp'],coords={'k':Allvars,'kp':Allvars})
        return V
    except AttributeError:
        if len(Cvars):
            return v,Vhat
        else:
            return Vhat


def ols(x,y,return_se=True,return_v=False,return_e=False):
    """Produce OLS estimates of b in $y = xb + u$.

    If standard errors (return_se=True) or covariance matrices
    (return_v=True) are returned, these are Seemingly Unrelated
    Regression (SUR) estimates if y has multiple columns, or the
    simple OLS estimator var(u)(X'X)^{-1} otherwise.
    """

    x=pd.DataFrame(x) # Deal with possibility that x & y are series.
    y=pd.DataFrame(y)
    # Drop any observations that have missing data in *either* x or y.
    x,y = drop_missing([x,y]) 

    N,n=y.shape
    k=x.shape[1]

    b=np.linalg.lstsq(x,y,rcond=0)[0]

    b=pd.DataFrame(b,index=x.columns,columns=y.columns)

    out=[b]
    if return_se or return_v or return_e:

        u=y-x.dot(b)
        assert u.shape == (N,n), "Dimensions of disturbance not as expected"      

        if return_se or return_v:
            Sigma = u.T@u/N
            XXinv = np.linalg.inv(x.T@x)
            V = np.kron(Sigma,XXinv)

        if return_se:
            se=np.sqrt(V.diagonal()).reshape((x.shape[1],y.shape[1]))
            se=pd.DataFrame(se,index=x.columns,columns=y.columns)

            out.append(se)
        if return_v:
            # Extract blocks along diagonal; return a k x kp x n array
            col0 = x.columns
            col1 = col0.rename(name='kp')
            v = {y.columns[i]:pd.DataFrame(V[i*k:(i+1)*k,i*k:(i+1)*k],index=col0,columns=col1) for i in range(n)}
            V = xr.Dataset(v).to_array()
            out.append(V)

        if return_e:
            out.append(u)
    return tuple(out)
# Some econometric routines:1 ends here

# [[file:../Empirics/cfe_estimation.org::broadcast_binary_op][broadcast_binary_op]]
# Tangled on Wed Aug 25 16:27:31 2021
def merge_multi(df1, df2, on):
    """Merge on subset of multiindex.
   
    Idea due to http://stackoverflow.com/questions/23937433/efficiently-joining-two-dataframes-based-on-multiple-levels-of-a-multiindex
    """
    return df1.reset_index().join(df2,on=on).set_index(df1.index.names)

def broadcast_binary_op(x, op, y):
    """Perform x op y, allowing for broadcasting over a multiindex.

    Example usage: broadcast_binary_op(x,lambda x,y: x*y ,y)
    """
    x = pd.DataFrame(x.copy())
    y = pd.DataFrame(y.copy())
    xix= x.index.copy()

    if y.shape[1]==1: # If y a series, expand to match x.
        y=pd.DataFrame([y.iloc[:,0]]*x.shape[1],index=x.columns).T

    cols = list(x.columns)
    xindex = list(x.index.names)
    yindex = list(y.index.names)

    dif = list(set(xindex)-set(yindex))

    z = pd.DataFrame(index=xix)
    z = merge_multi(z,y,on=yindex)

    newdf = op(x[cols],z[cols])

    return newdf
# broadcast_binary_op ends here

# [[file:../Empirics/cfe_estimation.org::*Utility functions related to transformations between xarray and pandas objects][Utility functions related to transformations between xarray and pandas objects:1]]
# Tangled on Wed Aug 25 16:27:31 2021
import xarray as xr

def is_none(x):
    """
    Tests for None in an array x.
    """
    try:
        if np.any(np.equal(x,None)):
            return True
    except TypeError:
        return is_none(x.data)
    else:
        try:
            if len(x.shape)==0:
                return True
        except AttributeError:
            if isinstance(x,str):
                if len(x)==0: return True
                else: return False
            elif np.isscalar(x): return x is None
            elif isinstance(x,list): return None in x
            else:
                raise(TypeError,"Problematic type.")

def to_dataframe(arr,column_index=None,name=None,dropna_all=True):
    """Convert =xarray.DataArray= into a =pd.DataFrame= with indices etc. usable by =cfe=.
    """

    if name is None:
        dims = arr.dims
        df = arr.to_dataset(name='').to_dataframe(dims).squeeze()
        df.name = None
        df.index.names = dims # Deal with xarray bug in to_dataframe that drops index names?
    else:
        df = arr.to_dataframe(name)

    if column_index is not None:
        df = df.unstack(column_index)

    if dropna_all:
        df.dropna(how='all',inplace=True)

    return df

def from_dataframe(df,index_name=None):
    """Convert from dataframe used in cfe.estimation to xarray.DataArray.
    """
    if index_name is not None:
        df.index = df.index.set_names(index_name)

    df = pd.DataFrame(df) # Series to dataframe
    if not is_none(df.columns.names):
        df = df.stack(df.columns.names)

    arr = df.squeeze().to_xarray()

    return arr
# Utility functions related to transformations between xarray and pandas objects:1 ends here
