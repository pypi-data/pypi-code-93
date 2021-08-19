#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import colorama
import click
import os

colorama.init()
requests.adapters.DEFAULT_RETRIES = 5


@click.command()
def cli():
    email = os.environ.get("NETWEY_EMAIL")
    password = os.environ.get("NETWEY_PASSWORD")
    if not email or not password:
        print(f"{colorama.Fore.RED} not NETWEY_EMAIL  or NETWEY_PASSWORD env was set")
        return 
    s = requests.Session()
    response = s.get("https://secure.netwey.com.mx/site")
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    form_login = soup.find(id="form-login")
    token = form_login.find("input", {"name": "_token"})["value"]
    data = {'_token': token, 'dn': email, 'pass': password}
    resp = s.post("https://secure.netwey.com.mx/site/mi-netwey/login", data)
    resp.raise_for_status()
    if resp.json().get("status") == "success":
        resp = s.get("https://secure.netwey.com.mx/site/mi-netwey/mi-cuenta")
        soup = BeautifulSoup(resp.content, "html.parser")
        details_root = soup.find(class_="account-details")
        titles = details_root.find_all(class_="item-title-details")
        details = details_root.find_all(class_="item-cont-details")
        progress = details_root.find(class_="l-progress").string
        v = details_root.find(role="progressbar")["aria-valuenow"]
        print(
            f"{colorama.Fore.GREEN}NETWEY.COM.MX {colorama.Style.DIM} Internet Service"
        )
        print(colorama.Style.RESET_ALL, end="")
        for node_title, node_detail in zip(titles, details):
            if node_title.string and node_detail.string:
                print(
                    f"{colorama.Fore.MAGENTA}{node_title.string.strip()}:"
                    f"{colorama.Fore.WHITE}{node_detail.string.strip()}"
                )
            else:
                print(
                    f"{colorama.Fore.MAGENTA}{node_title.string.strip()}:"
                    f"{colorama.Style.BRIGHT+colorama.Fore.GREEN} {v}% "
                    f"{colorama.Fore.WHITE}{progress.strip()}"
                )
    else:
        print(resp.content)
