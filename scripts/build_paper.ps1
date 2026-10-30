$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$paperDirectory = Join-Path $projectRoot 'paper'
Push-Location -LiteralPath $paperDirectory
try {
    & pdflatex -interaction=nonstopmode -halt-on-error main.tex
    if ($LASTEXITCODE -ne 0) { throw 'First LaTeX pass failed' }
    & biber main
    if ($LASTEXITCODE -ne 0) { throw 'Bibliography build failed' }
    & pdflatex -interaction=nonstopmode -halt-on-error main.tex
    if ($LASTEXITCODE -ne 0) { throw 'Second LaTeX pass failed' }
    & pdflatex -interaction=nonstopmode -halt-on-error main.tex
    if ($LASTEXITCODE -ne 0) { throw 'Final LaTeX pass failed' }
    $destination = Join-Path $projectRoot 'output/pdf'
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Copy-Item -LiteralPath 'main.pdf' -Destination (Join-Path $destination 'UK_Small_Model_Census_2026-10-30.pdf')
} finally {
    Pop-Location
}
