#!/bin/python

import random
import string
from time import sleep
import requests
import sys
from requests_toolbelt import MultipartEncoder
import bs4

url = 'https://themis.ii.uni.wroc.pl/'
host = 'themis.ii.uni.wroc.pl'

login = 'Your login'
passwd = 'Your password'

availables_types = frozenset(['overseer', 'admin', 'user'])

def auth():
	response = requests.post(url+'login', data={'userid': login, 'passwd': passwd}, headers={'Host': host, 'Referer': 'https://themis.ii.uni.wroc.pl/'})
	return response.request.headers['Cookie']

def section_available(tag: bs4.element.Tag) -> str:
	return tag.find('div', {'class': 'section-type'}).text.strip() in availables_types

def section_code_and_description(tag: bs4.element.Tag):
	code = tag.find('a', {'class': 'section-enter'})
	return (code.get('href'), code.text)

def get_groups(text: str):
	data = bs4.BeautifulSoup(text, 'html.parser')
	for section in data.find_all('div', {'class': 'section'}):
		if section_available(section):
			code, description = section_code_and_description(section)
			yield "{0} - '{1}'".format(code, description)

def print_groups(cookies: str):
	response = requests.get(url, headers={'Host': host, 'Cookie': cookies})
	for entry in get_groups(response.text):
		print(entry)

def problem_code_and_description(tag: bs4.element.Tag):
	code = tag.find('td', {'class': 'problem-code'})
	desc = tag.find('td', {'class': 'problem-name'})
	if code == None or desc == None:
		raise LookupError
	
	code = code.find('a').text
	desc = desc.find('a').text

	return (code, desc)	

def get_tasks(text: str) -> list[str]:
	data = bs4.BeautifulSoup(text, 'html.parser')
	for problem in data.find_all('tr'):
		try:
			code, desc = problem_code_and_description(problem)
			yield "{0} - '{1}'".format(code, desc)
		except LookupError:
			continue

def print_tasks(cookies: str, group: str):
	response = requests.get(url + group, headers={'Host': host, 'Cookie': cookies})
	for task in get_tasks(response.text):
		print(task)

def print_results(text: str):
	
	text = text.split('<tr>')
	text = text[2:]
	idx = 1
	for i in text:
		t = i.split('<td>')
		if t[8].split('>')[1].split('<')[0] == 'accepted':
			print('{}. {}     {}/{}'.format(idx, t[8].split('>')[1].split('<')[0], t[3].split('<')[0], t[4].split('<')[0]))
		else:
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
		'lang': languages[filename.split('.')[-1]]
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
		if response.text.find('compiling') == -1 and response.text.find('running') == -1 and response.text.find('waiting') == -1:
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
