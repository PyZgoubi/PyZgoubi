#!/usr/bin/env python2

# makes zgoubi output files fai and plt in ascii and binary
# note that for plt files, the ascii/binary choise must be made at compile time by modifying include/FILPLT.H

binname = os.path.basename(zgoubi_settings['zgoubi_path'])
outdir = "result_"+binname
mkdir_p(outdir)

for binary in [True, False]:
	make_line('line')
	mass = PROTON_MASS
	energy = 1e6


	b_orig = Bunch.gen_halo_x_xp_y_yp(1e2, 1e-3, 1e-3, 4,5,1e-3, 2e-2, seed=4)

	b_orig_4d = numpy.column_stack([b_orig.particles()[col] for col in 'YTZP'])


	ob = OBJET2()
	ob.set(BORO=-ke_to_rigidity(energy, mass))
	for p in b_orig.particles():
		ob.add(D=1, Y=p['Y']*100, T=p['T']*1000, Z=p['Z']*100, P=p['P']*1000, LET='A')
	add(ob)
	add(PROTON())

	q1 = QUADRUPO(XL=1e-6, XPAS=(1,1,1), IL=2, B_0=1e-50, R_0=1)
	add(q1)

	if binary:
		add(FAISCNL(FNAME='b_zgoubi.fai'))
	else:
		add(FAISCNL(FNAME='zgoubi.fai'))

	add(END())

	res = run(xterm=False)
	
	if binary:
		try:
			res.save_b_fai(os.path.join(outdir,"binary.fai"))
		except IOError:
			print "could not save binary.fai"
		try:
			res.save_b_plt(os.path.join(outdir,"binary.plt"))
		except IOError:
			print "could not save binary.plt"
	else:
		res.save_fai(os.path.join(outdir,"ascii.fai"))
		try:
			res.save_fai("ascii.fai")
		except IOError:
			print "could not save ascii.fai"
		try:
			res.save_plt(os.path.join(outdir,"ascii.plt"))
		except IOError:
			print "could not save ascii.plt"


