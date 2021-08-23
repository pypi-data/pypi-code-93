#!/bin/python

import os
import typer
import time
import json
import requests 
import typer

app = typer.Typer()


def get_user(session):
    resp = session.get("http://localhost:8000/api/v1/user/")
    json_data = resp.json()

    return resp.json()


def get_meals(session):
    resp = session.get("http://localhost:8000/api/v1/meals")
    json_data = resp.json()

    return resp.json()

    
def onboard(session):
    url = 'http://localhost:8000/api/v1/user/onboarding/'
    headers = {'Content-Type': 'application/json', "X-CSRF-TOKEN": session.cookies['csrf_access_token']}
    payload = {"activity_level":"sedentary", "gender":"male", "height":180, "weight":80, "objective":"maintain_weight", "number_of_meals_per_days": 6, "birth_date": "2002-07-18"}

    resp = session.post(url, headers=headers, data=json.dumps(payload,indent=4))

    return resp.json()


def get_grocery_list(session):
    url = 'http://localhost:8000/api/v1/meals/grocery_list/'
    headers = {'Content-Type': 'application/json', "X-CSRF-TOKEN": session.cookies['csrf_access_token']}
    current_time = int(time.time()) 
    current_time_plus_7_days = current_time + 7 * 24 * 3600
    payload = {"timestamps": [current_time, current_time_plus_7_days]}
 
    resp = session.post(url, headers=headers, data=json.dumps(payload,indent=4))
    return resp.json()




def ensure_nutrimium_directory_exists():
    directory = ".nutrimium"
    parent_dir = f'/home/{os.environ.get("USER")}'
    path = os.path.join(parent_dir, directory)

    if not os.path.isdir(path):
        os.mkdir(path)
    

def save_cookies(session):
    with open(f'/home/{os.environ.get("USER")}/.nutrimium/credentials', 'w') as outfile:
        json.dump(dict(session.cookies), outfile)


def get_session():
    session = requests.Session()
    with open(f'/home/{os.environ.get("USER")}/.nutrimium/credentials', 'r') as infile:
        try:
            cookies = json.load(infile)
        except:
            cookies = {}
    session.cookies = requests.cookies.cookiejar_from_dict(cookies)
    return session


def _login(use_cache=True):
    session = get_session()
    if 'access_token_cookie' not in session.cookies.keys() or not use_cache:
        identity = typer.prompt("What's your email?")
        password = typer.prompt("What's your password?")
        session = requests.Session()

        url = 'http://localhost:8000/api/auth/'
        headers = {'Content-Type': 'application/json'}
        payload = {'identity': f'{identity}', 'password': f'{password}'}
        resp = session.post(url, headers=headers, data=json.dumps(payload,indent=4))

        if resp.status_code == 200:
            save_cookies(session)
        else:
            raise Exception("Error while trying to log in")

    return session



def handle_errors(response):
    if "error" in response.keys():
        error = response["error"]
        message = error["message"]
        if message == "Your auth token has expired":
            return "You need to login again, type: nutrimium login"

    return None


def run_command(func):
    session = _login()
    response = func(session)
    message = handle_errors(response)
    if message is not None:
        print(message)
    else:
        print(json.dumps(response))


@app.command()
def login():
    ensure_nutrimium_directory_exists()
    _login(use_cache=False)

@app.command()
def user():
    run_command(get_user)
    
@app.command()
def meals():
    run_command(get_meals)

@app.command()
def groceries():
    run_command(get_grocery_list)


    
if __name__ == "__main__":
    app()


