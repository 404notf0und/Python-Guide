# Python代码规范 by 404notfound
通过不断学习和模仿优秀项目的代码，提升编码能力和风格

## Python编码风格
- 代码注释
- 异常处理

## Python常用语法
- 编码
	- str(unicode) vs bytes(gbk,utf-8,gb2312) unicode是转码枢纽
- 迭代器
	- next() 小心越界
- 生成器
	- yield 函数生成器
- 装饰器的使用
- collections
	- OrderedDict有序字典
- SQLite3增删改查
	- replace vs update 
	- insert or ignore into
	- execute vs executemany
- 时间日期操作datetime
- 目录操作os.path
- glob查找符合特定规则的文件名
- beautifulsoup网页解析库
	- .strings .stripped_strings(generator)
- re正则匹配库
- requests HTTP请求库
	- 获取重定向url
- shutil文件操作模块，是对os的补充

## Python实现功能
- 全自动化：爬取、分析作图、生成报告、上传github

## 小坑
- requests
  - content(byte) vs text(string)
  - 读写文件的对象需和文件打开模式保持一致：byte和string 对应'wb'和'w'

## Bugs
1. sqlite3.ProgrammingError: Incorrect number of bindings supplied. The current statement uses 0, and there are 2 supplied
	- 参数没绑定好，检查sql语句、参数值、参数类型
2. 使用迭代器next()时，RuntimeError: generator raised StopIteration
	- 多次next()导致数据越界

## 小技巧
- str() vs repr()
- codecs语言编码转换
- format字符串格式化函数

## Github灵活使用
- commiter vs author
	- git config --global user.name "xx"
	- git config --global user.email "xx#gmail.com"
	- git commit --author "xx xx#gmail.com"
	
