.PHONY: doc clean all

DOCS = report.tex
PDFS = $(DOCS:%.tex=%.pdf)

all: doc

doc: $(DOCS)
	pdflatex $<
	rm *.aux *.log 

clean:
	rm -f $(PDFS)
