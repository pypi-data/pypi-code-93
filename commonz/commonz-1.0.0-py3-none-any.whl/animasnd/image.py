#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "provide images support"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "3.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2008"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### images modules
#import pygame # designed for writing games. (is not specific to images)

#import scipy # deprecating image I/O functionality and will be removed
### Pillow was the main library used by Scipy for images.

#import imageio # variety of plugins for many images formats.
### Pillow is also the main plugin of imageio for common images

### PIL (Python Image Library) been late adapted on Python3
### then a fork for Python 3 named Pillow been made
### so Pillow and PIL are almost the same
from PIL import Image
from PIL import ImageChops
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
from PIL import ImageFilter

### OpenCV (OpenSource Computer Vision) is available in Debian repo
### But no official OpenCV packages released by OpenCV.org on PyPI
### But on PyPI the not official opencv-contrib-python includes all OpenCV functionality.
import cv2

#import cairo # 2D graphics library


### others required modules
import numpy # use for exporting image as array



### PIL Image modes:
BITMAP_MODE = '1' #1b this binary mode is not respected, pixels values are stored with 0 or 255.
GREY_MODE = 'L' #1o shade of grey varies from 0 to 256
LA_MODE = 'LA' # same as L mode with alpha
INDEX_MODE = 'P' #1o the number of colors in a palette may vary, it is not always 256 colors,
RGB_MODE = 'RGB' #3o true color
HSV_MODE = 'HSV'	#3o Hue, Saturation, Value
RGBA_MODE = 'RGBA' #4o true color with transparency
INT_MODE = 'I' #4o(signed integer) why signed ?? anyway, I did not find any image format with this mode
FLOAT_MODE = 'F' #4o(floating point) I did not find any image format with this mode.

### resize resample:
### If omitted, or if the image has mode “1” or “P”, it is set PIL.Image.NEAREST.
NEAREST=Image.NEAREST# (use nearest pixels neighbour)
BILINEAR=Image.BILINEAR# (linear pixels interpolation)
BICUBIC=Image.BICUBIC# (cubic spline pixels interpolation) **the most interesting***
LANCZOS=Image.LANCZOS# (a high-quality downsampling pixels filter)

### transpose methods:
FLIP_HORIZONTALLY=Image.FLIP_LEFT_RIGHT
FLIP_VERTICALLY=Image.FLIP_TOP_BOTTOM
ROTATE_90=Image.ROTATE_90
ROTATE_180=Image.ROTATE_180
ROTATE_270=Image.ROTATE_270
TRANSPOSE=Image.TRANSPOSE

### text alignement
ALIGN_LEFT="left"
ALIGN_CENTER="center"
ALIGN_RIGHT="right"

### Direction of the text.
### not supported without libraqm
DIR_RTL="rtl" # (right to left)
DIR_LTR="ltr" # (left to right) 
DIR_TTB="ttb" # (top to bottom). Requires libraqm.

### pixel location Indexes
X=0
Y=1

### pixel compo Indexes
R=0
G=1
B=2
A=3

### RGB basics colors
RED=(255,0,0)
GREEN=(0,255,0)
BLUE=(0,0,255)
BLACK=(0,0,0)
WHITE=(255,255,255)



### disable DecompressionBomb safety
#Image.MAX_IMAGE_PIXELS = 200000**2
#Image.warnings.simplefilter('ignore', Image.DecompressionBombWarning)



def image_show(imagefile,title=None):
	"""Load and image file and show it in window"""
	img = cv2.imread(imagefile,cv2.IMREAD_UNCHANGED)
	cv2.imshow(title,img)
	cv2.waitKey(0)#display the window infinitely until any keypress.
	cv2.destroyAllWindows()



