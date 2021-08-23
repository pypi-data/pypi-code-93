# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, Toplevel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from pandas import DataFrame
import datetime
import socket
import subprocess
from proc_mem_monitor import PROGRAM_NAME, VERSION, COMBO_WIDTH, LABEL_WIDTH, \
    FIGURE_DPI, DEFAULT_REFRESH_INTERVAL


class ProcMemPlot:
    def __init__(self, hostname=None):
        self.peak_mem = 0
        self.total_mem = 1024
        self.free_mem = self.total_mem
        self.pause_plot = 0
        self.hostname = hostname

        # members for GUI
        self.window_plot = None

        self.combo_period = None
        self.label_period = None
        self.combo_period_seconds = []

        self.figure_hist = None
        self.plot_axe_hist = None
        self.y_ax = None
        self.canvas_hist = None
        self.frame_toolbar = None
        self.toolbar_plot = None

        self.button_plot_pause = None

        # members for plot data.
        self.time_hist = {}
        self.mem_hist = {}

    def plot_metrics(self):
        if (not (self.window_plot is not None and \
                 tk.Toplevel.winfo_exists(self.window_plot))) or \
            self.time_hist.get('rss_total') is None or self.pause_plot == 1:
            return

        period_selection = self.combo_period.current()
        period_secodns_sel = self.combo_period_seconds[period_selection]
        last_N = period_secodns_sel//DEFAULT_REFRESH_INTERVAL
        self.plot_axe_hist.clear()
        y_hist_dict = {'time': self.time_hist['rss_total'][-last_N:],
                       'mem': self.mem_hist['rss_total'][-last_N:]}
        y_hist_df = DataFrame(y_hist_dict, columns=['time', 'mem'])
        y_hist_df.plot(kind='line', legend=True, x='time', y='mem',
                        ax=self.plot_axe_hist, color='r', marker='.', fontsize=10)

        self.plot_axe_hist.set_ylabel('Memory(GB)')
        self.plot_axe_hist.set_title('Memory (GB) History - max=' + str(self.peak_mem) + \
                                     ' free=' + str(self.free_mem))
        self.plot_axe_hist.set_ylim([0, self.total_mem])
        self.canvas_hist.draw()

    def toggle_pause_plot(self):
        if self.pause_plot == 0:
            self.pause_plot = 1
            self.button_plot_pause['text'] = 'Resume'
        else:
            self.pause_plot = 0
            self.button_plot_pause['text'] = 'Pause'
  
    def show_plot_window(self, root_window):
        if self.window_plot is not None and tk.Toplevel.winfo_exists(self.window_plot):
            return

        self.window_plot = Toplevel(root_window)
        self.window_plot.geometry('1200x600+20+500')
        self.window_plot.title(PROGRAM_NAME + ' ' + VERSION + ' - plot - ' + self.hostname)
        self.window_plot.grid_columnconfigure(1, weight=1)

        cur_grid_row = 0
        self.label_period = ttk.Label(self.window_plot, text="Period", width=LABEL_WIDTH, anchor='w')
        self.label_period.grid(row=cur_grid_row, column=0,  sticky='w', padx=10, pady=10)
        self.combo_period = ttk.Combobox(self.window_plot, width=COMBO_WIDTH)
        self.combo_period['values'] = ['Last 1 hour', 'Last 4 hours', 'Last 8 hours',
                                       'Last 24 hours', 'All history'] 
        self.combo_period_seconds = [3600, 3600*4, 3600*8 , 3600*24, 3600*10000]       
        self.combo_period.grid(row=cur_grid_row, column=1, sticky='w', pady=10)
        self.combo_period.current(0)
        cur_grid_row = cur_grid_row + 1


        # plot row
        self.figure_hist = plt.Figure(figsize=(10, 5), dpi=FIGURE_DPI)
        self.plot_axe_hist = self.figure_hist.add_subplot(111)
        self.canvas_hist = FigureCanvasTkAgg(self.figure_hist, self.window_plot)
        self.canvas_hist.get_tk_widget().grid(row=cur_grid_row, column=0, 
                                              columnspan=2, sticky='nsew')
        self.window_plot.grid_rowconfigure(cur_grid_row, weight=1)
        cur_grid_row = cur_grid_row + 1

        # Plot navigation toolbar
        self.frame_toolbar = tk.Frame(self.window_plot)
        self.frame_toolbar.grid(row=cur_grid_row, column=0, columnspan=2)
        self.toolbar_plot = NavigationToolbar2Tk(self.canvas_hist, self.frame_toolbar)
        cur_grid_row = cur_grid_row + 1

        # command buttons
        self.button_plot_pause = ttk.Button(self.window_plot, text="Pause", 
                                            command=self.toggle_pause_plot)
        self.button_plot_pause.grid(row=cur_grid_row, column=0, columnspan=2, pady=10)
        cur_grid_row = cur_grid_row + 1

    def update_history(self, mem_usages):
        if self.time_hist.get('rss_total') is None:
            self.time_hist['rss_total'] = []
            self.mem_hist['rss_total'] = []

        cur_time = datetime.datetime.now().strftime("%m/%d %H:%M:%S")
        self.time_hist['rss_total'].append(cur_time)
        self.mem_hist['rss_total'].append(mem_usages['rss_total']['rss'])
        if mem_usages['rss_total']['rss'] > self.peak_mem:
            self.peak_mem = mem_usages['rss_total']['rss']
            print('INFO: @{} peak memory={} total memory={}'.format(
                cur_time, self.peak_mem, self.total_mem))

        # update free memeory
        command = ['free', '-g']
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        free_out = p.stdout.read().decode('utf-8')
        mem_line = free_out.strip().split('\n')[1]
        self.free_mem = int(mem_line.split()[6])
