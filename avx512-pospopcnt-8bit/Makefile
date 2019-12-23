main.pdf: main.tex pospopcnt-sadbw-step1.tex pospopcnt-sadbw-step2.tex 
	pdflatex main.tex

pospopcnt-sadbw-step1.tex: pospopcnt-sadbw-step1.tikz.py tikz.py
	python3 pospopcnt-sadbw-step1.tikz.py $@

pospopcnt-sadbw-step2.tex: pospopcnt-sadbw-step2.tikz.py tikz.py
	python3 pospopcnt-sadbw-step2.tikz.py $@