class Bitmap :
	"""allow bitmap image manipulation"""
	def __init__(self, mode, size, color):
		"""mode is the format of pixels, size contains x and y image dimension, color concern the image background"""

		self.img= Image.new( mode, size, color )
		
		#self.filename= self.img.filename
		#self.size= self.img.size
		#self.fmt = self.img.format
		#self.mode = self.img.mode
		#self.info = self.img.info
	
	
	def get_info(self):
		"""get extra info about the image"""
		return self.img.info
	
	def get_size(self):
		"""get the x,y size of the image"""
		return self.img.size
	
	def get_mode(self):
		"""get image pixel format info"""
		return self.img.mode

	def get_colors(self):
		"""return the quantity of pixels for each colors"""
		return self.img.getcolors()
	
	def show(self,title=None):
		"""display the image in new window"""
		self.img.show(title)
		
		
	def get_pixel(self,position):
		"""get the valu of image pixel"""
		return self.img.getpixel(position)
		
	def set_pixel(self,position,valu):
		"""change the valu of image pixel"""
		self.img.putpixel(position,valu)

	def set_alpha(self,alpha):
		"""change the transparency of the image"""
		self.img.putalpha(alpha)
		
	def resize(self,new_size,resample=NEAREST):
		"""resize the image by x,y new size"""
		self.img = self.img.resize(new_size,resample)


	def transpose(self,direction):
		"""rotate flip the image
		FLIP_VERTICALLY adapt image for openGL
		ROTATE_270 FLIP_VERTICALLY adapt image for numpy array"""
		self.img = self.img.transpose(direction)


	def offset(self,offset):
		"""displace the image by x,y pixel move"""
		self.img= ImageChops.offset(self.img,offset[X],offset[Y])
		
		
	def crop(self,cut):
		"""cut the image by left,top,right,bottom"""
		self.img= self.img.crop(cut)
		

	def convert(self,mode):
		"""convert image into the given mode"""
		# ImageOps.grayscale(self.img) = self.img.convert('L')
		# image.convert(mode='F') # transforms the image values into float, but without putting them between 0.0 and 1.0
		self.img= self.img.convert(mode)
	
	
	def save(self,output_path):
		"""save image in default format"""
		self.save_png(output_path)
		
	def save_gif(self,output_path):
		"""save image in .gif format"""
		self.img.save(output_path)
		
	def save_bmp(self,output_path):
		"""save image in .bmp format"""
		self.img.save(output_path,compression='bmp_rle')
		
	def save_tga(self,output_path):
		"""save image in .tga format"""
		self.img.save(output_path)
		
	def save_tiff(self,output_path):
		"""save image in .tif format"""
		self.img.save(output_path,compression="tiff_deflate")
		
	def save_png(self,output_path):
		"""save image in .png format"""
		self.img.save(output_path,"PNG",optimize=True)


	def tile(self,scale):#scale mini is (1,1)
		"""repeat the image horizontally and vertically""" 
		new_size=( self.img.size[X]*int(scale[X]) , self.img.size[Y]*int(scale[Y]) )
		result = Image.new(self.img.mode,new_size)# create a new  image
		#print(self.img.size,scale)
		for left in range(0,new_size[X],self.img.size[X]):
			for top in range(0,new_size[Y],self.img.size[Y]):
				#print(left, top)
				result.paste(self.img, (left,top))
		self.img= result


	def get_gl_data(self):
		"""return image data as opengl image""" 
		data = self.img.tobytes("raw",self.img.mode)# tostring() has been removed. Please call tobytes() instead.
		#data = self.img.getData()
		return data

	def get_array(self,tip):
		"""return image data as numpy array""" 
		return numpy.asarray(self.img,dtype=numpy.dtype(tip))


	def mask(self,mask_img):
		"""the grey scale mask_img picels are use for set the image transparency""" 
		self.img.putalpha(mask_img.img)
		
	def blend(self,other_img,mix_factor=0.5):
		"""no change if mix_factor=0, if mix_factor=1 the image is completly remplaced by the other_img"""
		self.img= Image.blend(self.img,other_img.img,mix_factor)

	def compose(self,other_img,alpha_img):
		"""same as blend but instead using mix_factor use alpha pixels valu of alpha_img"""
		self.img= Image.composite(self.img,other_img.img,alpha_img.img)
	
	def overwrite(self,other_img):
		"""write the other image on top of self image"""
		self.img= Image.alpha_composite(self.img,other_img.img)

	def smooth(self,qantum):
		"""makes image edges and points less sharp"""
		for q in range(qantum) :
			self.img= self.img.filter(ImageFilter.SMOOTH_MORE)
			#self.img= self.img.filter(ImageFilter.BLUR)



class Bitmap_File(Bitmap) :
	"""allow bitmap image file manipulation"""
	def __init__(self,image_file):
		"""need to provide an image file pathname"""
		img = Image.open(image_file)

		### Verifies the contents of a file. without decoding the image data. If any problems raises exceptions.
		img.verify()
			
		### after using image.verify(), need to reopen the image file.
		self.img = Image.open(image_file)
		
		
		
class Bitmap_Text(Bitmap) :
	"""allow to write text in bitmap"""
	def __init__(self,font_name,font_size,background_color,text_color,contour_color,contour_size):
		"""need to provide an text data"""
		
		self.font = ImageFont.truetype(font=font_name,size=font_size)

		self.background_color=background_color
		self.text_color=text_color
		self.contour_color=contour_color
		self.contour_size=contour_size
			
		self.img = Image.new ( RGBA_MODE,(1,1),background_color )
		
		
	def write(self,text,dir,align,spacing):
		"""create the appropriate image to write in a text with the font specified previously"""
		total_size=[0,0]
		quantum=0
		for line in text.splitlines():
			line_size= self.font.getsize(line)
			total_size[X]=max(total_size[X],line_size[X])
			total_size[Y]+=line_size[Y]
			quantum+=1
			#print(line_size,total_size)
		total_size[X]+=self.contour_size*2
		total_size[Y]+=self.contour_size*2 + (quantum-1)*spacing
		
		#other_total_size=ImageDraw.textsize(text,font=self.font,spacing=spacing,direction=dir,stroke_width=self.contour_size)
		#print(other_total_size,total_size)
		
		self.img = Image.new( RGBA_MODE,total_size,self.background_color )
		
		draw = ImageDraw.Draw( self.img )
		draw.text((self.contour_size,self.contour_size),text,font=self.font,fill=self.text_color,spacing=spacing,direction=dir,align=align)#,stroke_width=self.contour_size,stroke_fill=self.contour_color )
		
		
