import qrcode

# QR Code generation function
def generate_qrcode_and_save(qr_data):
	"""
	pip install qrcode
	Generate data to PIL image. 
	"""
	qr = qrcode.QRCode(
		version=1,
		box_size=5,
		border=5)
	qr.add_data(qr_data)
	qr.make(fit=True)
	img = qr.make_image(fill='black', back_color='white')
	return img