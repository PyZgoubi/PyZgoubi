#!/usr/bin/env python3
from setuptools import setup 
import sys
import os
import shutil
import errno
from glob import glob

MAIN_VERSION = '0.8.0a2'

with open("README", "r", encoding="utf-8") as fh:
    long_description = fh.read()

if not ( "--help" in sys.argv):
	if ("install" in sys.argv) or ("sdist" in sys.argv) or ("bdist_wheel" in sys.argv):
		# check that we have write access to zgoubi/version.py
		try:
			f = open("zgoubi/version.py","w")
			f.close()
			f =open("install.log","w")
			f.close()
			f =open("build/lib/zgoubi/version.py","w")
			f.close()
			os.remove("build/lib/zgoubi/version.py")
		except IOError as exc:
			if exc.errno == errno.EACCES:
				print("ERROR: Permission denied updating zgoubi/version.py, build and/or install.log.\nIf they are owned by root, due to previously running install as root please remove them (eg. sudo ./setup.py clean --all ; sudo rm install.log zgoubi/version.py).")
				exit(1)


		vfile = open("zgoubi/version.py","w")
		vfile.write("#!/usr/bin/env python\n")
		vfile.write("MAIN_VERSION = '%s'\n"%MAIN_VERSION)
		vfile.close()


setup(name='pyzgoubi',
	version=MAIN_VERSION,
	packages=['zgoubi'],
	scripts=['pyzgoubi'],
	data_files=[
	            ('share/pyzgoubi/examples',glob('examples/*')),
	            ('share/pyzgoubi/test',glob('tests/*.py')),
	          #  ('share/pyzgoubi/doc', glob('doc'))
	            ],
	author="Sam Tygier",
	author_email="sam.tygier@manchester.ac.uk",
	url="http://sourceforge.net/projects/pyzgoubi/",
	license="GNU GENERAL PUBLIC LICENSE",
	description="PyZgoubi is an interface to the Zgoubi particle tracker written in python.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	classifiers=["Development Status :: 5 - Production/Stable",
	             "Intended Audience :: Science/Research",
				 "Topic :: Scientific/Engineering :: Physics",
				 "License :: OSI Approved :: GNU General Public License (GPL)",
				 "Programming Language :: Python :: 3.7",
				 "Programming Language :: Python :: 3.8",
				 "Programming Language :: Python :: 3.9",
				 ],
	install_requires=["numpy>=1.8.0", "scipy>=0.13.0", "matplotlib>=1.2.0", "Zgoubi-metadata>=0.1"],
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
		print("Could not see install log, install may have failed.")
		print("Can't give help with setting up path")
		sys.exit(1)

	if lib_path.endswith(".egg"):
		lib_path = os.path.dirname(lib_path)

	try:
		if sys.platform == "win32":
			print("Add the following to your PATH variable in user Environment Variables control panel")
			#print "export PYTHONPATH=$PYTHONPATH:%s"%lib_path
			print(bin_path)
			bat_file = open(os.path.join( bin_path, "pyzgoubi.bat"), "w")
			bat_file.write("set PYTHONPATH=%%PYTHONPATH%%;%s\n"%lib_path)
			bat_file.write("python %s\\pyzgoubi %%*\n"%bin_path)
			bat_file.close()
		else:
			print("\nyou may need to add the following to your .bashrc")
			print("export PYTHONPATH=%s:$PYTHONPATH"%lib_path)
			print("export PATH=%s:$PATH"%bin_path)
	except NameError:
		print("Could not find all paths in logfile")


