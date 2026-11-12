$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
    if ($LASTEXITCODE) { throw 'PDFLaTeX failed; inspect main.log' }
    bibtex main
    if ($LASTEXITCODE) { throw 'BibTeX failed; inspect main.blg' }
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
    if ($LASTEXITCODE) { throw 'PDFLaTeX failed; inspect main.log' }
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
    if ($LASTEXITCODE) { throw 'PDFLaTeX failed; inspect main.log' }
} finally {
    Pop-Location
}
