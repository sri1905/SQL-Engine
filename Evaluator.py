from __future__ import division

import sys
import csv
import re
import sqlparse
import itertools
from error_handler import *
#from Format import store,join_tables

Neql = '!='
neql = '<>'
lte = '<='
gte = '>='
lt = '<'
gt = '>'
eql = '='

operators = [Neql, neql, lte, gte, eql, lt, gt]

def evaluate(opr, lhs, rhs):

	lhs = int(lhs)
	rhs = int(rhs)

	if opr==eql:
		return lhs==rhs
	elif opr==Neql or opr==neql:
		return lhs!=rhs
	elif opr==lt:
		return lhs<rhs
	elif opr==gt:
		return lhs>rhs
	elif opr==lte:
		return lhs<=rhs
	elif opr==gte:
		return lhs>=rhs

def locate(Map, tabs, term):

	keys =  Map.keys()

	if re.match('[a-zA-Z].*[0-9]*\.\w',term):
		if term in keys:
			return Map[term],term
		else:
			ErrCol(term)

	if not term.isalnum():
		Err_unk(term)

	if term.isalpha() and term.isdigit():
		Err_unk(term)
	
	key = ''
	tc = ''
	cnt = 0
	index = -1
	t_list = tabs.split(',')
	for t in t_list:
		t=t.strip()
		tc = t+'.'+term
		if tc in keys:
			key = tc
			cnt+=1
			index = Map[tc]

	if cnt==0:
		ErrCol(term)
	elif cnt==1:
		return index,key
	elif cnt==2:
		Err_amb(term)
	else:
		Err_syn(term)

def simple_cond(tabs,col_map,all_rows,all_cols,cond):

	#print col_map

	fl = 0
	conditioned = []
	dup = -1
	no_dup = 0
	for opr in operators:
		if opr in cond:
			fl=1
			#print opr
			parts = cond.split(opr)
			lhs = parts[0].strip()
			rhs = parts[1].strip()

			#LHS
			l_ind,key = locate(col_map,tabs,lhs)
			if type(l_ind)==tuple:
				dup = l_ind[0]
				l_ind = l_ind[0]

			#RHS
			temp = ''
			if '-' == rhs[0] or rhs.isdigit():

				if rhs.isdigit():
					rnum = rhs

				elif rhs[1:].isdigit():
					rnum = int(rhs[1:])
					rnum*=-1

				else:
					Err_unk(rhs)

				for row in all_rows:
					if evaluate(opr, row[l_ind], rnum):
						if row not in conditioned:
							conditioned.append(row)

				return conditioned

			else:
				r_ind,key = locate(col_map,tabs,rhs)
				if type(r_ind)==tuple:
					dup = r_ind[0]
					r_ind = r_ind[0]
					if re.match('\*',all_cols):
						no_dup = 1

				for row in all_rows:
					if evaluate(opr,row[l_ind],row[r_ind]):
						if row not in conditioned:
							temp = []
							if no_dup:
								for i in range(len(row)):
									if not dup==i:
										temp.append(row[i])
							else:
								temp = row
							conditioned.append(temp)
				return conditioned
	if fl==0:
		Err_cond(cond)


def complex_cond(all_tabs,col_map,all_rows,all_cols,cond):
	# 0 -> OR 
	AND = 1
	if 'and' in cond:
		dlim = 'and'
	else:
		AND = 0
		dlim = 'or'

	one = cond.split(dlim)[0]
	two = cond.split(dlim)[1]

	if AND:
		part1 = simple_cond(all_tabs,col_map,all_rows,all_cols,one)
		conditioned = simple_cond(all_tabs,col_map,part1,all_cols,two)
	else:
		part1 = simple_cond(all_tabs,col_map,all_rows,all_cols,one)
		part2 = simple_cond(all_tabs,col_map,all_rows,all_cols,two)
		conditioned = part1+part2

	return conditioned

def Handle_where(all_tabs,col_map,all_rows,all_cols,cond):

	keys = col_map.keys()
	whole_cond = cond
	cond = cond.lower()
	cond = cond.replace('where', '')
	#print cond

	if 'and' in cond or 'or' in cond:
		conditioned = complex_cond(all_tabs,col_map,all_rows,all_cols,cond)
	else:
		conditioned = simple_cond(all_tabs,col_map,all_rows,all_cols,cond)

	return conditioned