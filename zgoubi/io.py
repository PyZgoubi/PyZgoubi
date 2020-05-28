#!/usr/bin/env python
"Module to handle reading and writing of Zgoubi files"

import numpy
import csv
import hashlib
import os
import struct
import sys

from zgoubi.exceptions import OldFormatError, BadFormatError, EmptyFileError
from zgoubi.core import zlog
from zgoubi.common import open_file_or_name

# translate some of the column names for compatibility with old pyzgoubi
col_name_trans = {
"KEX":"IEX",
"Do-1":"D0-1",
"Yo":"Y0",
"To":"T0",
"Zo":"Z0",
"Po":"P0",
"So":"S0",
"to":"tof0",
"D-1":"D-1",
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

# FIXME checksum changed to include record length, so these need updating
# store some definitions, to speed loading, and to work around some issues
definition_lookup = {}
# from zgoubi svn 255 (not changed between 251 and 255)
definition_lookup['e64fc05dd4b7f39045b6875d84b629f2'] = {'file_mode': 'ascii', 'file_type': 'fai', 'names': ['IEX', 'D0-1', 'Y0', 'T0', 'Z0', 'P0', 'S0', 'tof0', 'D-1', 'Y', 'T', 'Z', 'P', 'S', 'tof', 'SXo', 'SYo', 'SZo', 'modSo', 'SX', 'SY', 'SZ', 'modS', 'KE', 'E', 'ID', 'IREP', 'SORT', 'M', 'Q', 'G', 'tau', 'unused', 'RET', 'DPR', 'PS', 'BORO', 'PASS', 'NOEL', 'element_type', 'element_label1', 'element_label2', 'LET'], 'signature': 'e64fc05dd4b7f39045b6875d84b629f2', 'units': ['int', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'MeV', 'MeV', 'int', 'int', 'cm', 'MeV/c2', 'C', 'float', 'float', 'float', 'float', 'float', 'float', 'kG.cm', 'int', 'int', 'string', 'string', 'string', 'string'], 'types': ['i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'a10', 'a8', 'a8', 'a1']}

definition_lookup['214810873529de36ca1a9262cccf409a'] = {'header_length': 922, 'file_mode': 'binary', 'file_type': 'fai', 'record_length': 327, 'names': ['IEX', 'D0-1', 'Y0', 'T0', 'Z0', 'P0', 'S0', 'tof0', 'D-1', 'Y', 'T', 'Z', 'P', 'S', 'tof', 'SXo', 'SYo', 'SZo', 'modSo', 'SX', 'SY', 'SZ', 'modS', 'KE', 'E', 'ID', 'IREP', 'SORT', 'M', 'Q', 'G', 'tau', 'unused', 'RET', 'DPR', 'PS', 'BORO', 'PASS', 'NOEL', 'element_type', 'element_label1', 'element_label2', 'LET'], 'signature': '214810873529de36ca1a9262cccf409a', 'units': ['int', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'MeV', 'MeV', 'int', 'int', 'cm', 'MeV/c2', 'C', 'float', 'float', 'float', 'float', 'float', 'float', 'kG.cm', 'int', 'int', 'string', 'string', 'string', 'string'], 'types': ['i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'a10', 'a8', 'a8', 'a1']}

definition_lookup['cf6325603a7bbd57727637003208af60'] = {'file_mode': 'ascii', 'file_type': 'plt', 'names': ['IEX', 'D0-1', 'Y0', 'T0', 'Z0', 'P0', 'S0', 'tof0', 'D-1', 'Y', 'T', 'Z', 'P', 'S', 'tof', 'beta', 'DS', 'KART', 'ID', 'IREP', 'SORT', 'X', 'BX', 'BY', 'BZ', 'RET', 'DPR', 'PS', 'SXo', 'SYo', 'SZo', 'modSo', 'SX', 'SY', 'SZ', 'modS', 'EX', 'EY', 'EZ', 'BORO', 'PASS', 'NOEL', 'element_type', 'element_label1', 'element_label2', 'LET'], 'signature': 'cf6325603a7bbd57727637003208af60', 'units': ['int', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'v/c', 'cm', 'int', 'int', 'int', 'cm', 'cm', 'kG', 'kG', 'kG', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'V/m', 'V/m', 'V/m', 'kG.cm', 'int', 'int', 'string', 'string', 'string', 'string'], 'types': ['i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'a10', 'a8', 'a8', 'a1']}

definition_lookup['77b763ba233a2cd85ab8e0b77f5db05f'] = {'header_length': 922, 'file_mode': 'binary', 'file_type': 'plt', 'record_length': 347, 'names': ['IEX', 'D0-1', 'Y0', 'T0', 'Z0', 'P0', 'S0', 'tof0', 'D-1', 'Y', 'T', 'Z', 'P', 'S', 'tof', 'beta', 'DS', 'KART', 'ID', 'IREP', 'SORT', 'X', 'BX', 'BY', 'BZ', 'RET', 'DPR', 'PS', 'SXo', 'SYo', 'SZo', 'modSo', 'SX', 'SY', 'SZ', 'modS', 'EX', 'EY', 'EZ', 'BORO', 'PASS', 'NOEL', 'element_type', 'element_label1', 'element_label2', 'LET'], 'signature': '77b763ba233a2cd85ab8e0b77f5db05f', 'units': ['int', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'float', 'cm', 'mrd', 'cm', 'mrd', 'cm', 'mu_s', 'v/c', 'cm', 'int', 'int', 'int', 'cm', 'cm', 'kG', 'kG', 'kG', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'float', 'V/m', 'V/m', 'V/m', 'kG.cm', 'int', 'int', 'string', 'string', 'string', 'string'], 'types': ['i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'i4', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'i4', 'i4', 'a10', 'a8', 'a8', 'a1']}


def read_fortran_record(fh):
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

def write_fortran_record(fh, record):
	"Write a record, adds record length to start and end"
	rec_len = len(record)
	rec_len_r = struct.pack("i", rec_len)
	fh.write(rec_len_r+record+rec_len_r)
	#fh.write(record)
	#fh.write(rec_len_r)



def define_file(fname, allow_lookup=False):
	"Read header from a file and determine formating. Returns a dict that describes the file"
	fh = open_file_or_name(fname)
	fh.seek(0)
	file_size = os.path.getsize(fh.name)

	first_bytes = fh.read(30)
	# zgoubi's ascii files start with '# '
	# the binary files start with an int that tells you the length of the next record
	
	if first_bytes[0:2] == "# ":
		file_mode = 'ascii'
	else:
		file_mode = 'binary'
		if sys.platform == "win32":
			# reopen as binary
			fh = open_file_or_name(fname, mode="rb")
			fh.seek(0)
			first_bytes = fh.read(30)
			
	
	if "COORDINATES" in first_bytes:
		file_type = "fai"
	elif "TRAJECTORIES" in first_bytes:
		file_type = "plt"
	elif "SPIN" in first_bytes:
		file_type = "spn"

	fh.seek(0)
	if file_mode == 'ascii':
		header = [fh.readline() for x in xrange(4)]
	else:
		header = [read_fortran_record(fh) for x in xrange(4)]
	
	if header[2].startswith("..."):
		raise OldFormatError, "This is an old format that does not define column headings"

	header_length = sum([len(h) for h in header])
	if file_size <= header_length+8*4:
		raise EmptyFileError

	record_len = 0
	if file_mode == 'binary':
		header_length += 4*8 # extra bytes from record lengths
		fh.seek(header_length)
		record_len = struct.unpack("i", fh.read(4))[0]
		print "record_len", record_len

	
	signature = file_mode + file_type + header[2] + header[3] + str(record_len)
	signature = hashlib.md5(signature).hexdigest()	

	if allow_lookup:
		try:
			return definition_lookup[signature]
		except KeyError:
			zlog.debug("new format, analysing. sig:%s" % signature)

	if file_mode == 'binary':
		#file_length = os.path.getsize(fname)
		fh.seek(header_length)
		record_length = len(read_fortran_record(fh)) +8

		#file_length = len(whole_file)
		#print "file_length", file_length
		#print "header_length",header_length
		#print "record_length", record_length
		

	col_names = header[2].strip().strip('#').replace(" ", "").split(',')
	col_types = header[3].strip().strip('#').replace(" ", "").split(',')
	
	if col_names[-1]=='S':
		col_names[-1] = 'SL' #CDK temporary fix to avoid duplicaiting 'S' in Zgoubi rev 955.

	dupes = list(set ([x  for x in col_names if (col_names.count(x) > 1)]))
	if dupes:
		raise ValueError, "Duplicate columns in:" + str(fname) + "\n" + " ".join(dupes)

	if len(col_names) != len(col_types):
		raise ValueError, "Length of col_names (%s) not equal to length of col_types (%s)" % (len(col_names), len(col_types))

	names = []
	types = []
	units = []
	byte_count = 8 # count how long the field lengths add up to

	for rname, rtype in zip(col_names, col_types):
		#print "#", rname,"#" , rtype,"#"
		ntype = "f8"
		nunit = rtype
		nbytes = 8
		if rtype == "int":
			ntype = "i4"
			nbytes = 4
		elif rtype == "string":
			if rname == "KLEY":
				ntype = "a10"
				nbytes = 10
			if rname == "LABEL1":
				ntype = "a10"
				nbytes = 10
			if rname == "LABEL2":
				ntype = "a10"
				nbytes = 10
			if rname == "LET":
				ntype = "a1"
				nbytes = 1
		byte_count += nbytes

		nname = col_name_trans.get(rname, rname)

		names.append(nname)
		types.append(ntype)
		units.append(nunit)

	if file_mode == 'binary' and byte_count == record_length - 20:
		# After Zgoubi 6, label length increased from 10 to 20
		types[names.index("element_label1")] = "a20"
		types[names.index("element_label2")] = "a20"
		byte_count += 20

	if file_mode == 'binary' and byte_count != record_length:
		raise ValueError, "byte_count from header types does not match record_length in file"

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
	if file_def["file_mode"] == "binary" and sys.platform == "win32":
		fh = open_file_or_name(fname, mode="rb")
	else:
		fh = open_file_or_name(fname)
	fh.seek(0)

	
	if file_def["file_mode"] == "ascii":
		dummy = [fh.readline().strip() for dummy in xrange(4)]
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
		try:
			file_data2 = numpy.array(file_data, dtype= numpy.dtype(data_type))
		except ValueError:
			# FIXME
			# sometimes zgoubi outputs floats as
			# 1.5741247399232311-101 instead of 1.5741247399232311E-101
			# try to catch as repair these
			# first, try again row by row, and repair on broken rows
			# should probably try to fix in zgoubi
			file_data2 = numpy.zeros(len(file_data), dtype= numpy.dtype(data_type))
			for n, row in enumerate(file_data):
				try:
					file_data2[n] = numpy.array(row, dtype= numpy.dtype(data_type))
				except ValueError:
					new_row = []
					for s in row:
						if len(s)>5 and (s[1]=='.'or s[2]=='.') and (s[-4] == '-' or s[-4] == '+'):
							ns = s[:-4] + 'E' + s[-4:]
							zlog.debug("Replaced %s with %s (%s)"%(s, ns, float(ns)))
							s = ns
							
						new_row.append(s)

					new_row = new_row[:len(data_type)]
					file_data2[n] = numpy.array(tuple(new_row), dtype= numpy.dtype(data_type))

	if file_def["file_mode"] == "binary":
		rec_len = file_def["record_length"]
		head_len = file_def["header_length"]
		fh.seek(head_len)
		
		#types = file_def['types']
		#types = listreplace(types, 'f8', 'd')
		#types = listreplace(types, 'i4', 'i')
		#types = listreplace(types, 'a8', '8s')
		#types = listreplace(types, 'a10', '10s')
		#types = listreplace(types, 'a1', 'c')
		#data_format = "="+"".join(types)

		file_size = os.path.getsize(fname)
		num_records = (file_size - head_len) / rec_len
		if num_records == 0:
			raise EmptyFileError
	
		file_data2 = numpy.zeros(num_records, dtype= numpy.dtype(data_type))
		
		for n in xrange(num_records):
			full_rec = fh.read(rec_len)
			#FIXME this check wastes some time in a bit of code that should be fast. maybe should only be on if debug is enabled
			if not ((rec_len-8) == struct.unpack("i", full_rec[:4])[0] == struct.unpack("i", full_rec[-4:])[0]):
				zlog.error("Record length not correct: header says %s but file contains %s"%(rec_len-8, struct.unpack("i", full_rec[:4])))
				raise BadFormatError("Can't read records")

			rec = full_rec[4:-4]
			if rec == "": break
			file_data2[n] = numpy.frombuffer(rec, dtype=data_type)

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
