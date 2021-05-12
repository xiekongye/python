#! /usr/bin/env python 
#encoding=utf-8
import mylib
from sys import argv
from mylib import myargv

if __name__ == '__main__':
	# myargv = myargv(argv) #命令行用法
	myargv = myargv(['-v','user.ibd'])
	if myargv.parse_cmdline() == 0:
		pass
	else:
		mylib.get_innodb_page_type(myargv)
