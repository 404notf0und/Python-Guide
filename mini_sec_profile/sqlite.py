# -*- coding: utf-8 -*-
import sqlite3
import os
import logging
import codecs

class SQLite(object):
	"""
	sqlite3增删改查
	"""
	def __init__(self,path,is_new=False,script_file=""):
		"""
		init
		:param path:
		:param is_new:
		:param scirpt_file:
		"""
		if is_new:
			if os.path.exists(path):
				os.remove(path)
			if script_file:
				with codecs.open(script_file,mode='rb',encoding='utf-8') as f:
					script=f.read()
					self.sqlite3_conn=sqlite3.connect(path,timeout=20)
					self.executescript(script)
		self.sqlite3_conn=sqlite3.connect(path,timeout=20)
		
	def executescript(self,script):
		"""
		执行sql脚本文件
		"""
		self.sqlite3_conn.executescript(script)

	def execute(self,sql):
		"""
		执行单条sql，无参数
		"""
		logging.debug(sql)
		cursor=self.sqlite3_conn.cursor()
		try:
			r=cursor.execute(sql)
		except Exception as e:
			logging.error("failed execute %s,error:%s" %(sql,repr(e)))

		self.sqlite3_conn.commit()
	
	def executemany(self,sql,params=None):
		"""
		执行多条sql，有参数

		"""
		logging.debug(sql)
		cursor=self.sqlite3_conn.cursor()
		cursor.executemany(sql,params)
		self.sqlite3_conn.commit()

	def query(self,sql):
		"""
		查数据
		"""
		logging.debug(sql)
		cursor=self.sqlite3_conn.cursor()
		try:
			cursor.execute(sql)
		except Exception as e:
			logging.error("failed execute %s,error:%s" %(sql,repr(e)))
		for line in cursor.fetchall():
			yield line

	def close(self):
		"""
		关闭数据库连接
		"""
		self.sqlite3_conn.close()

if __name__=="__main__":
	sql=SQLite("sqlite.db",is_new=True,script_file='script.txt')
	cursor=sql.query("SELECT id, name, address, salary  from COMPANY")
	for i in cursor:
		print(i)
	sql.close()

	# 创建secwiki table
	sql=SQLite("data/secwiki.db")
	sql.execute("create table if not exists secwiki (\
				ts TEXT ,tag TEXT ,url TEXT ,\
				title TEXT,root_domain TEXT,domain TEXT,url_path TEXT);\
				")
	r=sql.query("select * from secwiki")
	print(len([i for i in r]))
