#!/usr/bin/env python3

import logging
import time
import math
import pymoku
import struct
import threading

from moku.instruments import Oscilloscope

from matplotlib import pyplot as plt
from matplotlib.widgets import Button, Slider, RadioButtons
from matplotlib.ticker import FuncFormatter

FORMAT = '%(asctime)-15s %(name)s: %(message)s'
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

logging.getLogger("matplotlib.font_manager").setLevel(logging.CRITICAL)

running = True


def _on_close(event):
    global running
    running = False


class Callbacks(object):
    def __init__(self, osc, ax):
        self.osc = osc
        self.ax = ax
        self.dac_ctrl_offset = self.osc.num_cbufs * 4 + 13

    def trigger_level(self, val):
        self.osc.set_trigger('in1', 'rising', val, hysteresis=0.1)

    def relays(self, ch, coupling=None, range=None, dc=None):
        self.osc.set_frontend(ch, coupling=coupling, range=range)

    def scroll_x(self, ax):
        t1, t2 = ax.get_xlim()
        # add 50% to each end so we don't have blank edges when scrolling
        d = t2 - t1
        t1 = t1 - 0.5 * d
        t2 = t2 + 0.5 * d
        self.osc.set_timebase(t1, t2)

    def pause(self, btn):
        self.osc.pause = not self.osc.pause
        btn.label.set_text('Run' if self.osc.pause else 'Stop')
        self.osc.commit()

    def xmode(self, mode):
        mode = mode.lower()
        self.osc._render.set_xmode(mode)

        if mode == 'roll':
            x1, x2 = self.ax.get_xlim()
            dx = x2 - x1
            self.ax.set_xlim(-max(dx, 5.0), 0.0)

    def singen_f(self, f):
        v = math.e ** f
        for ch in self.osc.wg.ch:
            ch._set_sweepgenerator(frequency=v)
        self.osc.wg.commit()

    def singen_a(self, a):
        for ch in self.osc.wg.ch:
            ch.amplitude = a
        self.osc.wg.commit()

    def singen_o(self, o):
        for ch in self.osc.wg.ch:
            ch.offset = o
        self.osc.wg.commit()

    def rmode(self, mode):
        self.osc.set_rmode(mode.lower())


