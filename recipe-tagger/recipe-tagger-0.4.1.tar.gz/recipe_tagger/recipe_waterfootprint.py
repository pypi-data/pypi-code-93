"""
Module containing all the methods in order to compute the water footprint of an ingredient or recipe. 
"""

import re

import numpy as np
from nltk.corpus.reader import toolbox

from .foodcategory import FoodCategoryWaterFootprint
from .recipe_tagger import get_ingredient_class
from .util import get_embedding, process_ingredients

waterfootprint_embedding_paths = {
    "en": "data/ingredient_waterfootprint_en.npy",
    "it": "data/ingredient_waterfootprint_it.npy",
}


def __calculate_waterfootprint(wf_ing, quantity):
    """
    Calculate the right water footprint of a ingredient from its
    (l/kg) water footprint and the quantity provided (in gr).

    :param wf_ing: the water footprint of the ingredient.
    :param quantity: the quantity of the ingredient.
    :return: the water footprint calcuated on the quantity.
    """
    return round((wf_ing * quantity) / 1000, 2)


def __get_default_waterfootprint(ingredient, language="en"):
    """
    Get the defualt water footprint of a food category. The recipe tagger
    module is used to predict the class of the ingredient.

    :param ingredient: the ingredient to be classified.
    :param language: the language of the ingredient.
    :return: the defualt water footprint of the predicted category.
    """
    ing_class = get_ingredient_class(ingredient, language)
    return FoodCategoryWaterFootprint[ing_class].value if ing_class != None else 50


def __get_quantites_formatted(ingredients, quantities, language):
    """
    Get the list of quantities well formatted in the same unit (gr).
    :param ingredients: the list containing the ingredients.
    :param quantities: the list containing quantites of the ingredients.
    :return: a list with the quantites well formatted in gr.
    """
    embedding = get_embedding(waterfootprint_embedding_paths[language])
    units = {"ml": 0.001, "gr": 1.0, "kg": 1000.0, "L": 1000.0, "l": 1000.0}
    values_units = [re.findall(r"[A-Za-z]+|\d+", q) for q in quantities]
    quantities = []
    for i in range(len(values_units)):
        value_unit = values_units[i]
        if len(value_unit) != 2:
            quantities.append(float(value_unit[0]))
        elif value_unit[1] == "unit":
            quantities.append(float(value_unit[0]) * embedding[ingredients[i]][1])
        elif value_unit[1] == "None":
            quantities.append(0.0)
        else:
            quantities.append(float(value_unit[0]) * units[value_unit[1]] / units["gr"])
    return quantities


def get_ingredient_waterfootprint(
    ingredient, quantity, embedding=None, process=False, language="en"
):
    """
    Get the water footprint of the provided ingredient based on the quantity.
    If the ingredient is not found in the embedding, the recipe tagger module is
    used to search the category of the ingredient and retrieve the footprint based
    on that.

    :param ingredient: the name of the ingredient.
    :param quantity: the quantity of ingredient to calculate water footprint. (in gr)
    :param embedding: the water footprint embedding.
    :param process: a bool indicating if the provided ingredient must be processed.
    :param language: the language of the ingredient.
    :return: the water footprint of the provided ingredient.
    """
    wf_embedding = (
        get_embedding(waterfootprint_embedding_paths[language])
        if not embedding
        else embedding
    )
    ingredient = (
        process_ingredients(ingredient, language=language) if process else ingredient
    )
    ingredient_wf = (
        int(wf_embedding[ingredient][0])
        if ingredient in wf_embedding
        else __get_default_waterfootprint(ingredient, language)
    )
    return __calculate_waterfootprint(ingredient_wf, quantity)


def get_recipe_waterfootprint(
    ingredients, quantities, information=False, language="en"
):
    """
    Get the water footprint of a recipe, providing the ingredients and the
    quantities for each ingredient. Params ingredients and quantities must have
    the same length. Quantites are strings containing the values and the unit
    without spaces (10gr).
    :param ingredients: a list containing all the ingredients of the recipe.
    :param quanities: a list containing all the quantities of the recipe ingredients.
    :param information: a dictionary containing the ingredients and its water footprint.
    :param language: the language of the ingredients.
    :return: an integer representing the water footprint of the recipe and if information
    param is setted to true, return also a dictionary with all ingredients and theirs
    computed water footprints.
    """
    wf_embedding = get_embedding(waterfootprint_embedding_paths[language])
    proc_ingredients = [
        process_ingredients(ing, language=language) for ing in ingredients
    ]
    quantities = __get_quantites_formatted(proc_ingredients, quantities, language)
    total_wf = 0
    information_wf = {}
    for i in range(len(ingredients)):
        ing_wf = get_ingredient_waterfootprint(
            proc_ingredients[i],
            quantities[i],
            embedding=wf_embedding,
            language=language,
        )
        information_wf[ingredients[i]] = ing_wf
        total_wf = round(total_wf + ing_wf, 2)
    return (total_wf, information_wf) if information else total_wf
