Param(
  [string]$PythonBin = "python",
  [string]$VenvDir = ".venv"
)

Write-Host "[*] Using Python: $PythonBin"
& $PythonBin -V

if (!(Test-Path $VenvDir)) {
  Write-Host "[*] Creating venv at $VenvDir"
  & $PythonBin -m venv $VenvDir
}

Write-Host "[*] Upgrading pip/setuptools/wheel"
& "$VenvDir\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel

Write-Host "[*] Installing project in editable mode"
& "$VenvDir\Scripts\python.exe" -m pip install -e .

Write-Host ""
Write-Host "[*] Done. Activate with:"
Write-Host "    $VenvDir\Scripts\Activate.ps1"
Write-Host ""
Write-Host "[*] Example run:"
Write-Host "    $VenvDir\Scripts\llm-arena.exe --prompt 'Erkläre TCP in drei Sätzen' --reveal-provenance false"
