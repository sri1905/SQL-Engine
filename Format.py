from __future__ import division

import sys
import csv
import re
import sqlparse
import itertools
import collections
from error_handler import *
from Evaluator import Handle_where,locate

def display(cols):

	length = len(cols)
	for i in range(len(cols)):
		if i == length-1:
			print cols[i]
		else:
			print cols[i]+',',

def store():

	meta = open('metadata.txt', 'r')
	data = meta.read()
	meta.close()

	begin = '<begin_table>'
	end = '<end_table>'

	Tables = []
	Columns = []
	cols = []
	Map = collections.OrderedDict()

	table_name=0
	t = 0
	c=0

	for line in data.split():
		line = line.lower()
		if line==begin:
			table_name=1
			continue

		if line==end:
			Columns.append(cols)
			cols = []
			continue

		if table_name:
			tag = line+"."
			Tables.append(line)
			table_name=0
			continue

		cols.append(line)

	for t in range(len(Tables)):
		Map[Tables[t]] = t
		for c in range(len(Columns[t])):
			tag = Tables[t]+'.'+Columns[t][c]
			Map[tag] = c

	data = []
	t = -1

	for t_name in Tables:

		row = []
		table = open(t_name+'.csv', 'rb')
		info = csv.reader(table)
		fl = 0
		for l in info:
			if not fl:
				fl=1
				cnt = len(l)
		table.close()

		for i in range(cnt):
			row.append([])

		table = open(t_name+'.csv', 'rb')
		info = csv.reader(table)

		for parts in info:
			for i in range(cnt):
				row[i].append(parts[i])

		data.append(row)
		table.close()

		#print "Table -: "+t_name
		#print row

	return data,Map

def process_colname(all_col,Map,tabs):
	names = ''
	all_col = all_col.strip()
	all_col = all_col.strip('\n')	

	for c in all_col:
		names = names.replace(',,',',')

		if c == '*':
			for t in tabs.split(','):
				for m in Map.keys():
					if '.' in m and t in m:
						names+=m+','
		else:
			names+=c

	if names[-1]==',':
		names = names[:-1]

	return names.lower()

def join_tables(query,tokens,data,Map):

	all_col = ''
	all_tab = ''
	cond = ''

	syntax = 0
	for i in range(len(tokens)):
		if i==1:
			all_col=tokens[i]
		elif i==3:
			all_tab = tokens[i]
		elif i==4:
			unit = tokens[i]
			where = tokens[i].split()[0]
			if 'where'==where:
				if unit[-1]==';':
					cond = unit[:-1]
				else:
					cond = unit

	tabs = all_tab.lower()
	cols = all_col.lower()

	all_col = process_colname(all_col,Map,tabs)

	# JOIN TABLES
	
	keys = Map.keys()

	TAB_MAP = collections.OrderedDict()
	for m in keys:
		if not '.' in m:
			TAB_MAP[m] = Map[m]

	length = 0
	duplicate = []
	ALL_ROWS = []
	c_map = collections.OrderedDict()
	cnt = 0

	temp = []
	for t in tabs.split(','):
		t = t.strip()
		if t not in TAB_MAP.keys():
			ErrTab(t)
		if t in temp:
			Erralias(t)
		temp.append(t)

	for t in tabs.split(','):
		TAB_ROWS = []
		COLS = []
		for k in keys:
			if re.match(t+'\..*',k):
				f = data[Map[t]][Map[k]]
				if f in duplicate:
					c_map[k]=(cnt,'dup')
				else:
					c_map[k]=cnt
				cnt+=1

				if len(f) > length:
					length = len(f)
				duplicate.append(f)
				COLS.append(f)

		# MAKE ROWS
		for i in range(length):
			ROW = [] 
			for C in COLS:
				ROW.append(C[i])
			#print ROW
			TAB_ROWS.append(ROW)

		ALL_ROWS.append(TAB_ROWS)

	# JOINING
	#print C_ORDER
	joined = []
	for e in itertools.product(*ALL_ROWS):
		joined.append(e)

	PRODUCT = []
	for tup in joined:
		row=[]
		for t in tup:
			if type(t) is list:

				for ele in t:
					row.append(ele)

		PRODUCT.append(row)

	'''
	for p in PRODUCT:
		print p
	'''
	
	return c_map,PRODUCT,all_col,all_tab,cond

def show(ROWS, col_map, all_tabs, all_cols):

	#print col_map

	order = []
	for col in all_cols.split(','):
		INPUT = col.strip()
		col = INPUT.lower()
		index,key = locate(col_map, all_tabs, col)
		order.append(key)

	display(order)

	if not len(ROWS):
		for i in range(len(order)):
			if not i==len(order)-1:
				print "NULL,",
			else:
				print "NULL"

	for row in ROWS:
		for i in range(len(order)):
			val = col_map[order[i]]
			if type(val)==tuple:
				val = val[0]
			if not i==len(order)-1:
				print row[val]+',',
			else:
				print row[val]
	return