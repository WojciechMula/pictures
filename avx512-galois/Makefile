png: gf2p8affine.png

DEPS=gf2p8affine.tikz.py gf2p8affine.py tikz.py

gf2p8affine.tex: $(DEPS)
	python3 gf2p8affine.tikz.py $@

TIKZ2PNG=tikz2png --background white --quality 200

%.png: %.tex
	$(TIKZ2PNG) -i $<
