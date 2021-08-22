import os
import imageio
import numpy as np
from tqdm import tqdm
from math import exp
import matplotlib.pyplot as plt

class IzhNeuron():
    def __init__(self):
        """
        Inititator function that can be 
        used to set the default values;
        Default parameters are set to 
        Regular Spiking
        """
        self.a = 0.02
        self.b = 0.2
        self.c = -65
        self.d = 8

        self.v = -65
        self.u = self.b * self.v

    def change_params(self, params):
        for key in params:
            setattr(self, key, params[key])        


    def simulate(self, t, I):
        self.dt = t[1] - t[0]
        self.t = t

        if type(I) not in [list, np.ndarray]:
            I = I*np.ones((len(t), ))

        if len(t) != I.size:
            assert("The sizes of the currect vector doesn't match with that of the time vector.")

        self.I = I

        niter = len(t)
        
        self.vhist = []
        self.uhist = []

        for idx in range(niter):
            dvdt = 0.04*self.v**2 + 5*self.v + 140 - self.u + self.I[idx]
            dudt = self.a*(self.b*self.v - self.u)

            if self.v + dvdt*self.dt >= 30:
                self.vhist.append(30)
                self.uhist.append(self.u + dudt*self.dt)
                self.v = self.c
                self.u += self.d
            else:
                self.v += dvdt*self.dt
                self.u += dudt*self.dt

                self.vhist.append(self.v)
                self.uhist.append(self.u)

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
        plt.grid()

        if ylim != None:
            plt.ylim(ylim)
        plt.xlabel("Time (ms)")
        plt.title("Izhikevich Neuron; Voltage across Time; $I=$"+name)
        if save:
            fig_name = image_directory+"/izh_"+name+"_v.png"
            print(fig_name)
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

            fig_name = image_directory+"/izh_"+str(round(self.I[0],5))+"_v.png"
            images_arr.append(imageio.imread(fig_name))

        print("Generating the GIF and MOV files... This might take a while...")
        imageio.mimsave(image_directory+"/izh_"+name+".gif", images_arr, duration=0.2)
        imageio.mimsave(image_directory+"/izh_"+name+".mov", images_arr)


        