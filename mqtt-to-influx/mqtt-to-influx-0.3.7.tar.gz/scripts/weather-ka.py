#!/usr/bin/env python3
# pylint #
# vim: tw=100 foldmethod=indent
# pylint: disable=bad-continuation, invalid-name, superfluous-parens
# pylint: disable=bad-whitespace, mixed-indentation
# pylint: disable=redefined-outer-name, logging-not-lazy, logging-format-interpolation
# pylint: disable=missing-docstring, trailing-whitespace, trailing-newlines, too-few-public-methods

from html.parser import HTMLParser
import json
import requests
import paho.mqtt.client as mqtt

base_url = "https://www.karlsruhe.de/b3/wetter"

def mqtt_pub(topic, message, host='q', port=1883, qos=1, clientid='ka-weather'):
    mqttc = mqtt.Client(clientid)
    mqttc.connect(host, port, keepalive=10)
    mqttc.loop_start()
    infot = mqttc.publish(topic, message, qos=qos)
    infot.wait_for_publish()
    mqttc.disconnect()

def get_data_by_url(url):
    orientation = {}
    orientation['select']=False
    orientation ['next_metric'] = None
    orientation['date_coming'] = False
    orientation['date_coming_in'] = 0
    total_time = ""
    htmldata = {}
    metrics = ['Lufttemperatur', 'Fühltemperatur', 'Luftdruck', 'Luftfeuchtigkeit', 
            'Niederschlag', 'Windstärke', 'Globalstrahlung', 'Windrichtung']

    class MyHTMLParser_streets(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag=="span":
                # print(F"Start tag: >>{tag}/{attrs}<<")
                orientation['date_coming'] = True
            pass
        def handle_endtag(self, tag):
            # print(F" end  >>{tag}<<")
            pass
        def handle_data(self, data):
            if data in metrics:
                # print(F"Encountered some data: {data}")
                orientation[F'{data}_coming_in'] = 2
                orientation['next_metric'] = data
            if orientation['next_metric']:
                # print (F"nm true")
                nm = orientation['next_metric']
                orientation[F'{nm}_coming_in'] -= 1

                # print (F"  Checking next metric: {nm}: {orientation[F'{nm}_coming_in']} ")
                if orientation[F'{nm}_coming_in'] == -1:
                    orientation['next_metric'] = False
                    htmldata[nm] = data
                    # print (F"    found: {data}")
                    if nm == 'Niederschlag':
                        orientation['next_metric'] = F"Niederschlag_tag"
                        orientation['Niederschlag_tag_coming_in'] = 1
                    if nm == 'Windstärke':
                        orientation['next_metric'] = F"Windstärke_kmh"
                        orientation['Windstärke_kmh_coming_in'] = 1
                    if nm == 'Windstärke_kmh':
                        orientation['next_metric'] = F"Windstärke_kmh_max"
                        orientation['Windstärke_kmh_max_coming_in'] = 1
            if orientation['date_coming']:
                if data in ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']:
                    orientation['date_coming_in'] = 2
            if orientation['date_coming_in'] == 1:
                # print (F"  Data: {data}")
                date_ = data.split(',')[1].lstrip(' ')
                time_ = data.split(',')[2].split(' ')[1]
                # print (F"  date: '{date}' - time: '{time}'")
                htmldata['date'] = F'{date_}T{time_}'
                # print (json.dumps(total_time))

            if orientation['date_coming_in'] > 0:
                orientation['date_coming_in'] -= 1

                    
    r = requests.get(url)
    parser = MyHTMLParser_streets()
    parser.feed(r.text)

    # post processing:
    metrics.append('Niederschlag_tag')
    metrics.append('Windstärke_kmh')
    metrics.append('Windstärke_kmh_max')
    for metric in  metrics:
        # print (F"{metric:17}: {htmldata[metric]}")
        try:
            htmldata[metric] = float(htmldata[metric].replace(',','.').split(' ')[0])
        except ValueError:
            try:
                htmldata[metric] = float(htmldata[metric].replace(',','.').split('(')[1].split('°')[0])
            except ValueError:
                htmldata[metric] = float(htmldata[metric].replace(',','.').split('\n')[1])
            except IndexError:
                htmldata[metric] = float(htmldata[metric].replace(',','.').split('bzw.')[1])
        # print (F"{metric:17}: {htmldata[metric]}\n")
    return {"Time": F"{htmldata['date']}", "data":htmldata}

data = get_data_by_url(base_url)
# print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
print(F"Received last update from: {data['Time']}")
mqtt_pub("/weather/ka/status", json.dumps(data))
