#!/usr/bin/env python

"""Functions to download and build zgoubi. To use run::

	pyzgoubi --install-zgoubi
	or
	pyzgoubi --install-zgoubi version

To so a list of avaliable versions run::

	pyzgoubi --install-zgoubi list


"""

import os
import sys
import shutil
import subprocess
import urllib2
from zgoubi import common

class ZgoubiBuildError(Exception):
	"Problem building Zgoubi"
	pass


zgoubi_build_dir = os.path.join(os.path.expanduser("~"), ".pyzgoubi", "build")
zgoubi_build_dir2 = os.path.join(zgoubi_build_dir, "zgoubi-trunk")
zgoubi_install_dir = os.path.join(os.path.expanduser("~"), ".pyzgoubi", "bin")
#zgoubi_svn_address = "https://zgoubi.svn.sourceforge.net/svnroot/zgoubi/trunk"
#zgoubi_svn_address = "http://svn.code.sf.net/p/zgoubi/code/trunk"
zgoubi_svn_address = "svn://svn.code.sf.net/p/zgoubi/code/trunk"

if sys.platform == "win32": exe_ext = ".exe"
else: exe_ext = ""

def check_for_programs():
	"Check that required programs are installed"
	devnull = open(os.devnull, "w")
	try:
		subprocess.call(['svn', '--version'], stdout=devnull)
	except OSError:
		raise ZgoubiBuildError("svn not found: install subversion")
	try:
		subprocess.call(['patch', '--version'], stdout=devnull)
	except OSError:
		raise ZgoubiBuildError("patch not found: install patch")


def get_zgoubi_svn():
	"Download zgoubi from SVN"
	if os.path.isdir(zgoubi_build_dir2):
		print "Zgoubi build folder already exists:", zgoubi_build_dir
		ret = subprocess.call(['svn', 'info'], cwd=zgoubi_build_dir2)
		if ret == 0:
			print "Zgoubi SVN already present at:", zgoubi_build_dir
			print "Reverting local changes"
			ret2 = subprocess.call(['svn', 'revert', '-R', '.'], cwd=zgoubi_build_dir2)
			return
		
		if ret != 0 or ret2 != 0:
			raise ZgoubiBuildError("%s already exists, but does not contain a working checkout")

	print "Downloading Zgoubi SVN:", zgoubi_svn_address
	common.mkdir_p(zgoubi_build_dir)
	ret = subprocess.call(['svn', 'co', zgoubi_svn_address, "zgoubi-trunk"], cwd=zgoubi_build_dir)
	if ret != 0:
		raise ZgoubiBuildError("SVN download failed")


def set_zgoubi_version(version=None):
	"Set downloaded SVN to a given version. or, if no version given, to latest version"
	ret = subprocess.call(['svn', 'revert', '-R', '.'], cwd=zgoubi_build_dir2)
	if version == None:
		ret = subprocess.call(['svn', 'update'], cwd=zgoubi_build_dir2)
	else:
		ret = subprocess.call(['svn', 'update', '-r', '%s'%version], cwd=zgoubi_build_dir2)
	if ret != 0:
		raise ZgoubiBuildError("SVN update failed")


def apply_zgoubi_patches(patches):
	"Download and apply a set of patches"
	for patch in patches:
		print "applying", patch
		patchname = patch.rpartition("/")[2]
		pf = open(os.path.join(zgoubi_build_dir2, patchname), "w")
		try:
			pf.write(urllib2.urlopen(patch).read())
		except urllib2.HTTPError as e:
			raise ZgoubiBuildError("Patch download failed (Error %s): %s" % (e.code, patch))
			
		pf.close()
		ret = subprocess.call('patch -p0 < %s' % patchname, cwd=zgoubi_build_dir2, shell=True)
		if ret != 0:
			raise ZgoubiBuildError("Patch application failed: %s" % patch)

def edit_includes(includes):
	"Set compile time variables, e.g. max magnet steps"
	for fname, sourcelines in includes:
		print "Editing", os.path.join("include", fname)
		file_content = open(os.path.join(zgoubi_build_dir2, "include", fname)).readlines()
		newfile = open(os.path.join(zgoubi_build_dir2, "include", fname), "w")
		for line in file_content:
			if not line.startswith("C"):
				newfile.write("C      Commented out by pyzgoubi build script\n")
				line = "C"+line
			newfile.write(line)
		for sourceline in sourcelines:
			newfile.write("       "+sourceline+"\n")




def make_zgoubi(makecommands, threads=2, clean=True):
	"Build zgoubi source code"
	print "building zgoubi"
	if clean:
		ret = subprocess.call(['make', 'clean'], cwd=zgoubi_build_dir2)
		if ret != 0:
			raise ZgoubiBuildError("Make clean failed")
	for makecommand in makecommands:
		command = makecommand.split()+ ['-j%d'%threads]
		ret = subprocess.call(command, cwd=zgoubi_build_dir2)
		if ret != 0:
			raise ZgoubiBuildError("Building zgoubi failed:" + " ".join(command))

