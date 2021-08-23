import logging
import sys, os
import time
import json
from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *
from PIL import Image, ImageDraw, ImageFont

import glob
import re

from reportlab.lib import utils
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

class GraphicFormat:
	def __init__(self, **configs):
		self.graphic_width = 380 # mm
		self.graphic_height = 300 # mm
		self.pdf_width = 38 # mm
		self.pdf_height = 30 # mm
		self.pdf_scale = 0.27
		self.default_font_path = configs.get("default_font_path", "@font/msyh.ttf")
		# Get default font from dodayutils
		self.default_font_path = os.path.dirname(os.path.abspath(__file__))+self.default_font_path.replace('@', '/') \
			if '@' in self.default_font_path else self.default_font_path
			
		self.tmpfile_path = configs["tmpfile_path"]

	def save_img_to_location(self, img, fn):
		# This is the function to save file to location
		img.save(fn)

	def sorted_nicely(self, l):
		""" 
		# http://stackoverflow.com/questions/2669059/how-to-sort-alpha-numeric-set-in-python
	 
		Sort the given iterable in the way that humans expect.
		""" 
		convert = lambda text: int(text) if text.isdigit() else text 
		alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
		return sorted(l, key = alphanum_key)

	def generate_img(self, sticker_format, **kwargs):
		"""
		generate the img file(.png) of input sticker format 
		"""
		init_img = kwargs.get("init_img", None)
		save_flag = kwargs.get("save", True)
		filename = kwargs.get("filename", "img.png")

		if init_img == None:
			img = Image.new('RGB', (self.graphic_width, self.graphic_height), color = (255, 255, 255))
		else:
			img = init_img
		d = ImageDraw.ImageDraw(img)
		self.img_draw_string(d, sticker_format)
		if save_flag:
			img_fp = self.tmpfile_path+"/"+filename
			self.save_img_to_location(img, img_fp)
		
		return img

	@dutils
	def img_draw_string(self, imgdraw, sticker_format, **kwargs):
		"""
		This is the function to draw the sticker
		string on the image canvas. 
		"""
		for line in sticker_format:
			imgdraw.text(line["pos"], line["string"], font=line["font"], fill=line["color"])

	@dutils
	def output_pdf(self, **kwargs):
		# This is the helper function generating a pdf file which contains all .png and .jpg files in the tmp_folder_path
		tmp_folder_path = kwargs.get("tmp_folder_path", self.tmpfile_path)
		outputPdfName = kwargs.get("output_pdf_name", "output_pdf")
		pathToSavePdfTo = tmp_folder_path
		pathToPictures = tmp_folder_path
		splitType = kwargs.get("splitType", "none")
		numberOfEntitiesInOnePdf = kwargs.get("numberOfEntitiesInOnePdf", 1)
		listWithImagesExtensions = kwargs.get("listWithImagesExtensions", ["png", "jpg"])
		picturesAreInRootFolder = kwargs.get("picturesAreInRootFolder", True)
		nameOfPart = "volume"
		self.unite_pictures_into_pdf(outputPdfName, pathToSavePdfTo, pathToPictures, splitType, numberOfEntitiesInOnePdf, listWithImagesExtensions, picturesAreInRootFolder, nameOfPart)
		
		if pathToSavePdfTo[-1] == "/":
			return str(pathToSavePdfTo) + str(outputPdfName) + ".pdf"
		else:
			return str(pathToSavePdfTo) + "/" + str(outputPdfName) + ".pdf"


	def unite_pictures_into_pdf(self, outputPdfName, pathToSavePdfTo, pathToPictures, splitType, numberOfEntitiesInOnePdf, listWithImagesExtensions, picturesAreInRootFolder, nameOfPart):
		
		if numberOfEntitiesInOnePdf < 1:
			print("Wrong value of numberOfEntitiesInOnePdf.")
			return
		if len(listWithImagesExtensions) == 0:
			print("listWithImagesExtensions is empty.")
			return
		
		
		if picturesAreInRootFolder == False:
			foldersInsideFolderWithPictures = self.sorted_nicely(glob.glob(pathToPictures + "/*/"))
			if len(foldersInsideFolderWithPictures) != 0:
				picturesPathsForEachFolder = []
				for iFolder in foldersInsideFolderWithPictures:
					picturePathsInFolder = []
					for jExtension in listWithImagesExtensions:
						picturePathsInFolder.extend(glob.glob(iFolder + "*." + jExtension))
					picturesPathsForEachFolder.append(self.sorted_nicely(picturePathsInFolder))
				if splitType == "folder":
					numberOfFoldersAdded = 0;
					for iFolder in picturesPathsForEachFolder:
						if (numberOfFoldersAdded % numberOfEntitiesInOnePdf) == 0:
							endNumber = numberOfFoldersAdded + numberOfEntitiesInOnePdf
							if endNumber > len(picturesPathsForEachFolder):
								endNumber = len(picturesPathsForEachFolder)
							filename = []
							if numberOfEntitiesInOnePdf > 1:
								filename = os.path.join(pathToSavePdfTo, outputPdfName + "_" + nameOfPart + "_" + str(numberOfFoldersAdded + 1) + '-' + str(endNumber) + "_of_" + str(len(picturesPathsForEachFolder)) + ".pdf")
							elif numberOfEntitiesInOnePdf == 1:
								filename = os.path.join(pathToSavePdfTo, outputPdfName + "_" + nameOfPart + "_" + str(numberOfFoldersAdded + 1) + "_of_" + str(len(picturesPathsForEachFolder)) + ".pdf")
							c = canvas.Canvas(filename)
						for jPicture in iFolder:
							img = utils.ImageReader(jPicture)
							imagesize = img.getSize()
							c.setPageSize(imagesize)
							c.drawImage(jPicture, 0, 0)
							c.showPage()
						numberOfFoldersAdded += 1
						if (numberOfFoldersAdded % numberOfEntitiesInOnePdf) == 0:
							c.save()
							print("created", filename)
					if (numberOfFoldersAdded % numberOfEntitiesInOnePdf) != 0:
							c.save()
							print("created", filename)
				elif splitType == "picture":
					numberOfPicturesAdded = 0;
					totalNumberOfPictures = 0;
					for iFolder in picturesPathsForEachFolder:
						totalNumberOfPictures += len(iFolder)
					for iFolder in picturesPathsForEachFolder:
						for jPicture in iFolder:
							if (numberOfPicturesAdded % numberOfEntitiesInOnePdf) == 0:
								endNumber = numberOfPicturesAdded + numberOfEntitiesInOnePdf
								if endNumber > totalNumberOfPictures:
									endNumber = totalNumberOfPictures
								filename = []
								if numberOfEntitiesInOnePdf > 1:
									filename = os.path.join(pathToSavePdfTo, outputPdfName + "_" + nameOfPart + "_" + str(numberOfPicturesAdded + 1) + '-' + str(endNumber) + "_of_" + str(totalNumberOfPictures) + ".pdf")
								elif numberOfEntitiesInOnePdf == 1:
									filename = os.path.join(pathToSavePdfTo, outputPdfName + "_" + nameOfPart + "_" + str(numberOfPicturesAdded + 1) + "_of_" + str(totalNumberOfPictures) + ".pdf")
								c = canvas.Canvas(filename)
							img = utils.ImageReader(jPicture)
							imagesize = img.getSize()
							c.setPageSize(imagesize)
							c.drawImage(jPicture, 0, 0)
							c.showPage()
							numberOfPicturesAdded += 1
							if (numberOfPicturesAdded % numberOfEntitiesInOnePdf) == 0:
								c.save()
								print("created", filename)
					if (numberOfPicturesAdded % numberOfEntitiesInOnePdf) != 0:
							c.save()
							print("created", filename)
				elif splitType == "none":
					filename = os.path.join(pathToSavePdfTo, outputPdfName + ".pdf")
					c = canvas.Canvas(filename)
					for iFolder in picturesPathsForEachFolder:
						for jPicture in iFolder:
							img = utils.ImageReader(jPicture)
							imagesize = img.getSize()
							c.setPageSize((self.pdf_width*mm, self.pdf_height*mm))
							c.scale(self.pdf_scale, self.pdf_scale)
							c.drawImage(jPicture, 0, 0)
							c.showPage()
					c.save()
					print("created", filename)
				else:
					print("Wrong splitType value")
			else:
				print("No pictures found.")
			return
			
		if picturesAreInRootFolder == True:
			picturesInsideFolderWithPictures = []
			for iExtension in listWithImagesExtensions:
				picturesInsideFolderWithPictures.extend(glob.glob(pathToPictures + "/*." + iExtension))
			picturesInsideFolderWithPictures = self.sorted_nicely(picturesInsideFolderWithPictures)
			if len(picturesInsideFolderWithPictures) != 0:
				if splitType == "picture":
					numberOfPicturesAdded = 0
					totalNumberOfPictures = len(picturesInsideFolderWithPictures)
					for iPicture in picturesInsideFolderWithPictures:
						if (numberOfPicturesAdded % numberOfEntitiesInOnePdf) == 0:
							endNumber = numberOfPicturesAdded + numberOfEntitiesInOnePdf
							if endNumber > totalNumberOfPictures:
								endNumber = totalNumberOfPictures
							filename = []
							if numberOfEntitiesInOnePdf > 1:
								filename = os.path.join(pathToSavePdfTo, outputPdfName + "_" + nameOfPart + "_" + str(numberOfPicturesAdded + 1) + '-' + str(endNumber) + "_of_" + str(totalNumberOfPictures) + ".pdf")
							elif numberOfEntitiesInOnePdf == 1:
								filename = os.path.join(pathToSavePdfTo, outputPdfName + "_" + nameOfPart + "_" + str(numberOfPicturesAdded + 1) + "_of_" + str(totalNumberOfPictures) + ".pdf")
							c = canvas.Canvas(filename)
						img = utils.ImageReader(iPicture)
						imagesize = img.getSize()
						c.setPageSize(imagesize)
						c.drawImage(iPicture, 0, 0)
						c.showPage()
						numberOfPicturesAdded += 1
						if (numberOfPicturesAdded % numberOfEntitiesInOnePdf) == 0:
							c.save()
							print("created", filename)
					if (numberOfPicturesAdded % numberOfEntitiesInOnePdf) != 0:
						c.save()
						print("created", filename)
				elif splitType == "none":
					filename = os.path.join(pathToSavePdfTo, outputPdfName + ".pdf")
					c = canvas.Canvas(filename)
					for iPicture in picturesInsideFolderWithPictures:
						img = utils.ImageReader(iPicture)
						imagesize = img.getSize()
						c.setPageSize((self.pdf_width*mm, self.pdf_height*mm))
						c.scale(self.pdf_scale, self.pdf_scale)
						c.drawImage(iPicture, 0, 0)
						c.showPage()
					c.save()
					print("created", filename)
				else:
					print("Wrong splitType value")
			else:
				print("No pictures found.")
			return