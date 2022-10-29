#!/bin/bash
for f in *png ; do
	convert $f -resize 30% ${f%.png}.jpg
done
