png: simd-vertop.png

DEPS=simd-vertop.tikz.py tikz.py

simd-vertop.tex: $(DEPS)
	python3 simd-vertop.tikz.py $@

TIKZ2PNG=tikz2png --background white --quality 200

%.png: %.tex
	$(TIKZ2PNG) -i $<
