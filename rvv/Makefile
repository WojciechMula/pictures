png: vector-layout.png \
     reduce.png \
     compress.png \
     iota.png

DEPS=tikz.py

vector-layout.tex: vector-layout.tikz.py $(DEPS)
	python3 vector-layout.tikz.py $@

reduce.tex: reduce.tikz.py $(DEPS)
	python3 reduce.tikz.py $@

compress.tex: compress.tikz.py $(DEPS)
	python3 compress.tikz.py $@

iota.tex: iota.tikz.py $(DEPS)
	python3 iota.tikz.py $@

TIKZ2PNG=tikz2png --background white --quality 200 --keep-tmp-files

%.png: %.tex
	$(TIKZ2PNG) -i $<
