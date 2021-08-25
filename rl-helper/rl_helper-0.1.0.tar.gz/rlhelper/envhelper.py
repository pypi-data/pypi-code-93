from matplotlib import animation
import matplotlib.pyplot as plt
from datetime import datetime
import os
class envhelper(object):
    from pyvirtualdisplay import Display
    virtual_display = Display(visible=0, size=(1400, 900))
    virtual_display.start()

    def __init__(self) -> None:
        super().__init__()
 
    def recording(self,env):
        self.frames = [] if getattr(self,"frames",None) is None else getattr(self,"frames",None) ;
        self.frames.append(env.render(mode="rgb_array"))
        self.env=env

    def save_gif(self,path=None,filename=None,times=5):
        """
        save frames to gif
        """
        print("saving gif...")
        def _save_frames_as_gif(frames, path='./', filename='gym_animation.gif',times=1):

            
            old_frames=frames.copy()
            frames=[]
            c=0
            for f in old_frames:
                c+=1
                if c==times:
                    frames.append(f)
                    c=0
            #Mess with this to change frame size
            plt.figure(figsize=(frames[0].shape[1] / 72.0, frames[0].shape[0] / 72.0), dpi=72)

            patch = plt.imshow(frames[0])
            plt.axis('off')

            def animate(i):
                patch.set_data(frames[i])

            anim = animation.FuncAnimation(plt.gcf(), animate, frames = len(frames), interval=1000)
            anim.save(path + filename, writer='imagemagick', fps=60)
        
        now = datetime.now() # current date and time    
        t=now.strftime("%Y%m%d-%H%M%S")
        assert path is None and filename is None, "not support diy path and filename"
        gif_name="{t}.gif".format(t=t)
        dirs="./runs/{env}/".format(env=self.env.spec.id)
        os.makedirs(dirs,exist_ok=True)
        _save_frames_as_gif(self.frames,path=dirs,filename=gif_name,times=times)
        print("gif saved to {}{}".format(dirs,gif_name))
