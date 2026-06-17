$ErrorActionPreference = "Stop"

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8NoBom
[Console]::InputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Set-Location -LiteralPath $PSScriptRoot
& python -m p5r_assistant.app run
exit $LASTEXITCODE
