import importlib
import os
import pkgutil

from django.conf.urls import url

from jaad.utils import camel_case_to_snake_case
from jaad.view import JaadView


def activate_if(*conditions):
    def add_activate_if(view):
        view.activate_if_conditions = conditions
        return view

    return add_activate_if


def jaad_views(base_module):
    """
    Recursively look for JaadViews in the module `base_module` and generate URLs based on their
     name and location
    """
    if isinstance(base_module, str):
        base_module = importlib.import_module(base_module)

    base_module_name = base_module.__name__
    prefix = base_module_name + "."
    # todo: support of multiple paths for one module
    base_module_path = base_module.__path__[0]
    base_module_dir = os.path.dirname(base_module_path)

    urlpatterns = look_for_views(base_module_path, prefix, base_module_dir)

    # todo: support of namespaces and app names
    return urlpatterns, None, None


def look_for_views(module_path, prefix, base_module_dir):
    urlpatterns = []

    for _, sub_module_name, is_a_sub_package in pkgutil.iter_modules(
        [module_path], prefix
    ):
        if is_a_sub_package:
            sub_package_prefix = sub_module_name + "."
            sub_package_relative_path = sub_module_name.split(".")
            urlpatterns += look_for_views(
                os.path.join(base_module_dir, *sub_package_relative_path),
                sub_package_prefix,
                base_module_dir,
            )
        else:
            submodule = importlib.import_module(sub_module_name)
            submodule_elements = dir(submodule)

            for element_name in submodule_elements:
                is_internal = element_name.startswith("_")
                if is_internal:
                    continue

                element = getattr(submodule, element_name)

                is_an_imported_root_module = not hasattr(element, "__module__")
                if is_an_imported_root_module:
                    continue

                element_module = getattr(submodule, element_name).__module__

                is_located_in_the_module = element_module == sub_module_name
                if not is_located_in_the_module:
                    continue

                is_not_a_class = not isinstance(element, type)
                if is_not_a_class:
                    continue

                is_not_a_view = not issubclass(element, JaadView)
                if is_not_a_view:
                    continue

                view_should_not_be_displayed = any(
                    condition() is False for condition in element.activate_if_conditions
                )
                if view_should_not_be_displayed:
                    continue

                view_module_path = element_module.split(".")
                url_definition = "/".join(view_module_path[1:-1])
                urlpatterns.append(
                    url(
                        fr"^{url_definition}$",
                        element.as_view(),
                        name=camel_case_to_snake_case(element.__name__),
                    )
                )

    return urlpatterns
