png: simd-vertop.png simd-cond.png

DEPS=simd-cond.tikz.py simd-vertop.tikz.py tikz.py

simd-vertop.tex: $(DEPS)
	python3 simd-vertop.tikz.py $@

simd-cond.tex: $(DEPS)
	python3 simd-cond.tikz.py $@

TIKZ2PNG=tikz2png --background white --quality 200

%.png: %.tex
	$(TIKZ2PNG) -i $<
