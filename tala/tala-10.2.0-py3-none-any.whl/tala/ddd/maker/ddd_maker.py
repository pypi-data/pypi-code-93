from io import StringIO
import os
import re

from tala.config import BackendConfig, DddConfig
from tala.ddd.maker import utils
from tala.utils import chdir

GRAMMAR_TEMPLATES_PATHS = {
    "chi": {
        "template_filename": "grammar_chi_template.xml",
        "ddd_relative_path": "grammar/grammar_chi.xml"
    },
    "dut": {
        "template_filename": "grammar_dut_template.xml",
        "ddd_relative_path": "grammar/grammar_dut.xml"
    },
    "eng": {
        "template_filename": "grammar_eng_template.xml",
        "ddd_relative_path": "grammar/grammar_eng.xml"
    },
    "fre": {
        "template_filename": "grammar_fre_template.xml",
        "ddd_relative_path": "grammar/grammar_fre.xml"
    },
    "it": {
        "template_filename": "grammar_it_template.xml",
        "ddd_relative_path": "grammar/grammar_it.xml"
    },
    "pes": {
        "template_filename": "grammar_pes_template.xml",
        "ddd_relative_path": "grammar/grammar_pes.xml"
    },
    "spa": {
        "template_filename": "grammar_spa_template.xml",
        "ddd_relative_path": "grammar/grammar_spa.xml"
    },
    "sv": {
        "template_filename": "grammar_sv_template.xml",
        "ddd_relative_path": "grammar/grammar_sv.xml"
    }
}

INTERACTION_TESTS_TEMPLATES_PATHS = {
    "chi": {
        "template_filename": "interaction_tests_chi_template.txt",
        "ddd_relative_path": "test/interaction_tests_chi.txt"
    },
    "dut": {
        "template_filename": "interaction_tests_dut_template.txt",
        "ddd_relative_path": "test/interaction_tests_dut.txt"
    },
    "eng": {
        "template_filename": "interaction_tests_eng_template.txt",
        "ddd_relative_path": "test/interaction_tests_eng.txt"
    },
    "fre": {
        "template_filename": "interaction_tests_fre_template.txt",
        "ddd_relative_path": "test/interaction_tests_fre.txt"
    },
    "it": {
        "template_filename": "interaction_tests_it_template.txt",
        "ddd_relative_path": "test/interaction_tests_it.txt"
    },
    "pes": {
        "template_filename": "interaction_tests_pes_template.txt",
        "ddd_relative_path": "test/interaction_tests_pes.txt"
    },
    "spa": {
        "template_filename": "interaction_tests_spa_template.txt",
        "ddd_relative_path": "test/interaction_tests_spa.txt"
    },
    "sv": {
        "template_filename": "interaction_tests_sv_template.txt",
        "ddd_relative_path": "test/interaction_tests_sv.txt"
    }
}


class UnexpectedCharactersException(Exception):
    pass


class DddMaker(object):
    def __init__(self, ddd_name, use_rgl, target_dir=".", language="eng"):
        self._validate(ddd_name)
        self._ddd_name = ddd_name
        self._use_rgl = use_rgl
        self._class_name_prefix = self.directory_to_class_name(ddd_name)
        self._target_dir = target_dir
        self._language = language

    @staticmethod
    def directory_to_class_name(directory_name):
        name_with_capitalized_words = directory_name.title()
        class_name = re.sub("[_]", "", name_with_capitalized_words)
        return class_name

    @staticmethod
    def _validate(name):
        if re.match(r'^[0-9a-zA-Z_]+$', name) is None:
            raise UnexpectedCharactersException(
                f"Expected only alphanumeric ASCII and underscore characters in DDD name '{name}', but found others."
            )

    def make(self):
        self._ensure_target_dir_exists()
        self._create_ddd_module()
        self._create_domain_skeleton_file()
        self._create_ontology_skeleton_file()
        self._create_service_interface_skeleton_file()
        self._create_configs()
        self._create_grammar(self._language)
        self._create_interaction_tests(self._language)
        self._create_word_list()

    def _ensure_target_dir_exists(self):
        if not os.path.exists(self._target_dir):
            os.mkdir(self._target_dir)

    def _create_ddd_module(self):
        ddd_path = self._ddd_path()
        if not os.path.exists(ddd_path):
            os.makedirs(ddd_path)
        self._create_empty_file("__init__.py")

    def _create_configs(self):
        with chdir.chdir(self._target_dir):
            BackendConfig.write_default_config(ddd_name=self._ddd_name, language=self._language)
            with chdir.chdir(self._ddd_name):
                DddConfig.write_default_config(use_rgl=self._use_rgl)

    def _create_ontology_skeleton_file(self):
        self._create_skeleton_file("ontology_template.xml", "ontology.xml")

    def _create_domain_skeleton_file(self):
        self._create_skeleton_file("domain_template.xml", "domain.xml")

    def _create_service_interface_skeleton_file(self):
        self._create_skeleton_file("service_interface_template.xml", "service_interface.xml")

    def _create_grammar(self, language):
        self._create_directory_inside_ddd("grammar")
        self._create_empty_file("grammar/__init__.py")
        template_filename = GRAMMAR_TEMPLATES_PATHS[language]["template_filename"]
        ddd_relative_path = GRAMMAR_TEMPLATES_PATHS[language]["ddd_relative_path"]
        self._create_skeleton_file(template_filename, ddd_relative_path, language)

    def _ddd_path(self):
        return os.path.join(self._target_dir, self._ddd_name)

    def _create_empty_file(self, filename):
        path = os.path.join(self._ddd_path(), filename)
        open(path, 'w').close()

    def _create_directory_inside_ddd(self, directory):
        os.mkdir(f"{self._target_dir}/{self._ddd_name}/{directory}")

    def _create_interaction_tests(self, language):
        self._create_directory_inside_ddd("test")
        template_filename = INTERACTION_TESTS_TEMPLATES_PATHS[language]["template_filename"]
        ddd_relative_path = INTERACTION_TESTS_TEMPLATES_PATHS[language]["ddd_relative_path"]
        self._create_skeleton_file(template_filename, ddd_relative_path, language)

    def _create_skeleton_file(self, template_filename, ddd_relative_path, language="eng"):
        target = os.path.join(self._ddd_path(), ddd_relative_path)
        content = self._template_from_file(template_filename, language)
        utils.write_template_to_file(target, content)

    def _create_word_list(self):
        utils.create_word_list_boilerplate(self._ddd_path())

    def _template_from_file(self, filename, language):
        path = os.path.join(utils.TEMPLATES_PATH, filename)
        content = StringIO()
        with open(path) as template:
            for line in template:
                line = line.replace('__app__', self._ddd_name)
                line = line.replace('__lang__', language)
                line = line.replace('__App__', self._class_name_prefix)
                content.write(line)
        return content
