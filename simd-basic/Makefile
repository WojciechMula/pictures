png: simd-vertop.png \
     simd-cond.png \
     simd-shuffle-sample.png \
     simd-shuffle-reverse.png \
     simd-shuffle-broadcast.png

DEPS=tikz.py

simd-vertop.tex: simd-vertop.tikz.py $(DEPS)
	python3 simd-vertop.tikz.py $@

simd-cond.tex: simd-cond.tikz.py $(DEPS)
	python3 simd-cond.tikz.py $@

simd-shuffle-sample.tex: simd-shuffle.tikz.py $(DEPS)
	python3 simd-shuffle.tikz.py $@ shuffle

simd-shuffle-reverse.tex: simd-shuffle.tikz.py $(DEPS)
	python3 simd-shuffle.tikz.py $@ reverse

simd-shuffle-broadcast.tex: simd-shuffle.tikz.py $(DEPS)
	python3 simd-shuffle.tikz.py $@ broadcast

TIKZ2PNG=tikz2png --background white --quality 200

%.png: %.tex
	$(TIKZ2PNG) -i $<
