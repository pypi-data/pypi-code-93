#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 18:08:49 2021

@author: nattawoot
"""
import pandas as pd
import os
import copy
from collections import namedtuple
from dataclasses import dataclass, field
from typing import List

from datetime import datetime
from loguru import logger

from wud.aws import s3bucket_json_get


def convar_dict():
    convar_dict = s3bucket_json_get('wud-cloudhouse','maruball_convar.json')
    return convar_dict


@dataclass
class Match:
    kot: datetime = ''
    team_home: str = ''
    team_away: str = ''
    link: str = ''
    league: str = ''
    
    def __repr__(self):
       return f'{self.team_home}-{self.team_away}'   
   
@dataclass
class MatchBet(Match):
    hdc: float = ''
    hdc_side: str = ''
    odd_home: float = ''
    odd_away: float = ''
    source: str = ''
    hdc_list: list = field(default_factory=list)
    
    def __repr__(self):
       return f'{self.team_home}-{self.team_away}'   
    
@dataclass    
class PrevMatch(Match):
    score_home: str = ''
    score_away: str = ''
    
@dataclass    
class MatchPreview(Match):
    prev_meets: List[PrevMatch] = None
    latest_matches_home: List[PrevMatch] = None
    latest_matches_away: List[PrevMatch] = None
    
    
@dataclass
class Player:
    name: str = ''
    team: str = ''
    goal: int = None
    assist : int = None


def team_name_revise0(team, source_input, source_output):
    
    epl = copy.deepcopy(convar_dict['team_name']['epl'])
    ucl_erp = copy.deepcopy(convar_dict['team_name']['ucl_erp'])
    tpl = copy.deepcopy(convar_dict['team_name']['tpl'])
    etc = copy.deepcopy(convar_dict['team_name']['etc'])

    Team = namedtuple("Team", ['footballapi', 'livescore', 'short', 'league'])   

    
    
    team_set = []
    for t in epl:
        t.append('epl')
        team_set.append(Team(*t))
    for t in ucl_erp:
        t.append('ucl_erp')
        team_set.append(Team(*t))
        
    for t in tpl:
        t.append('tpl')
        team_set.append(Team(*t))
        
    for t in etc:
        t.append('etc')
        team_set.append(Team(*t))
        
        
    result = team
    
    for i in team_set:
        if getattr(i, source_input) == team:
            result = getattr(i, source_output)
            break
        
    return result

def team_name_revise(team, source_input, source_output):
    
    this_folder = os.path.dirname(os.path.abspath(__file__))

    df = pd.read_csv(os.path.join(this_folder,'football_team_name.csv'))
    try:
        row = df.loc[df[source_input] == team]
        result = row.iloc[0][source_output]
    except (IndexError, KeyError):
        logger.warning(f'wud.football.team_name_revise - no register for {team}')
        result = team
        
        if(source_output=='abbv'):
            result = result[:3]

        
    if(pd.isnull(result))   :
        logger.warning(f'wud.football.team_name_revise - blank cell in csv for {team}')
        
        result = team
        if(source_output=='abbv'):
            result = result[:3]
            
    return result

def get_hdc_result(hdc, hdc_side, score_home, score_away):
    
    hdc = float(hdc)
    score_home = float(score_home)
    score_away = float(score_away)
    
    if hdc_side == 'home':
        score_away = score_away + hdc
    else:
        score_home = score_home + hdc
    
    if score_home - score_away > 0.25:
        hdc_side_win = 'home'
        return_factor = 1
        
    elif score_home - score_away == 0.25:
        hdc_side_win = 'home'
        return_factor = 0.5
        
    elif score_home - score_away == 0:
        hdc_side_win = 'home'
        return_factor = 0
        
    elif score_home - score_away == -0.25:
        hdc_side_win = 'away'
        return_factor = 0.5

    else:        
        hdc_side_win = 'away'
        return_factor = 1

    return (hdc_side_win, return_factor)    

def get_hdc_return(hdc_side_win, return_factor , play_side, play_amount):
    if play_side == 'minus':
        result = -1*int(play_amount)
    elif hdc_side_win == play_side:
        result = int(play_amount)*return_factor
    else:
        result = -1*int(play_amount)*return_factor
        
        
        
    return result

def tor_rong_win(hdc, hdc_side, score_home, score_away):
    hdc = float(hdc)
    score_home = float(score_home)
    score_away = float(score_away)
    
    hdc_side_win, return_factor = get_hdc_result(hdc, hdc_side, score_home, score_away)    
    
    if hdc == 0:
        result = ('n_a', 0)
    elif return_factor == 0:
        result = ('draw', 0)
        
    elif hdc_side == hdc_side_win:
        result = ('tor', return_factor)
    
    else:
        result = ('rong', return_factor)
        

    return result
