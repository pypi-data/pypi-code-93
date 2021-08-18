import requests
import json
import bs4
import os
import re

os.chdir(os.getcwd())

class Scratch:
    API_URL = 'https://api.scratch.mit.edu/'
    CDN_URL = 'https://cdn2.scratch.mit.edu/'
    SPI_URL = 'https://scratch.mit.edu/site-api/'
    PSI_URL = 'https://projects.scratch.mit.edu/'

    def getUserProj(user:str, num=1):
        r = json.loads(requests.get('{}users/{}/projects/'.format(Scratch.API_URL, user)).text)
        ids = []
        for i in range(0, num):
            ids.append(str(r[i]['id']))
        return ids

    def getProjThumb(id:str, url=False, file='thumbnail.png'):
        if url == False:
            r = requests.get('{}get_image/project/{}_640x372.png'.format(Scratch.CDN_URL, id), stream=True)
            if r.status_code == 200:
                with open(file, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
            else:
                print('The ID for this project is invalid!')
        elif url == True:
            return '{}get_image/project/{}_640x372.png'.format(Scratch.CDN_URL, id)

    def searchProj(query:str, num=1):
        r = json.loads(requests.get('{}search/projects/?mode=trending&q={}'.format(Scratch.API_URL, query)).text)
        ids = []
        for i in range(0, num):
            ids.append(str(r[i]['id']))
        return ids

    def getInfo(id:str):
        r = json.loads(requests.get('{}projects/{}'.format(Scratch.API_URL, id)).text)
        j = { 'title':r['title'],'author':r['author']['username'],'share':r['history']['shared'],'stats':r['stats'], 'remix': 'False' }
        if r['remix']['root']:
             j['remix'] = r['remix']['root']
        return j

    def getUserAv(user:str, url=False, file='userav.gif'):
        if url == False:
            uid = json.loads(requests.get('{}users/ajskateboarder/'.format(Scratch.API_URL)).text)['id']
            r = requests.get('{}get_image/user/{}_60x60.png'.format(Scratch.CDN_URL, uid), stream=True)
            if r.status_code == 200:
                with open(file, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
        elif url == True:
            uid = json.loads(requests.get('{}users/ajskateboarder/'.format(Scratch.API_URL)).text)['id']
            return '{}get_image/user/{}_60x60.png'.format(Scratch.CDN_URL, uid)

    def exists(ini:str):
        if re.match('^[0-9]*$', ini):
            r = requests.get('https://api.scratch.mit.edu/projects/{}'.format(ini))
            if r.status_code == 200:
                return True
            else:
                return None
        elif re.match('^[a-zA-Z]+$', ini, re.IGNORECASE):
            r = requests.get('https://api.scratch.mit.edu/users/{}'.format(ini))
            if r.status_code == 200:
                return True
            else:
                return None

    def getProjComments(id:str, num=1):
        def Commentformat(string):
            comment = string.replace('        ', '').replace('\n\n', '').replace('Reply', '').replace('    ', '').split('\n')
            while '  ' in comment:
                comment.remove('  ')
            return comment

        r = requests.get('{}comments/project/{}'.format(Scratch.SPI_URL, id))
        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        rawcomments = []
        formattedcomments = []

        for tr in soup.find_all('li'):
            values = [div.text.strip('\n') for div in tr.find_all('div', {'class':'comment'})]
            rawcomments.append(values)
        for i in range(0, num):
            comment = rawcomments[i][0]
            formattedcomments.append(Commentformat(comment))
            
        return formattedcomments

    def getUserComments(user:str, num=1):
        def Commentformat(string):
            comment = string.replace('        ', '').replace('\n\n', '').replace('Reply', '').replace('    ', '').split('\n')
            while '  ' in comment:
                comment.remove('  ')
            return comment

        r = requests.get('{}comments/user/{}'.format(Scratch.SPI_URL, user))
        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        rawcomments = []
        formattedcomments = []

        for tr in soup.find_all('li'):
            values = [div.text.strip('\n') for div in tr.find_all('div', {'class':'comment'})]
            rawcomments.append(values)
        for i in range(0, num):
            comment = rawcomments[i][0]
            formattedcomments.append(Commentformat(comment))
            
        return formattedcomments

    def cloneProj(id:str, file='scratchproject.sb3'):
        r = requests.get('{}internalapi/project/{}/get'.format(Scratch.PSI_URL, id), stream=True)
        if r.status_code == 200:
            with open(file, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)