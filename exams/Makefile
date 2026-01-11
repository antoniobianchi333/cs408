Q=@


ALL=final.pdf

all: $(ALL)


PLOTS_DATA = $(wildcard plots/*.dat)
PLOTS_SRCS = $(wildcard plots/*.plot)
PLOTS_PNGS = $(PLOTS_SRCS:.plot=.png)

ALL_TEX=$(ALL:.pdf=.tex)


$(ALL): $(wildcard *.tex) $(wildcard figs/*.tex) $(wildcard code/*) $(wildcard *.bib)  $(wildcard sections/*.tex) $(wildcard figs/*.pdf) $(PLOTS_PNGS) $(PLOTS_SRCS) 
	echo $(subst .pdf,,$@) 
	$(Q)bin/latexrun --latex-args="--shell-escape" -Wall --bibtex-args=-min-crossrefs=100 $(subst .pdf,,$@) 


SYS = $(shell sed -n -e 's/\\newcommand{\\sys}{\(.*\)}/\1/p' cmds.tex | sed -e 's/\\xspace//g' -e 's/\\textsc//g' -e 's/\\mbox//g')
abstr.txt: abstr.tex
	@cat $< | \
          sed -e 's/\\sys/${SYS}/g' | \
          sed -e 's/\\emph//g' | \
          sed -e 's/{//g' | \
          sed -e 's/}//g' | \
	  sed -e /^[%].*/d | \
          fmt -w72 > $@

%.png: %.plot  $(PLOTS_DATA)
	cd plots && gnuplot ../$<

code:
	gcc -o bug1 bug1.c

clean:
	rm -rf final.pdf midterm.pdf latex.out

.PHONY: abstr.txt clean

include Makefile.spell
