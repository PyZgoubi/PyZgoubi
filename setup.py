#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup 
import sys
import os
import shutil
import errno
from glob import glob

MAIN_VERSION = '0.6.0'

if ("install" in sys.argv) and not ( "--help" in sys.argv):
	# check that we have write access to zgoubi/version.py
	try:
		f = open("zgoubi/version.py","w")
		f.close()
		f =open("install.log","w")
		f.close()
		f =open("build/lib/zgoubi/version.py","w")
		f.close()
		os.remove("build/lib/zgoubi/version.py")
	except IOError, exc:
		if exc.errno == errno.EACCES:
			print "ERROR: Permission denied updating zgoubi/version.py, build and/or install.log.\nIf they are owned by root, due to previously running install as root please remove them (eg. sudo ./setup.py clean --all ; sudo rm install.log zgoubi/version.py)."
			exit(1)

	if (os.path.exists(".bzr") and
		os.system("bzr version-info --format=python > zgoubi/version.py") == 0 and
		"sdist" not in sys.argv):
		# run from a bzr repo, can use version info
		print "updated zgoubi/version.py"
		vfile = open("zgoubi/version.py","a")
	else:
		vfile = open("zgoubi/version.py","w")
		vfile.write("#!/usr/bin/env python\n")
	vfile.write("MAIN_VERSION = '%s'\n"%MAIN_VERSION)
	vfile.close()

	# generate definitions
	print "generating definitions "
	from zgoubi import makedefs
	shutil.copyfile(os.path.join("defs","static_defs.py"), os.path.join("zgoubi","static_defs.py"))

	makedefs.make_element_classes([os.path.join("defs","simple_elements.defs")],os.path.join("zgoubi","simple_defs.py"))




setup(name='pyzgoubi',
	version=MAIN_VERSION,
	packages=['zgoubi'],
	scripts=['pyzgoubi'],
	#package_data={'zgoubi': ['defs/*.py', 'defs/*.defs']},
	data_files=[
	            #('share/pyzgoubi/definitions',glob('defs/*')),
	            ('share/pyzgoubi/examples',glob('examples/*')),
	            ('share/pyzgoubi/test',glob('tests/*.py')),
	          #  ('share/pyzgoubi/doc', glob('doc'))
	            ],
	author="Sam Tygier",
	author_email="sam.tygier@hep.manchester.ac.uk",
	url="http://sourceforge.net/projects/pyzgoubi/",
	license="GNU GENERAL PUBLIC LICENSE"
	)


if ("install" in sys.argv) and not ( "--help" in sys.argv):
	#find the log
	try:
		logfile = [x for x in sys.argv if x.startswith('--record')][-1]
		#strip away quotes, and expand path
		logfile = logfile.split('=')[-1].strip('"\'')
		logfile = os.path.expanduser(logfile)
	except IndexError:
		logfile = "install.log"

	try:
		for line in open(logfile):
			line = line.strip()
			if line.endswith("bin/pyzgoubi"):
				bin_path = os.path.dirname(line)
			if line.endswith("Scripts\pyzgoubi"):
				bin_path = line.rpartition('\\')[0]
			if line.endswith("zgoubi/__init__.py"):
				lib_path = os.path.normpath(os.path.join(os.path.dirname(line),".."))
			if line.endswith("zgoubi\__init__.py"):
				lib_path = line.rpartition('\\')[0].rpartition('\\')[0]
	except IOError:
		print "Could not see install log, install may have failed."
		print "Can't give help with setting up path"
		sys.exit(1)
		
	try:
		if sys.platform == "win32":
			print "Add the following to your PATH variable in user Environment Variables control panel"
			#print "export PYTHONPATH=$PYTHONPATH:%s"%lib_path
			print bin_path
			bat_file = open(os.path.join( bin_path, "pyzgoubi.bat"), "w")
			bat_file.write("set PYTHONPATH=%%PYTHONPATH%%;%s\n"%lib_path)
			bat_file.write("python %s\\pyzgoubi %%*\n"%bin_path)
			bat_file.close()
		else:
			print "\nyou may need to add the following to your .bashrc"
			print "export PYTHONPATH=%s:$PYTHONPATH"%lib_path
			print "export PATH=%s:$PATH"%bin_path
	except NameError:
		print "Could not find all paths in logfile"


