import sys
import re

def Err_unk(term):
	print "Unknown unit - "+term
	sys.exit()

def error(query):
	print "Can't Handle - "+query
	sys.exit()

def Erralias(t):
	print "Not unique table/alias: "+t
	sys.exit()

def Err_join():
	print "Tables not included for columns specified in the condition"

def ErrTab(t):
	print "Invalid table name - "+t
	sys.exit()

def ErrCol(c):
	print "Invalid column name - "+c
	sys.exit()

def Err_morecols():
	print "Abmigous Columns / aggregated query without GROUP BY"
	sys.exit()

def Err_syn(query):
	print "Syntax error in the query. - "+query
	sys.exit()

def Err_dis(query):
	print "Not right syntax near distinct - "+query
	sys.exit()

def Err_amb(c):
	print "Ambigous column - "+c
	sys.exit()

def Err_cond(cond):
	print "Error in the condition - "+cond
	sys.exit()