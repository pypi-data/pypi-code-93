# !/usr/bin/env python3
# coding: utf-8
import os

import click
import qrcode


def _get_cmd_value(cmd: str, startswith: str):
    with os.popen(cmd) as f:
        for line in f.read().split('\n'):
            if line.strip().startswith(startswith):
                return line.split(':')[1].strip()


def get_ssid():
    cmd = 'CHCP 65001 && netsh wlan show interfaces | findstr SSID'
    return _get_cmd_value(cmd, 'SSID')


def get_password(ssid):
    cmd = f'CHCP 65001 && netsh wlan show profile name={ssid} key=clear'
    return _get_cmd_value(cmd, 'Key Content')


def get_wifi_str(s, p, t='WPA', h='false'):
    return f'WIFI:T:{t};S:{s};P:{p};H:{h};'


@click.command()
def main():
    ssid = get_ssid()
    password = get_password(ssid)
    wifi_str = get_wifi_str(ssid, password)
    print(wifi_str)
    q = qrcode.QRCode()
    q.add_data(wifi_str)
    q.print_ascii()


if __name__ == '__main__':
    main()
