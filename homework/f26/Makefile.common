Q = @

# Directory that holds THIS file (with trailing slash).  Evaluated at
# include time, so bin/ and cmds.tex are found no matter which
# subdirectory make was run from.
TOP := $(dir $(lastword $(MAKEFILE_LIST)))

# Documents are the .tex files in the CURRENT directory only.
EXCLUDE ?=
SRCS = $(filter-out $(EXCLUDE),$(wildcard *.tex))
ALL  = $(SRCS:.tex=.pdf)

LATEXRUN ?= $(TOP)bin/latexrun

all: $(ALL)

%.pdf: %.tex FORCE
	@echo $*
	$(Q)$(LATEXRUN) --latex-args="--shell-escape" -Wall \
	    --bibtex-args=-min-crossrefs=100 $*

# Shared preamble: touching it rebuilds everything here.
$(ALL): $(TOP)cmds.tex

list:
	@echo $(ALL)

clean:
	rm -rf $(ALL) latex.out _minted-* *.aux *.log *.out

FORCE:

.PHONY: all clean list FORCE
