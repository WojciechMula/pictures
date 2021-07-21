png: simdutf-mapping-all.png \
     simdutf-mapping-1byte.png \
     simdutf-mapping-2bytes.png \
     simdutf-mapping-3bytes.png \
     simdutf-mapping-4bytes.png \
     simdutf-mapping-123.png \
     simdutf-utf8toutf16-case1.png

DEPS=simdutf-mapping.tikz.py tikz.py
DEPS2=simdutf-utf8toutf16-case1.tikz.py tikz.py common.py

simdutf-mapping-all.tex: $(DEPS)
	python3 simdutf-mapping.tikz.py $@ 1234

simdutf-mapping-1byte.tex: $(DEPS)
	python3 simdutf-mapping.tikz.py $@ 1

simdutf-mapping-2bytes.tex: $(DEPS)
	python3 simdutf-mapping.tikz.py $@ 2

simdutf-mapping-3bytes.tex: $(DEPS)
	python3 simdutf-mapping.tikz.py $@ 3

simdutf-mapping-4bytes.tex: $(DEPS)
	python3 simdutf-mapping.tikz.py $@ 4

simdutf-mapping-123.tex: $(DEPS)
	python3 simdutf-mapping.tikz.py $@ 123

simdutf-utf8toutf16-case1.tex: $(DEPS2)
	python3 simdutf-utf8toutf16-case1.tikz.py $@

TIKZ2PNG=tikz2png --background white --quality 250

%.png: %.tex
	$(TIKZ2PNG) -i $<
