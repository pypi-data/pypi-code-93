import os
import imageio
import numpy as np
from tqdm import tqdm
from math import exp
import matplotlib.pyplot as plt

class FHNNeuron():
    def __init__(self):
        self.a = 0.5
        self.b = 0.1
        self.r = 0.1

    def change_params(self, params):
        for key in params:
            setattr(self, key, params[key])       

    def f(self):
        return self.v*(self.a - self.v)*(self.v - 1)

    def dvdt(self, I):
        return self.f() - self.w + I

    def dwdt(self):
        return self.b*self.v - self.r*self.w

    def simulate(self, v, w, t, I):
        self.v = v
        self.w = w

        self.t = t
        dt = t[1] - t[0]
        niter = len(t)

        self.vhist = []
        self.whist = []

        if type(I) not in [list, np.ndarray]:    
            I = I*np.ones((len(t),))
        if I.size != len(t):
            assert("The lengths of I and t vectors don't match!")

        self.I = I
        # print(I, type(I))

        for idx in range(niter):
            dvdt = self.dvdt(I[idx])
            dwdt = self.dwdt()

            self.v += dvdt*dt
            self.w += dwdt*dt
            self.vhist.append(self.v)
            self.whist.append(self.w)

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
        plt.plot(self.t, self.vhist, label="v")
        plt.plot(self.t, self.whist, label="w")
        plt.grid()
        plt.legend()

        if ylim != None:
            plt.ylim(ylim)
        plt.xlabel("Time (ms)")
        plt.title("Fitz-Hugh Nagumo Neuron; Voltage across Time; $I=$"+name)
        if save:
            fig_name = image_directory+"/fhn_"+name+"_v.png"
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
            self.simulate(self.v, self.w, t, I)
            self.plot(ylim=ylim, save=True, show=False)

            fig_name = image_directory+"/fhn_"+str(round(self.I[0],5))+"_v.png"
            images_arr.append(imageio.imread(fig_name))

        print("Generating the GIF and MOV files... This might take a while... ")
        imageio.mimsave(image_directory+"/fhn_"+name+".gif", images_arr, duration=0.2)
        imageio.mimsave(image_directory+"/fhn_"+name+".mov", images_arr)
