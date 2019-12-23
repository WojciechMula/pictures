main.pdf: main.tex pospopcnt-sadbw-step1.tex pospopcnt-sadbw-byte-layout.tex pospopcnt-sadbw-reshuffled.tex 
	pdflatex main.tex

png: pospopcnt-sadbw-step1.png pospopcnt-sadbw-byte-layout.png pospopcnt-sadbw-reshuffled.png

pospopcnt-sadbw-step1.tex: pospopcnt-sadbw-step1.tikz.py tikz.py
	python3 pospopcnt-sadbw-step1.tikz.py $@

pospopcnt-sadbw-byte-layout.tex: pospopcnt-sadbw.tikz.py tikz.py
	python3 pospopcnt-sadbw.tikz.py byte-layout $@

pospopcnt-sadbw-reshuffled.tex: pospopcnt-sadbw.tikz.py tikz.py
	python3 pospopcnt-sadbw.tikz.py reshuffled $@

TIKZ2PNG=tikz2png --background white --quality 200

pospopcnt-sadbw-step1.png: pospopcnt-sadbw-step1.tex
	$(TIKZ2PNG) -i pospopcnt-sadbw-step1.tex

pospopcnt-sadbw-byte-layout.png: pospopcnt-sadbw-byte-layout.tex
	$(TIKZ2PNG) -i pospopcnt-sadbw-byte-layout.tex

pospopcnt-sadbw-reshuffled.png: pospopcnt-sadbw-reshuffled.tex
	$(TIKZ2PNG) -i pospopcnt-sadbw-reshuffled.tex
