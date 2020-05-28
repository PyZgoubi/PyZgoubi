#!/usr/bib/env python
#import io2 as io

from zgoubi import io

#io.store_def_all()

for fname in ["ascii.fai", "ascii.plt", "binary.fai", "binary.plt"]:
	print "Reading", fname
	try:
		af = io.read_file(fname)
		#print af
		print af.shape
		print af[0]
	except IOError:
		print "IOError reading", fname




import timeit

#print timeit.timeit('io.define_file("ascii.fai")', setup="import io2 as io", number=10)
#print timeit.timeit('io.define_file("ascii.plt")', setup="import io2 as io", number=10)
#print timeit.timeit('io.define_file("ascii.fai", allow_lookup=False)', setup="import io2 as io", number=100)

#print timeit.timeit('io.read_file("ascii.fai")', setup="import io2 as io", number=100)
#print timeit.timeit('io.read_file("binary.fai")', setup="import io2 as io", number=100)

