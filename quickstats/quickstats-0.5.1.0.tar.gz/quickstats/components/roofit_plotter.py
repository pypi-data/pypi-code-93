from typing import List
from copy import deepcopy
from quickstats.components.root_plots import set_attrib
        
import ROOT

class RooFitPlotter(object):
    
    _DEFAULT_BOX_OPTIONS_ = {
        'FillColor'  : 0,
        'BorderSize' : 0,
        'TextAlign'  : 12,
        'TextSize'   : 0.04,
        'FillStyle'  : 1001
    }
    
    _DEFAULT_TEXTS_ = ['ATLAS #bf{Internal}', '#sqrt{s} = 13 TeV, L=139fb^{-1}']

    def __init__(self, x, data, model, name='roofit_plot'):
        self.x = x
        self.data = data
        self.model = model
        self.name = name
        
    def setup_canvas(self):
        canvas_name = 'c_{}'.format(self.name)
        if not ROOT.gROOT.FindObject(canvas_name):
            self.canvas = ROOT.TCanvas(canvas_name, canvas_name,800,600)
        else:
            self.canvas = ROOT.gROOT.FindObject(canvas_name)

        self.canvas.Clear()
        self.canvas.Divide(1, 2)
        self.canvas.GetPad(1).SetPad(0.0, 0.25, 1, 1)
        self.canvas.GetPad(1).SetBottomMargin(0.05)
        self.canvas.GetPad(1).SetRightMargin(0.05)
        self.canvas.GetPad(1).SetTicks(1, 1)
        self.canvas.GetPad(2).SetPad(0.0, 0.0, 1, 0.25)
        self.canvas.GetPad(2).SetBottomMargin(0.32)
        self.canvas.GetPad(2).SetTopMargin(0.05)
        self.canvas.GetPad(2).SetRightMargin(0.15)
        self.canvas.GetPad(2).SetRightMargin(0.05)
        self.canvas.GetPad(2).SetTicks(1, 1)
        
        self.legend = ROOT.TLegend(0.63, 0.70, 0.85, 0.85)
        self.legend.SetBorderSize(0)
        self.label = ROOT.TLatex()
    
    def plot_text(self, texts, name=None, box_options=None, x_min=0.1,
                  x_max=0.3, y_max=0.85, dy=0.06):
        
        n_lines = len(texts)
        y_min = y_max - dy * n_lines
        
        # create text box
        box = ROOT.TPaveText(x_min, y_max, x_max, y_min,"BRNDC");
        if not box:
            return 0
        if name is None:
            box.SetName('new_textBox')
        else:
            box.SetName(name)
        
        set_attrib(box, **self._DEFAULT_BOX_OPTIONS_)
        if box_options:
            set_attrib(box, **box_options)
        
        # add labels
        for text in texts:
            box.AddText(text)
    
        self.frame.addObject(box)
    
        return box
        
    def plot_param(self, params=None, show_constants=False, labels=None,
                   name=None, box_options=None, precision=3,
                   x_min=0.6, x_max=0.99, y_max=0.85, dy=0.06):
        
        parameters = self.model.getParameters(self.data)
        if params is not None:
            parameters = [p for p in parameters if p.GetName() in params]
        if not show_constants:
            parameters = [p for p in parameters if not p.isConstant()]
        param_format = ROOT.RooFit.Format("NEU", ROOT.RooFit.AutoPrecision(precision))
        parameter_text = [p.format(param_format).Data() for p in parameters]
        
        if labels:
            parameter_text += labels
            
        if not name:
            name = '{}_paramBox'.format(self.model.GetName())
            
        return self.plot_text(parameter_text, name=name, box_options=box_options,
                              x_min=x_min, x_max=x_max, y_max=y_max, dy=dy)
        
    @staticmethod
    def get_relative_hist(frame, histname, curvename, threshold=None, epsilon=1e-7):
        hist = frame.findObject(histname)
        curve = frame.findObject(curvename)
        rel_hist = ROOT.RooHist(hist.getNominalBinWidth())
        #rel_hist.SetName('relative_error_{}_{}'.format(hist.GetName(), curve.GetName()))
        #rel_hist.SetTitle('relative error of {} and {}'.format(hist.GetTitle(), curve.GetTitle()))

        #Determine range of curve
        xstart, xstop, y = ROOT.Double(), ROOT.Double(), ROOT.Double()
        curve.GetPoint(0, xstart, y)
        curve.GetPoint(curve.GetN()-1, xstop, y)
        n_bin = hist.GetN()
        for i in range(n_bin):
            x = ROOT.Double()
            point = ROOT.Double()
            hist.GetPoint(i, x, point)
            if (x < xstart) or (x > xstop):
                continue
            yy = ROOT.Double()
            #yy = 1 - data/fit
            fit_value = curve.interpolate(x)
            if abs(point) <= epsilon:
                yy = 0
            else:
                yy = (fit_value - point)/point
            if threshold and abs(yy) > threshold:
                continue
            if abs(point) <= epsilon:
                dyl = 0
                dyh = 0
            else:
                dyl = hist.GetErrorYlow(i)/fit_value
                dyh = hist.GetErrorYhigh(i)/fit_value
            rel_hist.addBinWithError(x, yy, dyl, dyh)
        return rel_hist
    
    def create_ratio(self, x_title="m_{#gamma#gamma}[GeV]", label_scale=1.0,
                     marker_size = 0.4, threshold = 1.0):
        self.canvas.cd(2)
        self.h_ratio = self.get_relative_hist(self.frame, 'data', 'fit',
                                              threshold=threshold)
        self.h_ratio.SetMarkerSize(0.4)
        self.h_ratio.SetMarkerColor(ROOT.kRed)
        self.ratio_frame = self.x.frame(ROOT.RooFit.Title(" "))
        self.ratio_frame.addPlotable(self.h_ratio, "P")
        
        self.ratio_frame.SetXTitle(x_title)
        self.ratio_frame.GetYaxis().SetTitle("Relative Error")
        self.ratio_frame.GetYaxis().CenterTitle()
        self.ratio_frame.GetXaxis().SetTitleSize(0.12)
        self.ratio_frame.GetYaxis().SetTitleSize(0.1)
        self.ratio_frame.GetYaxis().SetTitleOffset(0.4)
        self.ratio_frame.GetXaxis().SetTitleOffset(1.3)
        self.ratio_frame.GetXaxis().SetLabelSize(0.12 * label_scale)
        self.ratio_frame.GetYaxis().SetLabelSize(0.12 * label_scale)
        self.ratio_frame.GetYaxis().SetLabelOffset(0.006)
        self.ratio_frame.GetYaxis().SetRangeUser(-1.0, 1.0)
        
        self.ratio_frame.GetXaxis().SetLabelFont(2)
        self.ratio_frame.GetXaxis().SetTitleFont(2)
        self.ratio_frame.GetXaxis().SetLabelFont(2)
        
    def format_ticks(self, tick_len=20):
        ### Equal sized ticks!!
        pad1 = self.canvas.GetPad(1)
        pad2 = self.canvas.GetPad(2)

        pad1W = pad1.GetWw() * pad1.GetAbsWNDC()
        pad1H = pad1.GetWh() * pad1.GetAbsHNDC()
        pad2W = pad2.GetWw() * pad2.GetAbsWNDC()
        pad2H = pad2.GetWh() * pad2.GetAbsHNDC()
        
        #self.ratio_frame.GetXaxis().SetTickLength(self.ratio_frame.GetXaxis().GetTickLength() * 3.0)
       
        self.frame.GetYaxis().SetNdivisions(1005)
        self.ratio_frame.GetYaxis().SetNdivisions(505)
        self.frame.GetXaxis().SetNdivisions(1010)
        self.ratio_frame.GetXaxis().SetNdivisions(1010)

        self.frame.SetTickLength(tick_len/pad1W, "Y")
        self.frame.SetTickLength(tick_len/pad1H, "X")
        self.ratio_frame.SetTickLength(tick_len/pad2W, "Y")
        self.ratio_frame.SetTickLength(tick_len/pad2H, "X")
        
    def draw_labels(self, labels):
        self.canvas.cd(1)
        self.label.SetTextSize(0.1);
        self.label.SetTextAlign(13);
        for i, label in enumerate(labels):
            self.label.DrawLatex(0.36, 0.9-0.0275*i, label)
        
    def plot(self, x_title="m_{#gamma#gamma}[GeV]",
             marker_size = 0.3, line_width=2, label_scale=1.0,
             ratio_marker_size = 0.4, labels=None):
        self.setup_canvas()
        self.canvas.cd(1)
        self.frame = self.x.frame(ROOT.RooFit.Title(" "))
        self.data.plotOn(self.frame, ROOT.RooFit.Name("data"), 
                         ROOT.RooFit.MarkerSize(marker_size),
                         ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
        self.model.plotOn(self.frame, ROOT.RooFit.Name("fit"), 
                          ROOT.RooFit.LineWidth(line_width), 
                          ROOT.RooFit.LineColor(ROOT.kRed))
        self.data.plotOn(self.frame, ROOT.RooFit.Name("data"), 
                         ROOT.RooFit.MarkerSize(marker_size),
                         ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
        self.legend.AddEntry(self.frame.findObject("data"), "Data", "LPE")
        self.legend.AddEntry(self.frame.findObject("fit"), "Fit", "L")
        
        self.frame.GetXaxis().SetLabelFont(2)
        self.frame.GetXaxis().SetTitleFont(2)
        self.frame.GetXaxis().SetLabelFont(2)
        self.frame.GetXaxis().SetTitle(" ")
        self.create_ratio(marker_size=ratio_marker_size)
        self.format_ticks()
        
        self.canvas.cd(1)
        
        self.plot_param(y_max=0.67, name='{}_paramBox'.format(self.name))
        
        texts = deepcopy(self._DEFAULT_TEXTS_)
        if labels:
            texts += labels
        self.plot_text(texts, x_min=0.12, name='{}_textBox'.format(self.name))
        
        ##double chi2 = frame->chiSquare("fit","data",7); 
        #TString chi2Line = TString::Format("Chisquare = %f ",chi2)
        #fit->paramOn(frame,Layout(0.7,0.9,0.9), Label(chi2Line))
        
        self.frame.Draw()
        self.legend.SetTextFont(2)
        self.legend.Draw("same")
        self.canvas.cd(2)
        self.ratio_frame.Draw()
        
        return self.canvas