def setup_plot(osc):
    plt.ion()

    fig = plt.figure(figsize=(10.0, 7.5))
    fig.canvas.mpl_connect('close_event', _on_close)

    ax0 = fig.add_subplot(111)
    callbacks = Callbacks(osc, ax0)
    ax0.callbacks.connect('xlim_changed', callbacks.scroll_x)

    lines = {}
    for ch, col in zip(osc._render.sources,
                       ['red', 'blue', 'green', 'orange']):
        lines['rdr0' + ch], = ax0.plot([0] * osc._render.frame_length, col)

    ax0.grid(b=True)
    ax0.set_xlim([-2e-6, 2e-6])
    ax0.set_ylim([-10.0, 10.0])

    stuff = []
    if callbacks is not None:
        plt.subplots_adjust(bottom=0.4, top=0.97, right=0.97, left=0.15)

        btnax = plt.axes([0.01, 0.4, 0.045, 0.57])  # x, y, w, h
        s = Slider(btnax, '', -4.0, 4.0, valinit=0, valfmt='%4.2f',
                   valstep=0.01, orientation='vertical')
        s.on_changed(callbacks.trigger_level)
        stuff.append(s)

    # Relay Controls
    x, y = 0.12, 0.26
    w, h = 0.06, 0.07
    for i, c in enumerate(osc._render.sources):
        label = fig.text(x, y - (h + 0.005) * i + 0.015, "CH{:1d}".format(i))

        rax = plt.axes([x + w, y - i * (h + 0.005), w, h])
        radio = RadioButtons(rax, ('AC', 'DC'))
        radio.on_clicked(
            lambda lbl, ch=i: callbacks.relays(ch, dc=lbl == 'DC'))
        stuff.append(radio)

        rax = plt.axes([x + w + w, y - i * (h + 0.005), w, h])
        radio = RadioButtons(rax, ('1X', '10X'))
        radio.on_clicked(
            lambda lbl, ch=i: callbacks.relays(ch, atten=lbl == '1X'))
        stuff.append(radio)

        rax = plt.axes([x + w + w + w, y - i * (h + 0.005), w, h])
        radio = RadioButtons(rax, ('50Ω', '1MΩ'))
        radio.on_clicked(
            lambda lbl, ch=i: callbacks.relays(ch, fiftyr=lbl == '50Ω'))
        stuff.append(radio)

    # TODO these buttons create huge performance issues (mouse over)
    # btnax = plt.axes([0.525, 0.41, 0.07, 0.03])
    # pause_btn = Button(btnax, 'Stop')
    # pause_btn.on_clicked(lambda evt, btn=pause_btn: callbacks.pause(btn))
    # stuff.append(pause_btn)

    # x, y = 0.90, 0.31
    # for l, s in [('±5s', 5.0), ('±1s', 1.0), ('±100ms', 0.1), ('±100us', 0.0001)]:
    #     btnax = plt.axes([x, y, 0.07, 0.03])
    #     scale_btn = Button(btnax, l)
    #     scale_btn.on_clicked(lambda evt, s=s: ax0.set_xlim([-s, s]))
    #     stuff.append(scale_btn)
    #     y = y - 0.04

    # x, y = 0.81, 0.31
    # for l, s in [('±5V', 5.0), ('±1V', 1.0), ('±0.5V', 0.5), ('±0.1V', 0.1)]:
    #     btnax = plt.axes([x, y, 0.07, 0.03])
    #     scale_btn = Button(btnax, l)
    #     scale_btn.on_clicked(lambda evt, s=s: ax0.set_ylim([-s, s]))
    #     stuff.append(scale_btn)
    #     y = y - 0.04

    rax = plt.axes([0.72, 0.19, 0.07, 0.12])
    radio = RadioButtons(rax, ('Normal', 'Sweep', 'Roll'))
    radio.on_clicked(callbacks.xmode)
    stuff.append(radio)

    rax = plt.axes([0.82, 0.15, 0.11, 0.16])
    radio = RadioButtons(rax, ('Normal', 'Precision', 'MinMax', 'MinMaxier'))
    radio.on_clicked(callbacks.rmode)
    stuff.append(radio)

    x, y = 0.53, 0.10
    btnax = plt.axes([x, y, 0.04, 0.20])
    s = Slider(btnax, '', 0, 20, valinit=1, valfmt='%5.2f', valstep=0.01,
               orientation='vertical')
    s.on_changed(lambda val: callbacks.singen_f(val))
    stuff.append(s)

    x, y = 0.58, 0.10
    btnax = plt.axes([x, y, 0.04, 0.20])
    s = Slider(btnax, '', 0, 2.0, valinit=0.0, valfmt='%4.2f', valstep=0.01,
               orientation='vertical')
    s.on_changed(lambda val: callbacks.singen_a(val))
    stuff.append(s)

    x, y = 0.63, 0.10
    btnax = plt.axes([x, y, 0.04, 0.20])
    s = Slider(btnax, '', -1.0, 1.0, valinit=0, valfmt='%4.2f', valstep=0.01,
               orientation='vertical')
    s.on_changed(lambda val: callbacks.singen_o(val))
    stuff.append(s)

    plt.draw()
    plt.show()
    return ax0, lines, stuff


def main(ip_addr):
    osc = Oscilloscope(ip_addr, force_connect=False)
    try:
        osc.set_acquisition_mode('Normal')
        osc.set_trigger('Edge', "Input1")

        for ch in osc.wg.ch:
            ch.sinewave(0.0, 0.0)

        # need to hold a reference to stuff
        ax0, lines, stuff = setup_plot(osc)

        # Start the loop
        while running:
            try:
                frame = osc.get_data(timeout=1.0 / 20.0)
                # import pdb; pdb.set_trace()
                if frame.type_id in [0x02, 0x04]:  # MinMax
                    for source in frame.samples.keys():
                        lines[source].set_ydata(
                            [j for i in frame.samples[source] for j in i])
                        lines[source].set_xdata(
                            [j for i in zip(frame.time, frame.time) for j in
                             i])
                else:
                    for source, data in frame.samples.items():
                        lines[source].set_ydata(data)
                        lines[source].set_xdata(frame.time)

                ax0.xaxis.set_major_formatter(
                    FuncFormatter(frame.get_xaxis_fmt))
                ax0.yaxis.set_major_formatter(
                    FuncFormatter(frame.get_yaxis_fmt))

            except FrameTimeout:
                pass
            except (
            UnicodeDecodeError, KeyError):  # TODO add renderer type to packet
                log.exception("")
            plt.pause(0.001)

    finally:
        osc.relinquish_ownership()


if __name__ == '__main__':
    import argparse  # noqa

    parser = argparse.ArgumentParser(description='Oscilloscope Plotting')
    parser.add_argument('ip_addr', type=str)

    args = parser.parse_args()
    main(args.ip_addr)
