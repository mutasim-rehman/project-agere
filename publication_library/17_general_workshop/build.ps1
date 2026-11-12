$ErrorActionPreference='Stop'
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if($LASTEXITCODE){throw 'LaTeX failed'}
bibtex main
if($LASTEXITCODE){throw 'BibTeX failed'}
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if($LASTEXITCODE){throw 'LaTeX failed'}
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if($LASTEXITCODE){throw 'LaTeX failed'}
