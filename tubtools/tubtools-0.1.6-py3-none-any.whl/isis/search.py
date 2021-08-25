from .common import ISIS_SEARCH_URL

import bs4
import requests
import dataclasses
import json

@dataclasses.dataclass
class Course:
    name: str
    course_id: int
    description: str = None
    category: str = None


def search(args):
    params = {
        'q': args.query,
        'areaids': 'core_course-course',
        'perpage': args.limit if args.limit is not None else 'all'
    }

    rsp = requests.get(ISIS_SEARCH_URL, params=params)
    soup = bs4.BeautifulSoup(rsp.text, 'html.parser')
    courses = []

    for d in soup.find_all('div', class_='coursebox'):
        info = d.find('div', class_='info').find('h3', class_='coursename')
        name = info.text
        course_id = d.get('data-courseid')

        content = d.find('div', class_='content')
        summary = content.find('div', class_='summary')
        description = summary.text if summary is not None else None
        category = content.find('div', class_='coursecat').find('a').text

        c = Course(name, course_id, description=description, category=category)
        courses.append(c)

    if not args.json:
        for c in courses:
            print(f'{c.course_id}, {c.name}, {c.category}')
    else:
        print(json.dumps(list(map(lambda c: dataclasses.asdict(c), courses)), indent=4, ensure_ascii=False))


if __name__ == '__main__':
    class Object:
        pass
    import argparse
    args = argparse.Namespace()
    args.query = 'Rechnernetze und Verteilte Systeme'
    args.limit = None
    args.json = True
    search(args)
