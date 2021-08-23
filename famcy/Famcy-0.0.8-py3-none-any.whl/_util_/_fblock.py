# -*- coding: UTF-8 -*-
import abc
import copy
import base64
import random
import Famcy

def fblock_id_generator(fblock_id_key):
    """
    This is the helper function to 
    create unique key from fblock id
    key. 
    Returns fblock id
    """
    return base64.b64encode(fblock_id_key.encode('UTF-8')).decode('UTF-8').replace('=', '0')

class FBlock(metaclass=abc.ABCMeta):
    """
    Represents the base class of the fblock 
    function that displays and handles
    submissions. 

    Interface:
        render_html: render the html content
            for the block
        handle_submission: handle form submit
            action
    """
    def __init__(self, _submission_handler=lambda i,**c: None, **kwargs):
        self.context = copy.deepcopy(kwargs)
        self.submission_lambda = _submission_handler
        # self.fblock_id_key = kwargs.get("fblock_id_key", str(random.getrandbits(16)))
        # self._check_rep_()
        
    def _check_rep_(self):
        """
        Rep invariant:
            * need id for each fblock and
             id/names for each value entries
            * if values in entry, values need
             to be a list and all its elements
             are a dictionary
        """
        if "id" not in self.context:
            gen_id = fblock_id_generator(self.fblock_id_key)
            print("id", gen_id)
            self.context["id"] = gen_id
            self.context["target_id"] = "b_" + gen_id

        if "values" in self.context:
            assert isinstance(self.context["values"], list)
            for i in range(len(self.context["values"])):
                value_entry = self.context["values"][i]
                # Check value type
                assert isinstance(value_entry, dict)

                # check id and names in values entry
                if "id" not in value_entry:
                    value_entry["id"] = self.context["id"] + "-%d"%i
                    value_entry["name"] = self.context["id"] + "-%d"%i

    def link_submission_actions(self, path):
        """
        This is the helper function to link the submission 
        action to the instance. 
        """
        if "action" not in self.context or "method" not in self.context:
            self.update_page_context({
                "action": "/"+path,
                "method": "post"
            })

    def update_id(self, id_key):
        """
        This is the function to update the id key
        """
        self.fblock_id_key = id_key
        self._check_rep_()

    def update_page_context(self, update_dict):
        """
        Mutator function to update the context
        dictionary of the fblock
        """
        self.context.update(update_dict)
        self._check_rep_()

    def get_target_html(self, **configs):
        return self.render_html(self.context, **configs)

    def render(self, **configs):
        return self.render_html(self.context, **configs)

    def load_script(self, **configs):
        return self.extra_script(**configs)

    def handle_submission(self, submissions, **configs):
        """
        This is the function that
        handles submission. 
        """
        sub_list = Famcy.put_submissions_to_list(submissions, self.context["id"])

        submission_context = configs
        submission_context.update(self.context)
        return self.submission_lambda(sub_list, **submission_context)

    # Interface methods
    # ------------------------------------
    @classmethod
    @abc.abstractmethod
    def generate_template_content(cls, fblock_type=None):
        """
        This is the function that
        returns the template content 
        for the given fblock. 
        - Input:
            optional types for different type of
            content of fblock
        - Return a content dictionary
        """
        return NotImplemented

    @abc.abstractmethod
    def render_html(self, context, **configs):
        """
        This is the rendering function
        for fblock. 
        """
        return NotImplemented