def install_zgoubi(suffix="", install_zpop=True):
	"Install zgoubi into ~/.pyzgoubi folder"
	common.mkdir_p(zgoubi_install_dir)

	shutil.copy(os.path.join(zgoubi_build_dir2, "zgoubi", "zgoubi"+exe_ext),
	                os.path.join(zgoubi_install_dir, "zgoubi%s"%suffix+exe_ext))
	if install_zpop:
		shutil.copy(os.path.join(zgoubi_build_dir2, "zpop", "zpop"),
		            os.path.join(zgoubi_install_dir, "zpop%s"%suffix))


zgoubi_versions = {}
zgoubi_versions["261+patches"] = dict(svnr=261,
patches=[
"http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/mcmodel-fix.diff",
"http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/zgoubi_parallel_build.diff",
"http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/objet3.diff",
"http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/kobj301.diff",
],
)

zgoubi_versions["329+patches"] = dict(svnr=329,
patches=[
"http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/build_tweaks2.diff",
"http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/kobj301_3.diff",
],
makecommands=["make -f Makefile_zgoubi_gfortran"],
makecommands_zpop=["make -f Makefile_zpop_gfortran"],
includes=[
["MXSTEP.H", ["PARAMETER (MXSTEP = 10000)"]]
],
)

zgoubi_versions["360+patches"] = dict(svnr=360,
patches=[
"http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/build_tweaks2.diff",
"http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/kobj301_4.diff",
],
makecommands=["make -f Makefile_zgoubi_gfortran"],
makecommands_zpop=["make -f Makefile_zpop_gfortran"],
includes=[
["MXSTEP.H", ["PARAMETER (MXSTEP = 10000)"]],
],
)

zgoubi_versions["365"] = dict(svnr=365,
patches=[
"http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/build_tweaks2.diff",
#"http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/kobj301_4.diff",
],
makecommands=["make -f Makefile_zgoubi_gfortran"],
makecommands_zpop=["make -f Makefile_zpop_gfortran"],
includes=[
["MXSTEP.H", ["PARAMETER (MXSTEP = 10000)"]],
],
)

#on 32bit some arrays need shrinking
zgoubi_versions["365_32bit"] = dict(svnr=365,
patches=[
"http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/build_tweaks2.diff",
#"http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/kobj301_4.diff",
],
makecommands=["make -f Makefile_zgoubi_gfortran"],
makecommands_zpop=["make -f Makefile_zpop_gfortran"],
includes=[
["MXSTEP.H", ["PARAMETER (MXSTEP = 10000)"]],
[os.path.join("..", "zgoubi", "PARIZ.H"), ["PARAMETER (IZ = 61, ID=3, MMAP=8)", "PARAMETER (MXX=801, MXY=29)"]],
],
)
if sys.platform == "win32":
	zgoubi_versions["365_32bit"]["patches"][0] = "http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/build_tweaks2_windows.diff"
	zgoubi_versions["365"]["patches"][0] = "http://www.hep.man.ac.uk/u/sam/pyzgoubi/zgoubipatches/build_tweaks2_windows.diff"

def install_zgoubi_all(version="365"):
	"This currently install a version of zgoubi known to work with pyzgoubi"
	check_for_programs()
	if sys.platform.startswith('linux'):
		build_zpop = True
	else:
		build_zpop = False

	if version in ['list', 'help']:
		print "Available versions:", " ".join(zgoubi_versions.keys())
		exit(0)
	if not zgoubi_versions.has_key(version):
		raise ZgoubiBuildError("Unknown version: "+ version+ "\nTry "+ " ".join(zgoubi_versions.keys()))
	print "Preparing to install zgoubi:", version
	get_zgoubi_svn()
	set_zgoubi_version(zgoubi_versions[version]['svnr'])
	apply_zgoubi_patches(zgoubi_versions[version]['patches'])
	if zgoubi_versions[version].has_key("includes"):
		edit_includes(zgoubi_versions[version]["includes"])
	
	make_zgoubi(zgoubi_versions[version].get("makecommands", ['make']))
	if build_zpop:
		makecommands_zpop = zgoubi_versions[version].get("makecommands_zpop", None)
		if makecommands_zpop:
			make_zgoubi(makecommands_zpop, clean=False)


	install_zgoubi("_"+version, build_zpop)
	print "\nInstalled zgoubi into ", zgoubi_install_dir
	print "Add the following line to ~/.pyzgoubi/settings.ini"
	print "zgoubi_path =", os.path.join(zgoubi_install_dir, "zgoubi_"+version+exe_ext)

if __name__ == "__main__":
	install_zgoubi_all()
