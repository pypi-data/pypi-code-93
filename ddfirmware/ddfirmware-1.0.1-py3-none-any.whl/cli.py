import requests
import sys
import argparse
import datetime
import re
import os
from datetime import datetime

parser = argparse.ArgumentParser(description='Checks for dd-wrt firmware updates')
parser.add_argument('router', type=str)

args = vars(parser.parse_args())

def get_list(year):
    tld = 'https://download1.dd-wrt.com/dd-wrtv2/downloads/betas/'
    url = tld+str(year)
    data = requests.get(url).text
    return data

def date_picker(data,year):
    url = 'https://download1.dd-wrt.com/dd-wrtv2/downloads/betas/'+str(year)+"/"
    pattern = re.findall('(\d+-\d+-\d+-\w+)',data)
    pattern.sort(reverse=True)
    release_date = str(pattern[0]) 
    release = url+release_date+"/"
    release_data = requests.get(release).text
    return release_data, release, release_date

def model_picker(release):
    model = args['router']
    pattern = re.findall('>(.+'+str(model)+'.+)/',release)
    pattern.sort()
    pattern = [i.replace('/<','') for i in pattern] #yeet dis out
    print('These are the routers that match your input:')
    print(*pattern, sep='\n')
    model = input('Which router do you want firmware for?')
    return model


def main():
    dt = datetime.now()
    year = dt.year
    ymd = dt.strftime('%Y-%m-%d')

    # This reaches out to dd-wrt and pulls down a list of releases
    data = get_list(year)

    # This regex matches all the releases, sorts descending and prompts for user to pick
    release = date_picker(data,year)[0]
    release_url = date_picker(data,year)[1]
    info = date_picker(data,year)[2]
    
    # Request specific model type
    model = model_picker(release)

    # Enumerate PWD
    path = '.'
    files = os.listdir(path)
    files.sort(reverse=True)
    print('LS of current directory:')
    print(*files, sep='\n')

    #get binary
    target = model+'-webflash.bin'
    prompt = input('Download '+info+'_'+target+'? (Y/n)')
    if prompt == 'n':
        quit()
    else:
        pass
    binary = requests.get(release_url+model+"/"+target)
    open(info+'_'+target, 'wb').write(binary.content)
    print('Wrote '+info+'_'+target)

if __name__ == '__main__':
    main()