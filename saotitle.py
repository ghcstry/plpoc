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

def bt(url,proxies):
	headers = {"Connection":"close","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36","Accept-Encoding":"gzip, deflate","X-Forwarded-For":"127.0.0.1"}
	if 'https://' in url or 'http://' in url:
		url = url
	else:
		url = 'https://' + url
	
	try:
		requests.packages.urllib3.disable_warnings()
		response = requests.get(url=url,headers=headers,timeout=60,proxies=proxies,verify=False)
	except:
		url = url.replace('https://','http://')
		try:
			response = requests.get(url=url,headers=headers,timeout=60,proxies=proxies)
		except Exception as e:
			url = url.replace('http://','')
			out = url + ' ----- 无法连接 ----- ' + str(e)
			print(out)
			log(out)
			return False

	try:
		if response.encoding != 'ISO-8859-1':
			content = response.content.decode(response.encoding)
		elif requests.utils.get_encodings_from_content(str(response.content)) != []:
			content = response.content.decode(requests.utils.get_encodings_from_content(str(response.content))[0])
		else:
			content = response.content.decode('utf-8')
	except:
		if response.content == b'':
			title = '！返回内容为空！'
		else:
			title = '？未知网页编码？'
		out = url + ' ----- ' + str(response.status_code) + ' ----- ' + title
		print(out)
		log(out)
		return True

	if content == '':
		title = '！返回内容为空！'
		out = url + ' ----- ' + str(response.status_code) + ' ----- ' + title
		print(out)
		log(out)
		return True

	try:
		title = re.search('<title.*>.*</title>',content,re.I).group()
	except:
		try:
			title = re.search('<title.*>.*</title>',content.replace('\n',''),re.I).group()
		except:
			title = '！获取标题失败！'
	try:
		tq = re.search('<title.*?>',title,re.I).group()
		th = re.search('</title>',title,re.I).group()
		title = title.replace(tq,'').replace(th,'').replace('\r','').replace('\t','')
	except:
		title = '！获取标题失败！'

	out = url + ' ----- ' + str(response.status_code) + ' ----- ' + title
	print(out)
	log(out)
	return True

def pl(u,proxies,se):
	se.acquire()
	bt(u,proxies)
	se.release()

if __name__ == '__main__':

	ap = argparse.ArgumentParser()
	ap.add_argument('-u','--url',help='xx.com or http://xx.com')
	ap.add_argument('-f','--file',help='file path')
	ap.add_argument('-p','--proxy',help='127.0.0.1:8080')
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

