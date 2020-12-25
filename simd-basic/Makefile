png: simd-vertop.png \
     simd-cond.png \
     simd-shuffle-sample.png \
     simd-shuffle-reverse.png \
     simd-shuffle-broadcast.png

DEPS=simd-cond.tikz.py simd-vertop.tikz.py simd-shuffle.tikz.py tikz.py

simd-vertop.tex: $(DEPS)
	python3 simd-vertop.tikz.py $@

simd-cond.tex: $(DEPS)
	python3 simd-cond.tikz.py $@

simd-shuffle-sample.tex: $(DEPS)
	python3 simd-shuffle.tikz.py $@ shuffle

simd-shuffle-reverse.tex: $(DEPS)
	python3 simd-shuffle.tikz.py $@ reverse

simd-shuffle-broadcast.tex: $(DEPS)
	python3 simd-shuffle.tikz.py $@ broadcast

TIKZ2PNG=tikz2png --background white --quality 200

%.png: %.tex
	$(TIKZ2PNG) -i $<
