png: zigzag.png

DEPS=tikz.py \
     model.py

zigzag.tex: zigzag.tikz.py $(DEPS)
	python3 zigzag.tikz.py $@

TIKZ2PNG=tikz2png --background white --quality 200 --keep-tmp-files

%.png: %.tex
	$(TIKZ2PNG) -i $<
