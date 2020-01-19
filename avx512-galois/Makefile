main.pdf: main.tex gf2p8affine.tex
	pdflatex main.tex

png: pgf2p8affine.png

gf2p8affine.tex: gf2p8affine.tikz.py tikz.py
	python3 gf2p8affine.tikz.py $@
