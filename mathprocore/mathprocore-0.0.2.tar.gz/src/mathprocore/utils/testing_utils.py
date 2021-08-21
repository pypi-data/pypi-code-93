from sys import platform
import json, webbrowser
from importlib import resources
from pathlib import Path
from .driver_utils import group_q_gens, make_questions

def worksheet_latex_output(q_gens, num=5):
	"""Generates a worksheet with problems from q-gens in questions. Opens the worksheet in a web browser.

	:param q_gens: The collection of q-gens. Either a list of q-gens or a dictionary of {topic_name: [q-gens]} values.
	:type q_gens: list or dict
	:param num: The number of problems per q-gen
	:type num: int
	"""
	if type(q_gens) == list:
		q_gens = group_q_gens(q_gens)

	JSON = json.dumps({
		"topics": [make_questions(q_gens, topic_name, num) for topic_name in q_gens]
	})


	# write the json data into a file that will be accessed by the worksheet.	
	with resources.path("test", "dump.js") as dump:
		dump.write_text(f"const jsonData = {JSON};")

	# handling mac's superior os
	if platform == "darwin":
		chrome = "open -a /Applications/Google\\ Chrome.app %s"
	elif platform == "linux":
		chrome = "google-chrome"
	else:
		chrome = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s"

	# open the worksheet in chrome.
	with resources.path("test", "tester_pdf.html") as resource_path:
		webbrowser.get(chrome).open(str(Path(resource_path)))