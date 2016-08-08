#!/bin/bash

export PATH=$PATH:/usr/texbin

latexmk -cd -e -f -pdf -interaction=nonstopmode -synctex=1 "main.tex"
