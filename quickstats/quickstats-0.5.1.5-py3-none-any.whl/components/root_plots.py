from typing import Optional, Dict
import ROOT
import numpy as np

     
def set_attrib(obj, **kwargs):
    for key, value in kwargs.items():
        target = obj
        if '.' in key:
            tokens = key.split('.')
            if len(tokens) != 2:
                raise ValueError('maximum of 1 subfield is allowed but {} is given'.format(len(tokens)-1))
            field, key = tokens[0], tokens[1]
            method_name = 'Get' + field
            if hasattr(obj, 'Get' + field):
                target = getattr(obj, method_name)()
            else:
                raise ValueError('{} object does not contain the method {}'.format(type(target), method_name)) 
        method_name = 'Set' + key
        if hasattr(target, 'Set' + key):
            method_name = 'Set' + key
        elif hasattr(target, key):
            method_name = key
        else:
            raise ValueError('{} object does not contain the method {}'.format(type(target), method_name))         
        if value is None:
            getattr(target, method_name)()
        elif isinstance(value, (list, tuple)):
            getattr(target, method_name)(*value)
        else:
            getattr(target, method_name)(value)
    return obj

class StandardGraphMaker(object):
    @staticmethod
    def GraphAsymErrors(n:int, x:np.ndarray, y:np.ndarray, xerr_lo:Optional[np.ndarray]=None,
                        xerr_hi:Optional[np.ndarray]=None, yerr_lo:Optional[np.ndarray]=None,
                        yerr_hi:Optional[np.ndarray]=None, title:str="", xtitle:str="", ytitle:str="",
                        options:Dict={}):
        xerr_hi = xerr_hi if xerr_hi is not None else np.zeros(len(x))
        xerr_lo = xerr_lo if xerr_lo is not None else np.zeros(len(x))
        yerr_hi = yerr_hi if yerr_hi is not None else np.zeros(len(x))
        yerr_lo = yerr_lo if yerr_lo is not None else np.zeros(len(x))
        graph = ROOT.TGraphAsymmErrors(n, x, y, xerr_lo, xerr_hi, yerr_lo, yerr_hi)
        graph.SetTitle(title)
        graph.GetXaxis().SetTitle(xtitle)
        graph.GetYaxis().SetTitle(ytitle)
            
        return set_attrib(graph, **options)
    
    @staticmethod
    def TH2F(name:str, title:str, n_x:int, n_y:int, x_lo:Optional[float]=None,
             x_hi:Optional[float]=None, y_lo:Optional[float]=None,
             y_hi:Optional[float]=None, x_bins: Optional[np.ndarray]=None,
             y_bins: Optional[np.ndarray]=None, options:Dict={}):
        if (x_lo is None) and (x_hi is None) and (y_lo is None) and (y_hi is None):
            hist = ROOT.TH2F(name, title, n_x, x_bins, n_y, y_bins)
        elif (x_lo is None) and (x_hi is None) and (y_bins is None):
            hist = ROOT.TH2F(name, title, n_x, x_bins, n_y, y_lo, y_hi)
        elif (y_lo is None) and (y_hi is None) and (x_bins is None):
            hist = ROOT.TH2F(name, title, n_x, x_lo, x_hi, n_y, y_bins)            
        elif (y_bins is None) and (x_bins is None):
            hist = ROOT.TH2F(name, title, n_x, x_lo, x_hi, n_y, y_lo, y_hi)
        else:
            raise ValueError('cannot convert arguments for TH2F')
        return set_attrib(hist, **options)
    
    @staticmethod
    def TGaxis(x_min:float, y_min:float, x_max:float, y_max:float, w_min:float,
               w_max:float, n_div:int=510, chopt:str="", grid_length:float=0.0,
               options:Dict={}):
        axis = ROOT.TGaxis(x_min, y_min, x_max, y_max, w_min, w_max, n_div, chopt, grid_length)
        return set_attrib(axis, **options)
    
    @staticmethod                 
    def TLine(x1:Optional[float]=None, y1:Optional[float]=None, 
              x2:Optional[float]=None, y2:Optional[float]=None, options:Dict={}):
        if (x1 is None) and (y1 is None) and (x2 is None) and (y2 is None):
            line = ROOT.TLine()
        else:
            line = ROOT.TLine(x1, y1, x2, y2)
        return set_attrib(line, **options)
    
    @staticmethod
    def TLegend(x1:Optional[float]=None, y1:Optional[float]=None, 
                x2:Optional[float]=None, y2:Optional[float]=None,
                w:Optional[float]=None, h:Optional[float]=None,
                header:str="", option:str="", options:Dict={}):
        if (x1 is None) and (y1 is None) and (x2 is None) and (y2 is None):
            legend = ROOT.TLegend(w, h, header, option)
        else:
            legend = ROOT.TLegend(x1, y1, x2, y2, header, option)
        return set_attrib(legend, **options)
    
    @staticmethod
    def TLatex(options:Dict={}):
        latex = ROOT.TLatex()
        return set_attrib(latex, **options)