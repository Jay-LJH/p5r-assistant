# Windows Encoding Launch Design

## Goal

Fix Chinese text garbling when launching P5R Assistant from PowerShell or cmd, and add one-click Windows launch scripts that start the app in persistent tray mode.

## Current Context

The project is a Python package with CLI entry point `python -m p5r_assistant.app`. Runtime commands and README content are UTF-8, but Windows PowerShell and cmd can display UTF-8 Chinese output incorrectly when their active code page or Python stdio encoding is not UTF-8. The project currently has no root-level `.ps1` or `.cmd` launch script.

The default one-click behavior should be persistent tray mode:

```powershell
python -m p5r_assistant.app run
```

## Approach

Use a combined fix:

1. Add `run.ps1` for PowerShell users.
2. Add `run.cmd` for cmd or double-click usage.
3. Configure Python stdout/stderr encoding defensively in the CLI entry path so direct `python -m p5r_assistant.app ...` runs also prefer UTF-8.
4. Replace any already-garbled hard-coded Chinese UI strings in `p5r_assistant/ui/overlay.py` with correct UTF-8 Chinese text.

This keeps encoding setup close to launch concerns while leaving matching, OCR, capture, and guide data behavior unchanged.

## Script Behavior

`run.ps1` will:

- Set the PowerShell console output and input encoding to UTF-8.
- Set `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8`.
- Change to the repository root based on the script location.
- Run `python -m p5r_assistant.app run`.
- Return Python's exit code.

`run.cmd` will:

- Switch the console code page to UTF-8 with `chcp 65001`.
- Set `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8`.
- Change to the repository root based on the script location.
- Run `python -m p5r_assistant.app run`.
- Return Python's exit code.

## Python Encoding Fallback

The CLI module will add a small helper that calls `sys.stdout.reconfigure(encoding="utf-8")` and `sys.stderr.reconfigure(encoding="utf-8")` when available. This helper will be called at the start of `main()`. It should tolerate environments where streams do not support `reconfigure`, such as some test captures.

## Tests

Add focused tests for:

- The CLI configures UTF-8-capable stdout and stderr streams without failing on streams that do not support `reconfigure`.
- `run.ps1` contains the UTF-8 environment setup and starts `python -m p5r_assistant.app run`.
- `run.cmd` contains `chcp 65001`, the UTF-8 environment setup, and starts `python -m p5r_assistant.app run`.
- Overlay formatting returns correct Chinese labels for console and rich text output.

## Out of Scope

- Changing OCR, screenshot, guide import, or matching logic.
- Adding an installer.
- Changing the default runtime paths.
- Converting data files or generated logs.
