from __future__ import division

import sys
import csv
import re
import sqlparse
import itertools
from error_handler import *
from Format import store,join_tables,show,display
from Evaluator import Handle_where,locate

funcs = ['max', 'min', 'sum', 'avg', 'distinct']

def is_aggr(cols,tabs,Map):

	excep = {}
	a_map = {}
	dist = 0
	exist = 0

	for col in cols.split(','):
		cex = 0
		c = col.strip()
		c = c.lower()

		if c=="*":
			a_map[c]='all'

		else:
			for f in funcs:
				if f in c:
					c = c.replace(f,'')
					c = c.replace('(','')
					c = c.replace(')','')

					index,key = locate(Map,tabs,c)
					cex = 1
					exist = 1
					if f=='distinct':
						dist+=1
					tup = (index,f)
					a_map[col]=tup

			index,key = locate(Map,tabs,c)
			if not cex:
				excep[c]=index

	if dist and len(cols.split(','))>1:
		Err_dis(cols)

	return exist,dist,a_map,excep

def out_dist(a_map,data):

	field = []
	for k in a_map.keys():
		ind = a_map[k][0]

	for row in data:
		field.append(row[ind])

	for k in a_map.keys():
		k = k.split('(')[1]
		k = k.split(')')[0]
		print k

	field = set(field)
	for f in field:
		print f

	sys.exit()

def calculate(field, func):

	if not field:
		return 'NULL'

	if func=='max':
		return max(field)
	elif func=='min':
		return min(field)
	else:
		tot = sum(field)
		if func=='sum':
			return tot
		else:
			return tot/len(field)


def Handle_aggr(data,cols,tabs,Map):

	exist,dist,a_map,excep = is_aggr(cols,tabs,Map)

	if exist:
		if dist:
			out_dist(a_map,data)

		names = []
		out = []

		for col in cols.split(','):
			field = []

			if col in excep.keys():
				result = data[0][excep[col]]
				names.append(col)
				out.append(result)

			else:
				if col=='*':
					line = []
					for t in tabs.split(','):
						#print t
						for k in Map.keys():
							#print "     "+k
							if t in k and re.match('[a-zA-Z].*[0-9]*\.\w',k):
								line.append((k,Map[k]))

					line = sorted(line)
					print line
					for l in line:
						names.append(l[0])
						out.append(int(data[0][l[1]]))
				else:
					ind = a_map[col][0]
					func = a_map[col][1]

					for row in data:
						field.append(int(row[ind]))

					result = calculate(field, func)

					names.append(col)
					out.append(result)

		display(names)

		for i in range(len(out)):

			if not i==len(out)-1:
				print str(out[i])+',',
			else:
				print out[i]

		sys.exit()
	else:
		return data

