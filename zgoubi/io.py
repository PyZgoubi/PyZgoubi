#!/usr/bin/env python

import numpy
import csv
import hashlib
import os
import struct

from exceptions import OldFormatError

# translate some of the column names for compatibility with old pyzgoubi
col_name_trans ={
"KEX":"IEX",
"Do-1":"D0",
"Yo":"Y0",
"To":"T0",
"Zo":"Z0",
"Po":"P0",
"So":"S0",
"to":"tof0",
"D-1":"D",
"Y":"Y",
"T":"T",
"Z":"Z",
"P":"P",
"S":"S",
"time":"tof",
"ENEKI":"KE",
"ENERG":"E",
"IT":"ID",
"IREP":"IREP",
"SORT":"SORT",
"M":"M",
"Q":"Q",
"G":"G",
"tau":"tau",
"unused":"unused",
"RET":"RET",
"DPR":"DPR",
"PS":"PS",
"BORO":"BORO",
"IPASS":"PASS",
"NOEL":"NOEL",
"KLEY":"element_type",
"LABEL1":"element_label1",
"LABEL2":"element_label2",
"LET":"LET",
"Y-DY":"Y",
}


# store some definitions, to speed loading, and to work around some issues
definition_lookup = {}
# from zgoubi svn 251
definition_lookup['7e0d6c789529cad60f97c7a9f3ff8894'] = {'file_mode': 'ascii', 'file_type': 'fai', 'names': ['IEX', 'D0', 'Y0', 'T0', 'Z0', 'P0', 'S0', 'tof0', 'D-1', 'Y', 'T', 'Z', 'P', 'S', 'tof', 'SXo', 'SYo', 'SZo', 'modSo', 'SX', 'SY', 'SZ', 'modS', 'KE', 'E', 'ID', 'IREP', 'SORT', 'M', 'Q', 'G', 'tau', 'unused', 'RET', 'DPR', 'PS', 'BORO', 'PASS', 'NOEL', 'element_type', 'element_label1', 'element_label2', 'LET'], 'signature': '7e0d6c789529cad60f97c7a9f3ff8894', 'units': ['int', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'MeV', 'MeV', 'int', 'int', 'cm', 'MeV/c2', 'C', 'float', 'float', 'float', 'float', 'float', 'float', 'kG.cm', 'int', 'int', 'string', 'string', 'string', 'string'], 'types': ['i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'a10', 'a8', 'a8', 'a1']}

definition_lookup['09173c37cdb73b2a6c7b1c2f12519f2e'] = {'header_length': 922, 'file_mode': 'binary', 'file_type': 'fai', 'record_length': 327, 'names': ['IEX', 'D0', 'Y0', 'T0', 'Z0', 'P0', 'S0', 'tof0', 'D-1', 'Y', 'T', 'Z', 'P', 'S', 'tof', 'SXo', 'SYo', 'SZo', 'modSo', 'SX', 'SY', 'SZ', 'modS', 'KE', 'E', 'ID', 'IREP', 'SORT', 'M', 'Q', 'G', 'tau', 'unused', 'RET', 'DPR', 'PS', 'BORO', 'PASS', 'NOEL', 'element_type', 'element_label1', 'element_label2', 'LET'], 'signature': '09173c37cdb73b2a6c7b1c2f12519f2e', 'units': ['int', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'MeV', 'MeV', 'int', 'int', 'cm', 'MeV/c2', 'C', 'float', 'float', 'float', 'float', 'float', 'float', 'kG.cm', 'int', 'int', 'string', 'string', 'string', 'string'], 'types': ['i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'a10', 'a8', 'a8', 'a1']}

definition_lookup['ea298b3ccc3f5b75bb672363221ec9da'] = {'file_mode': 'ascii', 'file_type': 'plt', 'names': ['IEX', 'D0', 'Y0', 'T0', 'Z0', 'P0', 'S0', 'tof0', 'D-1', 'Y', 'T', 'Z', 'P', 'S', 'tof', 'beta', 'DS', 'KART', 'ID', 'IREP', 'SORT', 'X', 'BX', 'BY', 'BZ', 'RET', 'DPR', 'PS', 'SXo', 'SYo', 'SZo', 'modSo', 'SX', 'SY', 'SZ', 'modS', 'EX', 'EY', 'EZ', 'BORO', 'PASS', 'NOEL', 'element_type', 'element_label1', 'element_label2', 'LET'], 'signature': 'ea298b3ccc3f5b75bb672363221ec9da', 'units': ['int', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'v/c', 'cm', 'int', 'int', 'int', 'cm', 'cm', 'kG', 'kG', 'kG', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'V/m', 'V/m', 'V/m', 'kG.cm', 'int', 'int', 'string', 'string', 'string', 'string'], 'types': ['i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'a10', 'a8', 'a8', 'a1']}

definition_lookup['98dfe80e482e210e6ed827aff0c70b53'] = {'header_length': 922, 'file_mode': 'binary', 'file_type': 'plt', 'record_length': 347, 'names': ['IEX', 'D0', 'Y0', 'T0', 'Z0', 'P0', 'S0', 'tof0', 'D-1', 'Y', 'T', 'Z', 'P', 'S', 'tof', 'beta', 'DS', 'KART', 'ID', 'IREP', 'SORT', 'X', 'BX', 'BY', 'BZ', 'RET', 'DPR', 'PS', 'SXo', 'SYo', 'SZo', 'modSo', 'SX', 'SY', 'SZ', 'modS', 'EX', 'EY', 'EZ', 'BORO', 'PASS', 'NOEL', 'element_type', 'element_label1', 'element_label2', 'LET'], 'signature': '98dfe80e482e210e6ed827aff0c70b53', 'units': ['int', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'v/c', 'cm', 'int', 'int', 'int', 'cm', 'cm', 'kG', 'kG', 'kG', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'V/m', 'V/m', 'V/m', 'kG.cm', 'int', 'int', 'string', 'string', 'string', 'string'], 'types': ['i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'a10', 'a8', 'a8', 'a1']}


def open_file_or_name(forn, mode="r"):
	"Pass either a filename or file handle like object. Returns a file like object"
	if hasattr(forn, 'readline'):
		return forn
	else:
		return open(forn, mode)



def fortran_record(fh):
	"Read 1 record from a fortran file"
	# length of each record is at start and end of record.
	# read length
	rec_len_r = fh.read(4)
	try:
		rec_len = struct.unpack("i", rec_len_r)[0]
	except struct.error:
		return None
	assert (rec_len < 1000), "zgoubi records should be short"
	# read record
	record = fh.read(rec_len)
	# read and check length
	rec_len_r2 = fh.read(4)
	assert (rec_len_r == rec_len_r2), "record should start and end with length"
	return record


def define_file(fname, allow_lookup=True):
	"Read header from a file and determine formating. Returns a dict that describes the file"
	fh = open_file_or_name(fname)
	fh.seek(0)

	first_bytes = fh.read(30)
	# zgoubi's ascii files start with '# '
	# the binary files start with an int that tells you the length of the next record
	
	if first_bytes[0:2] == "# ":
		file_mode = 'ascii'
	else:
		file_mode = 'binary'
	
	if "COORDINATES" in first_bytes:
		file_type = "fai"
	elif "TRAJECTORIES" in first_bytes:
		file_type = "plt"

	fh.seek(0)
	if file_mode == 'ascii':
		header = [fh.readline() for x in xrange(4)]
	else:
		header = [fortran_record(fh) for x in xrange(4)]
	
	if header[2].startswith("..."):
		raise OldFormatError, "This is an old format that does not define column headings"
	
	signature = file_mode + file_type + header[1] + header[2] + header[3]
	signature = hashlib.md5(signature).hexdigest()	

	header_length = sum([len(h) for h in header])

	if allow_lookup:
		try:
			return definition_lookup[signature]
		except KeyError:
			print "new format, analysing"

	if file_mode == 'binary':
		header_length += 4*8 # extra bytes from record lengths
		#file_length = os.path.getsize(fname)
		record_length = len(fortran_record(fh)) +8

		#file_length = len(whole_file)
		#print "file_length", file_length
		#print "header_length",header_length
		#print "record_length", record_length
		

	
	col_names = header[2].strip().replace(" ", "").split(',')
	col_types = header[3].strip().replace(" ", "").split(',')
	
	dupes = list(set ([x  for x in col_names if (col_names.count(x) > 1)]))
	if dupes:
		raise ValueError, "Duplicate columns in:"+ fname +"\n"+" ".join(dupes)
	
	names = []
	types = []
	units = []

	for rname, rtype in zip(col_names, col_types):
		#print "#", rname,"#" , rtype,"#"
		ntype = "f8"
		nunit = rtype
		if rtype == "int":
			ntype = "i4"
		if rtype == "string":
			if rname == "KLEY":
				ntype = "a10"
			if rname == "LABEL1":
				ntype = "a8"
			if rname == "LABEL2":
				ntype = "a8"
			if rname == "LET":
				ntype = "a1"

		nname = col_name_trans.get(rname, rname)

		names.append(nname)
		types.append(ntype)
		units.append(nunit)
	
	
	definition =  {'names':names, 'types':types, 'units':units, 'file_mode':file_mode, 'file_type':file_type, 'signature':signature}
	if file_mode == 'binary':
		definition['header_length'] = header_length
		definition['record_length'] = record_length

	definition_lookup[signature] = definition
	return definition



def listreplace(l, old, new):
	"Replace all occurrences of 'old' with 'new' in 'l'"
	return [x if x != old else new for x in l]
	
def read_file(fname):
	"Read a zgoubi output file. Return a numpy array with named column headers. The format is automatically worked out from the header information."
	file_def = define_file(fname)

	data_type = zip(file_def['names'], file_def['types'])
	fh = open_file_or_name(fname)
	fh.seek(0)

	
	if file_def["file_mode"] == "ascii":
		header = [fh.readline().strip() for x in xrange(4)]
		file_data = [] 
		# acsii files a space separated, but the quote around the stings are similar to in a csv file
		# so use csv module to split the line into elements
		#for row in csv.reader(fh, delimiter=" ", quotechar="'"):
		for n, row in enumerate(csv.reader(fh, delimiter=" ", quotechar="'")):
			#if n == 2: break
			# there are sometimes more that 1 space between fields, csv interprets this as empty fields, so need to remove them
			#print row
			vals = [e for e in row if e ]
			file_data.append(tuple(vals))
		# use the data_type info to set the fields right, and convert to numpy array
		file_data2 = numpy.array(file_data, dtype= numpy.dtype(data_type))

	if file_def["file_mode"] == "binary":
		rec_len = file_def["record_length"]
		head_len = file_def["header_length"]
		fh.seek(head_len)
		
		types = file_def['types']
		types = listreplace(types, 'f8', 'd')
		types = listreplace(types, 'i4', 'i')
		types = listreplace(types, 'a8', '8s')
		types = listreplace(types, 'a10', '10s')
		types = listreplace(types, 'a1', 'c')
		
		data_format = "="+"".join(types)

		file_size = os.path.getsize(fname)
		num_records = (file_size - head_len) / rec_len
	
		file_data2 = numpy.zeros(num_records, dtype= numpy.dtype(data_type))
		
		for n in xrange(num_records):
			rec = fh.read(rec_len)[4:-4]
			if rec == "": break
			file_data2[n] = rec

	return file_data2


def store_def_all():
	"Run define file on set of files, and output a code block that can be put into the to of this file to save rerunning define_file at program runtime"
	af = define_file("ascii.fai", allow_lookup=False)
	ap = define_file("ascii.plt", allow_lookup=False)
	bf = define_file("binary.fai", allow_lookup=False)
	bp = define_file("binary.plt", allow_lookup=False)

	print
	print "definition_lookup['%s'] = % s" % ( af['signature'], af)
	print
	print "definition_lookup['%s'] = % s" % ( bf['signature'], bf)
	print
	print "definition_lookup['%s'] = % s" % ( ap['signature'], ap)
	print
	print "definition_lookup['%s'] = % s" % ( bp['signature'], bp)
	print