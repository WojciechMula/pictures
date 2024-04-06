png: vector-layout.png

DEPS=tikz.py

vector-layout.tex: vector-layout.tikz.py $(DEPS)
	python3 vector-layout.tikz.py $@

TIKZ2PNG=tikz2png --background white --quality 200 --debug --keep-tmp-files

%.png: %.tex
	$(TIKZ2PNG) -i $<
