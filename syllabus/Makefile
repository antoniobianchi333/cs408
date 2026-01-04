Q=@
all: syllabus.pdf

%.pdf: $(wildcard *.tex) $(wildcard figs/*.tex) $(wildcard code/*) $(wildcard *.bib)
	@echo "Building "$*
	$(Q)bin/latexrun --latex-args="--shell-escape" -Wall --bibtex-args=-min-crossrefs=100 $*

clean:
	rm -rf  syllabus.pdf latex.out

.PHONY: clean


include Makefile.spell
