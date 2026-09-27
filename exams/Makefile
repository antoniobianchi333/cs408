Q = @

# ---------------------------------------------------------------------------
# Every .tex directly inside a subdirectory is treated as a document to build,
# so f26-midterm-1/midterm1.tex -> f26-midterm-1/midterm1.pdf.  The directory
# and the file do not need to share a name.
#
# Fragments meant only for \input (cmds.tex and friends) should live in THIS
# directory, not in an exam subdirectory.  If you must keep one alongside a
# document, add it to EXCLUDE below, e.g.
#     EXCLUDE = f26-final/preamble.tex
# ---------------------------------------------------------------------------

EXCLUDE =
SRCS    = $(filter-out $(EXCLUDE),$(wildcard */*.tex))
ALL     = $(SRCS:.tex=.pdf)

all: $(ALL)

# -cd tells latexmk to chdir into the source file's directory before running,
# so \input{../cmds} and figures/... resolve correctly and the aux files stay
# beside the source instead of littering this directory.
#
# FORCE (rather than marking the PDFs .PHONY) makes the rule run every time:
# make's wildcards cannot see \input'd files, figures or the minted cache, but
# latexmk tracks all of them in its own .fdb_latexmk database and exits almost
# instantly when nothing has changed.  Note that marking a target .PHONY would
# stop make from applying this pattern rule at all.
%.pdf: %.tex FORCE
	@echo $*
	$(Q)latexmk -pdf -cd -shell-escape -interaction=nonstopmode $*.tex

# Convenience aliases, so `make f26-midterm-1` builds everything in that
# directory.  One alias per subdirectory that contains a document.
EXAMDIRS = $(sort $(patsubst %/,%,$(dir $(SRCS))))
define EXAM_ALIAS
$(1): $$(filter $(1)/%,$$(ALL))
.PHONY: $(1)
endef
$(foreach d,$(EXAMDIRS),$(eval $(call EXAM_ALIAS,$(d))))

clean:
	$(Q)$(foreach s,$(SRCS),latexmk -C -cd $(s);)
	$(Q)rm -rf */_minted* */*.synctex.gz

# Print what would be built, without building it.
list:
	@echo $(ALL)

FORCE:

.PHONY: all clean list FORCE
