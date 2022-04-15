import random
import string
from time import sleep
import requests
import sys
from requests_toolbelt import MultipartEncoder

url = 'https://themis.ii.uni.wroc.pl/'
host = 'themis.ii.uni.wroc.pl'

def auth():
	with open('login_info', 'r', encoding='utf8') as f:
		login, passwd = f.read().split('\n')

	response = requests.post(url+'login', data={'userid': login, 'passwd': passwd}, headers={'Host': host, 'Referer': 'https://themis.ii.uni.wroc.pl/'})
	return response.request.headers['Cookie']

def get_groups(text: str, type: str, padding: int) -> list[str]:
	list_of_teams = []
	while True:
		finded = text.find(type)
		if finded == -1:
			break
		t = text[finded + padding:finded + 100].split(" ")[0]
		text = text[finded + padding:]
		if t[0] == "\"":
			list_of_teams.append(t)
	return list_of_teams

def print_groups(cookies: str):
	types = {'overseer': 35, "user": 37}
	response = requests.get(url, headers={'Host': host, 'Cookie': cookies})
	lst = []
	for key in types:
		lst += get_groups(response.text, key, types[key])

	for i in lst:
		print(i)

def get_tasks(text: str) -> list[str]:
	list_of_tasks = []
	while True:
		finded = text.find('problem-code')
		if finded == -1:
			break
		t = text[finded + 13:finded + 100].split('>')[2].split('<')[0]
		text = text[finded + 13:]
		list_of_tasks.append(t)
	return list_of_tasks

def print_tasks(cookies: str, group: str):
	response = requests.get(url+group, headers={'Host': host, 'Cookie': cookies})
	lst = get_tasks(response.text)
	
	for i in lst:
		print('\"{}\"'.format(i))

def print_results(text: str):
	text = text.split('<tr>')
	text = text[2:]
	idx = 1
	for i in text:
		t = i.split('<td>')
		print('{}. {}'.format(idx, t[8].split('>')[1].split('<')[0]))
		idx += 1

def sumbit(cookies: str, group: str, task: str, filename: str):

	languages = {
		'cpp': 'g++',
		'c': 'gcc',
		'RAM': 'ram'
	}

	with open(filename, 'r') as f:
		code = f.read()

	fields = {
		'source': code,
		'file': '',
		'lang': languages[filename.split('.')[1]]
	}
	
	boundary = '----WebKitFormBoundary'+ ''.join(random.sample(string.ascii_letters + string.digits, 16))
	m = MultipartEncoder(fields=fields, boundary=boundary)

	headers = {
		"Host": host,
		"Cookie": cookies,
		"Connection": "keep-alive",
		"Content-Type": m.content_type,
		"Referer": url+group+'/'+task
	}

	response = requests.post(url+group+"/"+task+"/submit", headers=headers, data=m)
	ret_code = response.text

	headers2 = {
		"Host": "themis.ii.uni.wroc.pl",
		"Cookie": cookies,
		"Connection": "keep-alive",
		"Referer": url+group+'/'+task
	}

	print('Running...')
	while True:
		sleep(0.25)
		response = requests.get(url+group+"/result/"+ret_code, headers=headers2)
		if response.text.find('compiling.') == -1 and response.text.find('running') == -1 and response.text.find('waiting') == -1:
			break
	print_results(response.text)

help_message = '''
Welcome to The themis submitter

Options:
'list groups' - listing groups
'list tasks <group_name>' - listing tasks in given groupname
'submit <group_name> <task_name> <path_to_src>' - submiting code and prinitng results

ver. 2.71828182...
'''

if (len(sys.argv) == 1):
	print(help_message)

if (len(sys.argv) == 3 and sys.argv[1] == 'list' and sys.argv[2] == 'groups'):
	cookies = auth()
	print_groups(cookies)

if (len(sys.argv) == 4 and sys.argv[1] == 'list' and sys.argv[2] == 'tasks'):
	cookies = auth()
	print_tasks(cookies, sys.argv[3])

if (len(sys.argv) == 5 and sys.argv[1] == 'submit'):
	cookies = auth()
	sumbit(cookies, sys.argv[2], sys.argv[3], sys.argv[4])