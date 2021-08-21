import random, os, importlib, re
import importlib.util
from collections import defaultdict
from pathlib import Path
from sys import platform

allow_classes = [
	"Algebra1",
	"Algebra2",
	"PreCalculus",
	"Calculus"
]

topic_exceptions = [
	"drivers"
]

def package_contents(package_name):
    """Returns an iterable over module imports (ex. "Classes.Algebra1.SketchingLines")

    :param package_name: Directory to the package. (ex. 'Classes.Algebra1')
    :type package_name: str
    """
    MODULE_EXTENSIONS = '.py'

    # validate module
    package_details = package_name.split(".")
    if len(package_details) > 1:
        subject = package_details[1]
        if subject not in allow_classes:
            return set()
    if len(package_details) > 2:
        topic = package_details[2]
        if topic in topic_exceptions:
            return set()

    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return set()

    pathname = Path(spec.origin).parent
    ret = set()
    with os.scandir(pathname) as entries:
        for entry in entries:
            if entry.name.startswith('__'):
                continue
            current = '.'.join((package_name, entry.name.partition('.')[0]))
            if entry.is_file():
                if entry.name.endswith(MODULE_EXTENSIONS):
                    ret.add(current)
            elif entry.is_dir():
                ret.add(current)
                ret |= package_contents(current)

    return ret

def test_q_gen_init(package, test_num = 10):
	"""Returns True if there is no problem with initializing the q-gens 
	or accessing the module.question_list attribute for all modules."""

	topic_exceptions = [
		"drivers"
	]

	all_good = True
	for module in package_contents(package):
		if len(module.split(".")) != 3 or module.split(".")[-1] in topic_exceptions:
			continue

		try:
			mod = importlib.import_module(module)
		except Exception as e:
			print(f"Unable to import q_gens from `{module}`. Likely because q-gens are broken.")
			all_good = False
			continue

		try:
			mod.question_list
		except:
			print(module + " does not have question_list defined.")
			all_good = False
			continue

		for q_gen in mod.question_list:
			try:
				for _ in range(test_num):
					next(q_gen) # make a question
			except:
				print("Trouble with generating questions ...")
				print(f"Module: {module}. q-gen: {q_gen.sub_topic + ' ' + q_gen.directions}.")
				all_good = False

	return all_good

def make_q_gen_ordering(package):
	"""Aggregates the q-gen directions (of type str) to a dictionary.
	This function is used to order the topics on the website display. 

	# {
	# 	subject: {
	# 		topic: {
	# 			subtopic: [directions, ...],
	# 			...,
	# 		},
	# 		...
	# 	},
	# 	...
	# }

	:param package: The package to search in. (ex. Classes.Algebra1, or Classes)
	:type package: str
	:returns: An ordering of directions we currently support.
	:rtype: dict
	"""

	def clean_topic_name(topic):
		# remove the .py, and add space between camelcase
		topic = topic[:-3]
		return re.sub("([A-Z])", " \\1", topic).strip()

	if not test_q_gen_init(package):
		print("Cannot safely use the q-gen files in this package.")
		return {}

	ordering = defaultdict(dict)
	for module in package_contents(package):
		topic = clean_topic_name(module.split(".")[-1])

		mod = importlib.import_module(module)
		question_list = mod.question_list

		# sub_topic: unique list of directions
		topic_dict = defaultdict(set) 
		for q_gen in question_list:
			topic_dict[q_gen.sub_topic].add(q_gen.directions) # no duplicate directions

		# convert sets to lists
		for key in topic_dict:
			topic_dict[key] = list(topic_dict[key])

		ordering[subject][topic] = dict(topic_dict)

	return dict(ordering)

def get_q_gens(package):
	"""Attempts to access all files within Classes.sub_class.
	Note that this is different than the get_q_gens function in the main drivers.py file.

	:param package: ex. Classes.Algebra2, or Classes
	:type package: str
	:returns: an aggregated dictionary of all q-gen lists from the various files.
	:rtype: dict
	"""

	if not test_q_gen_init(package):
		print("Cannot safely use the q-gen files in this package.")
		return {}

	bad_topics = [
		"drivers"
	]

	q_gens = list()
	for module in package_contents(package):
		mod = importlib.import_module(module)
		q_gens.extend(mod.question_list)

	return group_q_gens(q_gens)

def group_q_gens(q_gens):
	"""Groups question generators by their 'sub_topic' attribute.

	:param q_gens: A list of question generators.
	:type q_gens: list
	:returns: a dictionary (key: value) -> (sub topic: list of question generators)
	"""
	assert type(q_gens) == list

	# sub_topic: list of q-gens
	q_gen_map = defaultdict(list)
	for q in q_gens:
		q_gen_map[q.sub_topic].append(q)
	return dict(q_gen_map)

"""Server-support."""
def make_questions(q_gen_map, topic_name, num):
	"""For a single question topic type, choose from a list of question generators
	and return a json-like dictionary to organize topic questions.

	# {
	# 	topicName
	# 	num
	# 	groups
	# }

	:param q_gens: A list of QuestionGenerators to make questions from
	:type q_gens: list
	:param num: The number of questions to generate from this q-gen
	:type num: int
	:rtype: dict
	"""
	try:
		# generate questions. group by directions
		temp = defaultdict(list) # (directions: list of questions)
		choices = q_gen_map[topic_name]
		for _ in range(num):
			choice = random.choice(choices)
			question = next(choice)
			temp[question["directions"]].append(question["q-data"])

		groups = [ {"directions": dr, "questions": qs} for dr, qs in temp.items() ]

		# create the json data object
		data = {
			"topicName": topic_name,
			"num": num,
			"groups": groups
		}
		return data
	except Exception as e:
		print(topic_name)
		raise e


"""
Dictionary structures.

{
	"topics": [
		{
			"topicName": "Write a quadratic function from its vertex and another point", 
			"num": 1, 
			"groups": [
				{
					"directions": "", 
					"questions": [
						{
							"prompt": "\\text{A parabola has vertex (} -8 \\text{, } -9 \\text{) and passes through (} -7 \\text{, } -5 \\text{). Write its equation in vertex form.}", 
							"answer": "4 \\left(x + 8\\right)^{2} - 9", 
							"promptImage": {}, 
							"answerImage": {}
						}
					]
				}
			]
		}
	]

};

topic
	the website offers multiple topics to add to the worksheet
	attributes
		topicName: 
		num: the number of questions in the topic
		groups: every topic can have different types of questions. 
				that is, questions with different directions.

questionGroup
	often times, questions are grouped by directions.
	attributes
		directions: the instructions to complete the question
		questions: a list of objects. each object represents 
					the instructions for displaying a single
					question on the PDF.

question
	instructions for displaying a single question on the website
	attributes
		prompt: str
		answer: str
		promptImage: instructions for displaying an image
		answerImage: ''

"""