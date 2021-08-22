import os
import imageio
import numpy as np
from tqdm import tqdm
from math import exp
import matplotlib.pyplot as plt

class HHNeuron():
    def __init__(self):
        self.v = -65

        self.gnamax = 1.20
        self.gkmax = 0.36
        self.vk = -77 
        self.vna = 50 
        self.gl = 0.003
        self.vl = -54.387 
        self.cm = 0.01

        self.m = 0.0530
        self.h = 0.5960
        self.n = 0.3177

    def change_params(self, params):
        for key in params:
            setattr(self, key, params[key])       

    def simulate(self, t, I):
        self.t = t
        dt = t[1] - t[0]
        niter = len(t)

        self.vhist = []
        self.mhist = []
        self.hhist = []
        self.nhist = []

        if type(I) not in [list, np.ndarray]:
            I = I*np.ones((len(t),))
        
        if I.size != len(t):
            assert("The sizes of the currect vector doesn't match with that of the time vector.")

        self.I = I

        for idx in range(niter):
            gna = self.gnamax*self.m**3*self.h
            gk = self.gkmax*self.n**4
            gtot = gna + gk + self.gl
            vinf = ((gna*self.vna + gk*self.vk + self.gl*self.vl) + I[idx])/gtot
            tauv = self.cm/gtot

            self.v = vinf + (self.v - vinf)*exp(-dt/tauv)

            self.am = 0.1*(self.v + 40)/(1-exp(-(self.v + 40)/10))
            self.bm = 4*exp(-0.0556*(self.v + 65))

            self.an = 0.01*(self.v + 55)/(1-exp(-(self.v + 55)/10))
            self.bn = 0.125*exp(-(self.v + 65)/80)

            self.ah = 0.07*exp(-0.05*(self.v + 65))
            self.bh = 1/(1+exp(-0.1*(self.v + 35)))

            taum = 1/(self.am + self.bm)
            tauh = 1/(self.ah + self.bh)
            taun = 1/(self.an + self.bn)

            minf = self.am*taum
            hinf = self.ah*tauh
            ninf = self.an*taun

            self.m = minf + (self.m - minf)*exp(-dt/taum)
            self.h = hinf + (self.h - hinf)*exp(-dt/tauh)
            self.n = ninf + (self.n - ninf)*exp(-dt/taun)

            self.vhist.append(self.v)
            self.mhist.append(self.m)
            self.hhist.append(self.h)
            self.nhist.append(self.n)

    def plot(self, ylim=None, save=False, name=None, show=True, image_directory="images"):
        if not hasattr(self, "vhist"):
            assert("The model should be simulated before plotting the results! :)\nRun model.simulate()")

        if name == None:
            name = str(round(self.I[0],5))

        if save:
            try:
                os.mkdir(image_directory)
            except:
                pass

        plt.figure()
        plt.plot(self.t, self.vhist)
        plt.grid()
        if ylim != None:
            plt.ylim(ylim)
        plt.xlabel("Time (ms)")
        plt.title("Hodgkin & Huxley Neuron; Voltage across Time; $I=$"+name)
        if save:
            fig_name = image_directory+"/hh_"+name+"_v.png"
            plt.savefig(fig_name)

        plt.figure()
        plt.plot(self.t, self.mhist)
        plt.grid()
        plt.xlabel("Time (ms)")
        plt.title("Hodgkin & Huxley Neuron; $m$ across Time; $I=$"+name)
        if save:
            fig_name = image_directory+"/hh_"+name+"_m.png"
            plt.savefig(fig_name)

        plt.figure()
        plt.plot(self.t, self.nhist)
        plt.grid()
        plt.xlabel("Time (ms)")
        plt.title("Hodgkin & Huxley Neuron; $n$ across Time; $I=$"+name)
        if save:
            fig_name = image_directory+"/hh_"+name+"_n.png"
            plt.savefig(fig_name)

        plt.figure()
        plt.plot(self.t, self.hhist)
        plt.grid()
        plt.xlabel("Time (ms)")
        plt.title("Hodgkin & Huxley Neuron; $h$ across Time; $I=$"+name)
        if save:
            fig_name = image_directory+"/hh_"+name+"_h.png"
            plt.savefig(fig_name)

        if show:
            plt.show()
        plt.close("all")

    def animate(self, t, current_list, ylim=None, name="1", image_directory="images"):
        try:
            os.mkdir(image_directory)
        except:
            pass
        
        images_arr = []

        for I in tqdm(current_list):
            self.simulate(t, I)
            self.plot(ylim=ylim, save=True, show=False)

            fig_name = image_directory+"/hh_"+str(round(self.I[0],5))+"_v.png"
            images_arr.append(imageio.imread(fig_name))

        print("Generating the GIF and MOV files... This might take a while...")
        imageio.mimsave(image_directory+"/hh_"+name+".gif", images_arr, duration=0.2)
        imageio.mimsave(image_directory+"/hh_"+name+".mov", images_arr)
