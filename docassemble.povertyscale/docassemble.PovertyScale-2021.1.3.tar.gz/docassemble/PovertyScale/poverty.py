import json
import sys
from docassemble.base.util import path_and_mimetype, log
from typing import Union

__all__ = ['poverty_scale_income_qualifies',
           'get_poverty_scale_data',
           'poverty_scale_get_income_limit'
          ]

ps_poverty_scale_json_path = path_and_mimetype(f"{__package__}:data/sources/federal_poverty_scale.json")[0]
  
def get_poverty_scale_data():
  ps_data = {}
  try:
    with open(ps_poverty_scale_json_path) as f:
      ps_data = json.load(f)
  except FileNotFoundError:
    log(f"Cannot determine poverty scale: unable to locate file {ps_poverty_scale_json_path}")
  except json.JSONDecodeError as e:
    log(f"Cannot determine poverty scale: is {ps_poverty_scale_json_path} a valid JSON file? Error was {e}")
  
  return ps_data

def poverty_scale_get_income_limit(household_size:int=1, multiplier:int=1)->Union[int, None]:
  """
  Return the income limit matching the given household size.
  """
  ps_data = get_poverty_scale_data()
  if not ps_data:
    return None
  additional_income_allowed = household_size * int(ps_data.get("poverty_increment"))
  household_income_limit = (int(ps_data.get("poverty_base")) + additional_income_allowed) * multiplier
  
  return household_income_limit

def poverty_scale_income_qualifies(total_monthly_income:float, household_size:int=1, multiplier:int=1)->Union[bool,None]:
  """
  Given monthly income, household size, and an optional multiplier, return whether an individual
  is at or below the federal poverty level.
  
  Returns None if the poverty level data JSON could not be loaded.
  """
  # Globals: poverty_increment and poverty_base
  household_income_limit = poverty_scale_get_income_limit(household_size=household_size, multiplier=multiplier)
  
  if not household_income_limit:
    return None
  
  return int((household_income_limit)/12) >=  int(total_monthly_income)
