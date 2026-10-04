# COPR calls: make -f .copr/Makefile srpm outdir=... spec=...
spec ?= vrcx-0.spec
outdir ?= $(CURDIR)

.PHONY: srpm
srpm:
	dnf -y install rpmdevtools
	spectool -g -C $(dir $(spec)) $(spec)
	rpmbuild -bs $(spec) \
		--define "_sourcedir $(dir $(spec))" \
		--define "_srcrpmdir $(outdir)" \
		--define "_disable_source_fetch 0"
