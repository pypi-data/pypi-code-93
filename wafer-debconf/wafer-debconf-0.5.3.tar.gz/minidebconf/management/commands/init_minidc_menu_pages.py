from django.core.management.base import BaseCommand

from wafer.pages.models import Page


PAGES = [
    {
        "name": "Home page",
        "slug": "index",
        "include_in_menu": False,
    },
    {
        "name": "About",
        "slug": "about",
        "include_in_menu": True,
        "children": [
            {
                "name": "About the event",
                "slug": "event",
                "include_in_menu": True,
            },
            {
                "name": "Code of Conduct",
                "slug": "coc",
                "include_in_menu": True,
            },
            {
                "name": "Organizers",
                "slug": "org",
                "include_in_menu": True,
            },
        ]
    },
    {
        "name": "Contribute",
        "slug": "contribute",
        "include_in_menu": True,
        "children": [
            {
                "name": "Call for Proposals",
                "slug": "cfp",
                "include_in_menu": True,
            },
            {
                "name": "Important dates",
                "slug": "important-dates",
                "include_in_menu": True,
            },
        ]
    },
    {
        "name": "Schedule",
        "slug": "schedule",
        "include_in_menu": True,
    },
]


class Command(BaseCommand):
    help = 'Create sample set of pages for a MiniDebConf'

    def handle(self, *args, **options):
        if Page.objects.count():
            return
        self.create_pages(None, PAGES)

    def create_pages(self, parent, pages):
        for i, entry in enumerate(pages):
            self.create_page(menu_order=i, parent=parent, **entry)

    def create_page(self, **data):
        try:
            children = data.pop("children")
        except KeyError:
            children = []
        name = data["name"]
        content = f"# {name}\n\n"
        page = Page.objects.create(content=content, **data)
        print(f"Created page {page}")
        if children:
            self.create_pages(page, children)

