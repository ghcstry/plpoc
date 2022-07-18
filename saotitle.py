#!/usr/bin/python3
#coding: utf-8

import re
import requests
import argparse
import threading

def urls(path):
	with open(path,'r') as f:
		urls = f.readlines()
		return urls

def log(log):
	with open('titlelog.txt','a+',encoding='utf-8') as f:
		f.write(log + '\n')
	return log

def bt(url,proxies):
	headers = {"Connection":"close","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36","Accept-Encoding":"gzip, deflate","X-Forwarded-For":"127.0.0.1"}
	requests.packages.urllib3.disable_warnings()

	if 'https://' in url or 'http://' in url:
		try:
			response = requests.get(url=url,headers=headers,timeout=60,proxies=proxies,verify=False)
		except Exception as e:
				print(url + ' ----- 无法连接！')
				log(url + ' ----- 无法连接 ----- ' + str(e))
				return False
	else:
		url = 'https://' + url
		try:
			response = requests.get(url=url,headers=headers,timeout=60,proxies=proxies,verify=False)
		except:
			url = url.replace('https://','http://')
			try:
				response = requests.get(url=url,headers=headers,timeout=60,proxies=proxies)
			except Exception as e:
				url = url.replace('http://','')
				print(url + ' ----- 无法连接！')
				log(url + ' ----- 无法连接 ----- ' + str(e))
				return False

	try:
		if response.encoding != 'ISO-8859-1' and response.encoding != None:
			content = response.content.decode(response.encoding)
		elif requests.utils.get_encodings_from_content(str(response.content)) != []:
			content = response.content.decode(requests.utils.get_encodings_from_content(str(response.content))[0])
		else:
			content = response.content.decode('utf-8')
	except:
		if response.content == b'':
			title = '！返回内容为空导致未知编码！'
		else:
			title = '！网页解码出错！'
		print(log(url + ' ----- ' + str(response.status_code) + ' ----- ' + title))
		return False

	if content == '':
		title = '！返回内容为空！'
		print(log(url + ' ----- ' + str(response.status_code) + ' ----- ' + title))
		return False

	try:
		title = re.search('<title.*>.*</title>',content,re.I).group()
	except:
		try:
			title = re.search('<title.*>.*</title>',content.replace('\n',''),re.I).group()
		except:
			title = '！标题匹配失败！'
			print(log(url + ' ----- ' + str(response.status_code) + ' ----- ' + title))
			return False

	try:
		title = re.sub('<title.*?>|</title>|\r|\t','',title,flags=re.I)
	except:
		title = '！获取标题错误！'
	print(log(url + ' ----- ' + str(response.status_code) + ' ----- ' + title))
	return True

def pl(u,proxies,se):
	se.acquire()
	bt(u,proxies)
	se.release()

if __name__ == '__main__':

	ap = argparse.ArgumentParser()
	ap.add_argument('-u','--url',help='xx.com or http://xx.com')
	ap.add_argument('-f','--file',help='file path')
	ap.add_argument('-p','--proxy',help='http://127.0.0.1:8080')
	ap.add_argument('-t','--thread',help='xiancheng 10',type=int,default=10)
	args = vars(ap.parse_args())

	if args['proxy'] != None:
		proxies = {'http':args['proxy'],'https':args['proxy']}
	else:
		proxies = {}

	if args['file'] != None:
		se = threading.BoundedSemaphore(args['thread'])
		for u in urls(args['file']):
			u = u.replace('\n','')
			t = threading.Thread(target=pl,args=(u,proxies,se,))
			t.start()

	if args['url'] != None:
		bt(args['url'],proxies)
