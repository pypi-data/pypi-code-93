from DodayUtils._dwrappers import *
from DodayUtils.peripherals.CliTools import *
import xml.etree.ElementTree as ET

# Compile images
# -----------------------
@dutils
def add_img_to_qrc(img_names_list, qrc_file_name, **kwargs):
	"""
	This is the helper function to 
	add images to qrc file
	"""
	tree = ET.parse(qrc_file_name)
	root = tree.getroot()

	current_imgs = []
	for elem in root:
		for subelem in elem:
			current_imgs.append(subelem.text)

	n = len(current_imgs)

	need_to_add_imgs = []
	for img in img_names_list:
		if img in current_imgs or img in need_to_add_imgs:
			continue
		need_to_add_imgs.append(img)

	i = 0
	for add_img in need_to_add_imgs:
		# subelement = root[0][0].makeelement('file', {})
		ET.SubElement(root[0], 'file', {})
		root[0][n+i].text = add_img
		i += 1


	tree.write(qrc_file_name)

@dutils
def compile_qrc_img(img_list, qrc_file_name, binary_file_name="img_bin.py", **kwargs):
	"""
	This is the helper function to compile the qrc image
	and save it to binary file name
	* img_list: ["img/v_pic_4.png", img/v_pic_2.png, ...]
	"""
	add_img_to_qrc(img_list, qrc_file_name)
	# Need to install pyrcc5
	cli_normal_call(["pyrcc5", qrc_file_name, "-o", binary_file_name])


