from __future__ import division

import sys
import csv
import re
import sqlparse
import itertools
from error_handler import *
from Format import store,join_tables,show
from Evaluator import Handle_where,locate
from Aggr import Handle_aggr

def Break(query):
	tokens = []

	res = sqlparse.parse(query) #assuming only one command
	parsed = res[0]

	for t in parsed.tokens:
		#tok = str(t).replace(" ", "")
		if re.match('.*\S.*',str(t)):
			tokens.append(str(t))

	return tokens

def chk(query):

	q = query.split(';')
	one = q[0].strip()
	if len(q)>1:
		two = q[1].strip()
		if len(two):
			error(query)

if __name__=="__main__":

	while 1:
		query = raw_input("\n> ")
		#query = sys.argv[1]

		chk(query)

		tokens = Break(query)

		if len(tokens) < 4:
			Err_syn(query)

		data,Map = store()
		COL_MAP,JOINT,all_cols,all_tabs,cond = join_tables(query,tokens,data,Map)

		all_cols = all_cols.lower()
		all_tabs = all_tabs.lower()
		cond = cond.lower()

		if cond:
			conditioned = Handle_where(all_tabs,COL_MAP,JOINT,all_cols,cond)
			processed = Handle_aggr(conditioned,all_cols,all_tabs,COL_MAP)
			show(processed, COL_MAP, all_tabs, all_cols)
		else:
			processed = Handle_aggr(JOINT,all_cols,all_tabs,COL_MAP)
			show(processed, COL_MAP, all_tabs, all_cols)

	sys.exit()
