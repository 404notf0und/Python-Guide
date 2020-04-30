# 取数、作图做表分析、生成md报告
from sqlite import SQLite
from collections import OrderedDict
import matplotlib.pyplot as plt
import os
from github_crawler import path,date_delta
import codecs
from secwiki_crawler import secwiki

def get_top(table='secwiki',column='domain',time=2020,top=10):
	"""
	取top数据作饼图
	:param table:
	:param column:
	:param time:
	:param top:
	:return type:dict
		:return value:percentage(domain top10+other)
	"""
	so = SQLite("data/secwiki.db")
	sql = "select {column},count(url) as ct from {table} \
		  where ts like '%{time}%' \
		  group by {column} \
		  order by ct DESC".format(column=column,table=table,time=time)
	r = so.query(sql)

	od = OrderedDict()
	for i in r:
		od[i[0]]=i[1]
	
	od_pec=dict()
	i=0
	for k,v in od.items():
		if i<top:
			od_pec[k]=round(v/sum(od.values()),4)
		else:
			break
		i=i+1
	od_pec['other']=round(1-sum(od_pec.values()),4)
	return od_pec

def get_details():
	"""
	取相似数据做表：github和微信公众号
	"""

def draw_pie(table='secwiki',column='domain',time=2020,top=10):
	"""
	画饼图，保存
	"""
	od_pec=get_top(table=table,column=column,time=time,top=top)
	labels=od_pec.keys()
	values=od_pec.values()
	explode=[0.1]
	explode.extend([0 for i in range(1,len(od_pec))])

	fig,ax=plt.subplots()
	ax.pie(values,explode=explode,labels=labels,shadow=True,startangle=90)
	ax.axis('equal')
	if not os.path.exists(path('data/img')):
		os.mkdir(path('data/img'))
	plt.savefig(path('data/img','{time}_{table}_{column}_{top}.png'.format(time=time,table=table,column=column,top=top)))
	#plt.show()

def draw_table():
	"""
	画md表
	"""

def draw_md():
	"""
	按时间生成md报告
	"""
	month=date_delta(format='%Y%m')
	draw_pie(table='secwiki',column='domain',time=month,top=10)
	with codecs.open('secwiki_{month}.md'.format(month=month),'wb',encoding='utf-8') as f:
		f.write('## secwiki数据源Top10')
		f.write(os.linesep)
		f.write('![{month}_secwiki_domain_10](data/img/{month}_secwiki_domain_10.png)'.format(month=month))

def update_github():
	today=date_delta()
	command='git add . && git commit -m "{today} automated commit by 404notf0und" && git push origin master'.format(today=today)
	ret=os.system(command)

	if ret!=0:
		print("failed command %s" % command)

if __name__=="__main__":
	secwiki()
	draw_md()
	update_github()