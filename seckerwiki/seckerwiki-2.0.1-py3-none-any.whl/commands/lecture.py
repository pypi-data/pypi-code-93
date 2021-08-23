"""
This is pretty outdated and is only kept for reference - see scripts/lecture_gen.py 
"""
import glob
import os
import re

from PyInquirer import prompt

from seckerwiki.scripts.lecture_gen import generate_lecture


def lecture(cfg, args):
    # merge all courses from every category into a single list
    courses = [item for key in cfg['courses'].keys() for item in cfg['courses'][key]]

    questions = [
        {
            'type': 'input',
            'name': 'input_file',
            'message': 'Enter path of lecture pdf, or url'
        },
        {
            'type': 'list',
            'name': 'course',
            'message': 'Enter course code',
            'choices': courses
        },
        {
            'type': 'input',
            'name': 'lecture_num',
            'message': 'Enter lecture number',
            'validate': lambda x: x.isdigit(),
            'default': lambda answers: get_latest_lecture_num(cfg, answers['course'])
        },
        {
            'type': 'input',
            'name': 'title',
            'message': 'Enter lecture title',
        }
    ]
    answers = prompt(questions)
    generate_lecture(cfg, answers['input_file'], answers['course'], answers['lecture_num'], title=answers['title'])


def get_latest_lecture_num(cfg, course):
    """
    Return the latest lecture number from the filenames in course
    """
    tri = get_tri_from_course(course, cfg['courses'])
    lecture_dir = os.path.join(cfg['wiki-root'], "Uni", tri, course, "Lectures")

    print(lecture_dir)
    files = [f for f in glob.glob(lecture_dir + "**/*.md", recursive=False)]

    # if no files exist, return 0
    if len(files) < 1:
        print("No recent lectures found.")
        return "1"

    last_file = sorted(files)[-1]

    print("Most recent lecture: " + last_file)

    # use regex to match number (get last as most likely to be lecture num if alphabetised)
    last = re.findall(r'\d+', last_file)[-1]

    # suggest the latest lecture num + 1
    suggested = int(last) + 1 if last.isdigit() else "none"

    return str(suggested)


def get_tri_from_course(course, courses):
    """
    Given a courses dict, return the trimester of the :param course
    """
    for tri in courses:
        for _course in courses[tri]:
            if course == _course:
                return tri.capitalize()
