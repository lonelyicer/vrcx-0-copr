SPEC := vrcx-0.spec
OUTDIR := $(CURDIR)

.PHONY: srpm
srpm:
	$(MAKE) -f .copr/Makefile srpm spec=$(abspath $(SPEC)) outdir=$(abspath $(OUTDIR))
