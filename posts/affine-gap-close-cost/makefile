all: figures

figures: f0 f1 f2 f3
f0:
	drawio --export --format svg --transparent gapcost.drawio --embed -p 0 -o gapcost-gap-open.svg
f1:
	drawio --export --format svg --transparent gapcost.drawio --embed -p 1 -o gapcost-gap-close.svg
f2:
	drawio --export --format svg --transparent gapcost.drawio --embed -p 2 -o gapcost-symmetric-1.svg
f3:
	drawio --export --format svg --transparent gapcost.drawio --embed -p 3 -o gapcost-symmetric-2.svg
