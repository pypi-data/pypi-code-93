"""Main file that actually builds the static website."""

import os
import shutil
import logging

import frontmatter
from jinja2 import Environment, FileSystemLoader

_logger = logging.getLogger(__name__)


class SiteGenerator:
    """
        Class to build the static website.
    """

    def __init__(self, args):
        """
        Initialization of the SiteGenerator class.

        :param args: sys arguments
        """

        self.output_dir = args.output_dir
        self.template_dir = args.template_dir
        self.src_dir = args.src_dir

        self.env = Environment(loader=FileSystemLoader('template'))
        self.tags = set()
        self.recipes = []
        self.empty_output_dir()
        self.copy_assets()
        self.render_index_page()
        self.make_recipes()

    def empty_output_dir(self):
        """
        Ensure the public directory is empty before generating.

        :return:
        """
        try:
            os.mkdir('./' + self.output_dir)
        except IOError:
            _logger.warning("Error making new output dir")

        try:
            shutil.rmtree('./' + self.output_dir)
            os.mkdir('./' + self.output_dir)
        except IOError:
            _logger.warning("Error cleaning up old files.")

    def copy_assets(self):
        """
        Copy static assets to the public directory.

        :return:
        """
        try:
            shutil.copytree(self.template_dir + '/static', self.output_dir + '/static')
        except IOError:
            _logger.warning("Error copying static assets files.")
        try:
            shutil.copytree('data/pix', self.output_dir + '/static/data')
        except IOError:
            _logger.warning("Error copying static assets files.")

    def render_index_page(self):
        """
        Render the index page

        :return:
        """
        _logger.debug("Rendering index page to static file.")
        index_md = frontmatter.load(self.src_dir + '/index.md')
        template = self.env.get_template('index.html')

        with open(self.output_dir + '/index.html', 'w+') as file:
            html = template.render(
                title=index_md['title'],
                author=index_md['author'],
            )
            file.write(html)

    def make_recipes(self):
        """
        Make all the recipes.

        """
        directory = os.fsencode(self.src_dir)
        # loop over all recipes in folder and render them
        for recipe in os.listdir(directory):
            if recipe == b'index.md':
                continue
            else:
                recipe_md = frontmatter.load(os.path.join(directory, recipe))
                if recipe_md['img'] is None:
                    self.render_page(recipe.decode("utf-8"), 'recipe.html')
                else:
                    self.render_page(recipe.decode("utf-8"), 'recipe_img.html')

    def add_tags(self, tags):
        """
        Add tags to the set of tags.

        Args:
            tags (list): tags in recipe
        """
        for item in tags:
            self.tags.add(item)

    def render_page(self, recipe, template):
        """
        Render a recipe using specified template

        :param recipe: path to recipe markdown file
        :param template: template to use for rendering
        :return:
        """

        _logger.debug("Rendering recipe %s using template %s to static file.", recipe, template)
        self.recipes.append(recipe)
        recipe_md = frontmatter.load(self.src_dir + '/' + recipe)
        self.add_tags(recipe_md['tags'])

        template = self.env.get_template(template)
        with open(self.output_dir + recipe_md['title'], 'w+') as file:
            html = template.render(
                title=recipe_md['title'],
                author=recipe_md['author'],
                tags=recipe_md['tags'],
                recipe=recipe_md,
            )
            file.write(html)
