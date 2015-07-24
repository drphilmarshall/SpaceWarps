# ----------------------------------------------------------------------------

all: papers

clean:
	-rm -f *.aux *.log *.dvi *.blg *.out

papers: system cfhtls

system: sw-system.pdf

cfhtls: sw-cfhtls.pdf

# ----------------------------------------------------------------------------
# Paper I:

sw-system.pdf: sw-system.tex macros.tex
	pdflatex sw-system.tex
	pdflatex sw-system.tex
	bibtex sw-system
	pdflatex sw-system.tex
	pdflatex sw-system.tex

# sw-system.bbl: sw-system.tex references.bib
# 	bubble -f sw-system.tex references.bib >& sw-system.bbl.log
# 	cat sw-system.bbl.log
#
# sw-system.dvi: sw-system.tex sw-system.bbl macros.tex
# 	latex sw-system.tex
# 	latex sw-system.tex
#
# sw-system.pdf: sw-system.dvi
# 	\dvipdf -sPAPERSIZE=a4 sw-system.dvi

# ----------------------------------------------------------------------------
# Paper II:

sw-cfhtls.pdf: sw-cfhtls.tex macros.tex
	pdflatex sw-cfhtls.tex
	pdflatex sw-cfhtls.tex
	bibtex sw-cfhtls
	pdflatex sw-cfhtls.tex
	pdflatex sw-cfhtls.tex

# ----------------------------------------------------------------------------
