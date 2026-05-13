$ErrorActionPreference = "Stop"

Write-Host "Running Nyay end-to-end portfolio checks..." -ForegroundColor Cyan

.\myenv\Scripts\python.exe tests\e2e_test.py

$html = Get-Content -Path frontend.html -Raw
$script = [regex]::Match($html, '<script>([\s\S]*)</script>').Groups[1].Value
$tmp = "frontend-check.tmp.js"
Set-Content -Path $tmp -Value $script
try {
  node --check .\$tmp
  Write-Host "PASS frontend JavaScript syntax" -ForegroundColor Green
}
finally {
  if (Test-Path $tmp) {
    Remove-Item -LiteralPath $tmp
  }
}

Write-Host "All E2E checks passed." -ForegroundColor Green
