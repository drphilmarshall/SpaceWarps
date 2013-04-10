                                                                                                                                                               
all: papers

clean:
	-rm -f *.aux *.log *.dvi *.blg *.out *.bbl sw-system.pdf

papers: sw-system.pdf

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
