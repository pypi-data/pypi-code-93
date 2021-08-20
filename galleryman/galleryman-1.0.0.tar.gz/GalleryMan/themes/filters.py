from PIL import Image , ImageOps
import numpy as np

class Filters:
    def __init__(self , img) -> None:
        self.img = img
        
    def transform(self , r , g , b):
        new_color = r * self.rf + g * self.gf + b * self.bf
                
        return new_color.clip(0 , 255).astype(np.uint8)

    def sepia(self):
        img_array = np.asarray(self.img)

        R = img_array.T[0]
        G = img_array.T[1]
        B = img_array.T[2]
        A = img_array.T[3]

        self.rf , self.gf , self.bf = 0.393 , 0.769 , 0.189
        
        R = self.transform(R, G , B)
        
        self.rf , self.gf , self.bf = 0.349 , 0.686 , 0.168
        
        G = self.transform(R , G , B)
        
        self.rf , self.gf , self.bf = 0.272 , 0.534 , 0.131
        
        B = self.transform(R , G , B)

        return Image.fromarray(np.array([R, G, B, A]).T, mode="RGBA")
    
    def cherry(self):
        img_array = np.asarray(self.img)

        R = img_array.T[0]
        G = img_array.T[1]
        B = img_array.T[2]
        A = img_array.T[3]
        
        self.rf , self.gf , self.bf = [0.429, 0.346, 0.236]
        
        R = self.transform(R, G , B)
        
        self.rf , self.gf , self.bf = [0.09, 0.317, 0.122]
        
        G = self.transform(R , G , B)
        
        self.rf , self.gf , self.bf = [0.353, 0.314, 0.177]
        
        B = self.transform(R , G , B)

        return Image.fromarray(np.array([R, G, B, A]).T, mode="RGBA")
    
    def underwater(self):
        img_array = np.asarray(self.img)

        R = img_array.T[0]
        G = img_array.T[1]
        B = img_array.T[2]
        A = img_array.T[3]

        self.rf , self.gf , self.bf = [0.154, 0.057, 0.053]
        
        R = self.transform(R, G , B)
        
        self.rf , self.gf , self.bf = [0.278, 0.408, 0.768]
        
        G = self.transform(R , G , B)
        
        self.rf , self.gf , self.bf = [0.872, 0.814, 0.797]
        
        B = self.transform(R , G , B)

        return Image.fromarray(np.array([R, G, B, A]).T, mode="RGBA")
    
    def purple(self):
        img_array = np.asarray(self.img)

        R = img_array.T[0]
        G = img_array.T[1]
        B = img_array.T[2]
        A = img_array.T[3]

        self.rf , self.gf , self.bf = [0.416, 0.631, 0.027]
        
        R = self.transform(R, G , B)
        
        self.rf , self.gf , self.bf = [0.084, 0.247, 0.211]
        
        G = self.transform(R , G , B)
        
        self.rf , self.gf , self.bf = [0.989, 0.174, 0.373]
        
        B = self.transform(R , G , B)

        return Image.fromarray(np.array([R, G, B, A]).T, mode="RGBA")
    
    def pink(self):
        img_array = np.asarray(self.img)

        R = img_array.T[0]
        G = img_array.T[1]
        B = img_array.T[2]
        A = img_array.T[3]

        self.rf , self.gf , self.bf = [0.536, 0.406, 0.419]
        
        R = self.transform(R, G , B)
        
        self.rf , self.gf , self.bf = [0.462, 0.108, 0.284]
        
        G = self.transform(R , G , B)
        
        self.rf , self.gf , self.bf = [0.145, 0.647, 0.5]
        
        B = self.transform(R , G , B)

        return Image.fromarray(np.array([R, G, B, A]).T, mode="RGBA")
    
    def dark(self):
        img_array = np.asarray(self.img)

        R = img_array.T[0]
        G = img_array.T[1]
        B = img_array.T[2]
        A = img_array.T[3]

        self.rf , self.gf , self.bf = [0.072, 0.143, 0.055]
        
        R = self.transform(R, G , B)
        
        self.rf , self.gf , self.bf = [0.158, 0.525, 0.189]
        
        G = self.transform(R , G , B)
        
        self.rf , self.gf , self.bf = [0.273, 0.645, 0.811]
        
        B = self.transform(R , G , B)

        return Image.fromarray(np.array([R, G, B, A]).T, mode="RGBA")
    
    def clear(self):
        img_array = np.asarray(self.img)

        R = img_array.T[0]
        G = img_array.T[1]
        B = img_array.T[2]
        A = img_array.T[3]

        self.rf , self.gf , self.bf = [0.81, 0.185, 0.241]
        
        R = self.transform(R, G , B)
        
        self.rf , self.gf , self.bf = [0.392, 0.067, 0.558]
        
        G = self.transform(R , G , B)
        
        self.rf , self.gf , self.bf = [0.226, 0.622, 0.615]
        
        B = self.transform(R , G , B)

        return Image.fromarray(np.array([R, G, B, A]).T, mode="RGBA")
    
    def realistic(self):
        img_array = np.asarray(self.img)

        R = img_array.T[0]
        G = img_array.T[1]
        B = img_array.T[2]
        A = img_array.T[3]
        
        self.rf , self.gf , self.bf = [0.393, 0.374, 0.035]
        
        R = self.transform(R, G , B)
        
        self.rf , self.gf , self.bf = [0.214, 0.492, 0.143]
        
        G = self.transform(R , G , B)
        
        self.rf , self.gf , self.bf = [0.403, 0.465, 0.413]
        
        B = self.transform(R , G , B)

        return Image.fromarray(np.array([R, G, B, A]).T, mode="RGBA")
    
    def cool(self):
        img_array = np.asarray(self.img)

        R = img_array.T[0]
        G = img_array.T[1]
        B = img_array.T[2]
        A = img_array.T[3]

        self.rf , self.gf , self.bf = [0.492, 0.324, 0.026]
        
        R = self.transform(R, G , B)
        
        self.rf , self.gf , self.bf = [0.265, 0.142, 0.213]
        
        G = self.transform(R , G , B)
        
        self.rf , self.gf , self.bf = [0.417, 0.286, 0.374]
        
        B = self.transform(R , G , B)

        return Image.fromarray(np.array([R, G, B, A]).T, mode="RGBA")
    
    def shady(self):
        img_array = np.asarray(self.img)

        R = img_array.T[0]
        G = img_array.T[1]
        B = img_array.T[2]
        A = img_array.T[3]

        self.rf , self.gf , self.bf = [0.38, 0.407, 0.11]
        
        R = self.transform(R, G , B)
        
        self.rf , self.gf , self.bf = [0.47, 0.405, 0.059]
        
        G = self.transform(R , G , B)
        
        self.rf , self.gf , self.bf = [0.217, 0.474, 0.212]
        
        B = self.transform(R , G , B)

        return Image.fromarray(np.array([R, G, B, A]).T, mode="RGBA")
    
    def idk(self):
        img_array = np.asarray(self.img)

        R = img_array.T[0]
        G = img_array.T[1]
        B = img_array.T[2]
        A = img_array.T[3]

        self.rf , self.gf , self.bf = 0.21 , 0.31 , 0.63
  
        R = self.transform(R, G , B)
        
        self.rf , self.gf , self.bf = 0.26 , 0.43 , 0.63
        
        G = self.transform(R , G , B)
        
        self.rf , self.gf , self.bf = 0.12 , 0.84 , 0.79
        
        B = self.transform(R , G , B)

        return Image.fromarray(np.array([R, G, B, A]).T, mode="RGBA")
    
    def idk2(self):
        img_array = np.asarray(self.img)

        R = img_array.T[0]
        G = img_array.T[1]
        B = img_array.T[2]
        A = img_array.T[3]

        self.rf , self.gf , self.bf = 0.275 , 0.472 , 0.506
 
        R = self.transform(R, G , B)
        
        self.rf , self.gf , self.bf = 0.144 , 0.819 , 0.305
        
        G = self.transform(R , G , B)
        
        self.rf , self.gf , self.bf = 0.307 , 0.896 , 0.009
        
        B = self.transform(R , G , B)

        return Image.fromarray(np.array([R, G, B, A]).T, mode="RGBA")
    
    def grayscale(self):
        new_image = ImageOps.grayscale(self.img)
        
        return new_image