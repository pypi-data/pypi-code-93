# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, Toplevel, scrolledtext, messagebox
from tksheet import Sheet
import datetime

from proc_mem_monitor.proc_mem_handler import get_mem_usages
from proc_mem_monitor.proc_mem_plot import ProcMemPlot
from proc_mem_monitor import VERSION, LABEL_WIDTH, COMBO_WIDTH, STATUS_CODES, \
                DEFAULT_REFRESH_INTERVAL, __icon__, \
                SHEET_PID_COL, SHEET_CPU_COL, SHEET_RSS_COL, SHEET_CMD_COL, \
                SHEET_LAST_UPDATED_COL


def show_plot_window():
    global proc_mem_plot

    proc_mem_plot.show_plot_window(root_window)


# refresh database every DEFAULT_REFRESH_INTERVAL seconds
def refresh_database():
    global root_window

    pattern = combo_pattern.get()
    mem_usages = get_mem_usages(pattern)

    if mem_usages is not None:
        update_sheet_proc(mem_usages)
        proc_mem_plot.update_history(mem_usages)
        proc_mem_plot.plot_metrics()

    # add refresh_database back to the eventloop
    root_window.after(DEFAULT_REFRESH_INTERVAL*1000, refresh_database)


def start_gui(hostname, total_mem, patterns):
    global combo_pattern, root_window, sheet_proc, sheet_proc_last_row, proc_mem_plot
    global root_window

    ###############################################################################
    # root window
    ###############################################################################
    root_window = tk.Tk()
    root_window.geometry('1200x400+20+20')
    root_window.title('Process Memory Monitor ' + VERSION + ' - ' + hostname)
    root_window_icon = tk.PhotoImage(file=str(__icon__))
    root_window.iconphoto(True, root_window_icon)
    root_window.grid_columnconfigure(0, weight=0)
    root_window.grid_columnconfigure(1, weight=0)
    root_window.grid_columnconfigure(2, weight=0)
    root_window.grid_columnconfigure(3, weight=1)

    cur_grid_row = 0
    label_pattern = ttk.Label(root_window, text="Command Pattern", width=LABEL_WIDTH, anchor='w')
    label_pattern.grid(row=cur_grid_row, column=0,  sticky='w', padx=10, pady=10)
    combo_pattern = ttk.Combobox(root_window, width=COMBO_WIDTH)
    combo_pattern['values'] = []
    combo_pattern.grid(row=cur_grid_row, column=1, sticky='w', pady=10)
    cur_grid_row = cur_grid_row + 1

    # sheet for pattern
    sheet_proc = Sheet(root_window,
                       default_row_index="numbers", total_rows=200, total_columns=5)
    sheet_proc.enable_bindings(("single_select",  # "single_select" or "toggle_select"
                                "drag_select",  # enables shift click selection as well
                                "column_drag_and_drop",
                                "row_drag_and_drop",
                                #"column_select",
                                "row_select",
                                "column_width_resize",
                                "double_click_column_resize",
                                "arrowkeys",
                                #"row_height_resize",
                                #"double_click_row_resize",
                                "right_click_popup_menu",
                                "rc_select",
                                #"rc_insert_column",
                                #"rc_delete_column",
                                #"rc_insert_row",
                                #"rc_delete_row",
                                "copy",
                                "cut",
                                "paste",
                                "delete",
                                "undo",
                                "edit_cell"))
    sheet_proc.grid(row=cur_grid_row, columnspan=4, sticky='nswe')
    root_window.grid_rowconfigure(cur_grid_row, weight=1)
    sheet_proc.set_cell_data(0, SHEET_PID_COL, 'PID')
    sheet_proc.set_cell_data(0, SHEET_CPU_COL, '%CPU')
    sheet_proc.set_cell_data(0, SHEET_RSS_COL, 'RSS(GB)')
    sheet_proc.set_cell_data(0, SHEET_CMD_COL, 'CMD')
    sheet_proc.set_cell_data(0, SHEET_LAST_UPDATED_COL, 'Last Updated')
    sheet_proc.column_width(column=SHEET_PID_COL, width=150)
    sheet_proc.column_width(column=SHEET_CPU_COL, width=100)
    sheet_proc.column_width(column=SHEET_RSS_COL, width=100)
    sheet_proc.column_width(column=SHEET_CMD_COL, width=450)
    sheet_proc.column_width(column=SHEET_LAST_UPDATED_COL, width=200)
    cur_grid_row = cur_grid_row + 1
    sheet_proc_last_row = 0

    # command buttons
    button_plot = ttk.Button(root_window, text="Plot", command=show_plot_window)
    button_plot.grid(row=cur_grid_row, column=1, pady=10)
    cur_grid_row = cur_grid_row + 1

    proc_mem_plot = ProcMemPlot(hostname)
    proc_mem_plot.total_mem = total_mem

    combo_pattern['values'] = patterns
    if len(patterns) > 0:
        combo_pattern.current(0)

    root_window.after(DEFAULT_REFRESH_INTERVAL*1000, refresh_database)
    root_window.mainloop()


def update_sheet_proc(mem_usage):
    global sheet_proc_last_row, sheet_proc

    last_udpated = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    row = 1
    for k in mem_usage.keys():
        sheet_proc.set_cell_data(row, SHEET_PID_COL, k)
        sheet_proc.set_cell_data(row, SHEET_CPU_COL, mem_usage[k]['cpu'])
        sheet_proc.set_cell_data(row, SHEET_RSS_COL, mem_usage[k]['rss'])
        sheet_proc.set_cell_data(row, SHEET_CMD_COL, mem_usage[k]['cmd'])
        sheet_proc.set_cell_data(row, SHEET_LAST_UPDATED_COL, last_udpated)
        row = row + 1

    if sheet_proc_last_row > row:
        # clear contents from previous dump
        for r in range(row, sheet_proc_last_row+1):
            sheet_proc.set_cell_data(r, SHEET_PID_COL, '')
            sheet_proc.set_cell_data(r, SHEET_CPU_COL, '')
            sheet_proc.set_cell_data(r, SHEET_RSS_COL, '')
            sheet_proc.set_cell_data(r, SHEET_CMD_COL, '')
            sheet_proc.set_cell_data(r, SHEET_LAST_UPDATED_COL, '')

    # udpate the last row count
    sheet_proc_last_row = row

    sheet_proc.refresh()
