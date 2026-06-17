# Windows Encoding Launch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add UTF-8-safe Windows launch scripts for persistent tray mode and harden CLI/overlay Chinese text output.

**Architecture:** Root-level `run.ps1` and `run.cmd` configure the Windows console and Python UTF-8 environment before invoking the existing CLI. `p5r_assistant.app` adds a small stdout/stderr encoding helper, and `p5r_assistant.ui.overlay` keeps all user-visible Chinese labels as valid UTF-8 source text.

**Tech Stack:** Python 3.11, pytest, Windows PowerShell, cmd batch.

---

### Task 1: Tests for CLI Encoding and Launch Scripts

**Files:**
- Modify: `tests/test_app_cli.py`
- Create: `tests/test_windows_launch_scripts.py`

- [ ] **Step 1: Add failing CLI encoding tests**

Add tests that import `configure_utf8_stdio`, monkeypatch stdout/stderr with fake streams, and assert `reconfigure(encoding="utf-8")` is called when supported and skipped when unsupported.

- [ ] **Step 2: Add failing launch script tests**

Create tests that read `run.ps1` and `run.cmd` and assert the scripts set UTF-8 console/Python environment and invoke `python -m p5r_assistant.app run`.

- [ ] **Step 3: Run tests to verify red**

Run:

```powershell
pytest tests/test_app_cli.py tests/test_windows_launch_scripts.py -q
```

Expected: failures because `configure_utf8_stdio`, `run.ps1`, and `run.cmd` do not exist yet.

### Task 2: Implement CLI Encoding Fallback and Scripts

**Files:**
- Modify: `p5r_assistant/app.py`
- Create: `run.ps1`
- Create: `run.cmd`

- [ ] **Step 1: Add CLI encoding helper**

Add `configure_utf8_stdio()` to `p5r_assistant/app.py`. It should iterate over `sys.stdout` and `sys.stderr`, call `reconfigure(encoding="utf-8")` when available, and ignore `AttributeError`, `TypeError`, `ValueError`, and `OSError`.

- [ ] **Step 2: Call helper from `main()`**

Call `configure_utf8_stdio()` before parsing arguments.

- [ ] **Step 3: Add PowerShell launch script**

Create `run.ps1` that sets `[Console]::OutputEncoding`, `[Console]::InputEncoding`, `$OutputEncoding`, `PYTHONUTF8`, and `PYTHONIOENCODING`, changes to `$PSScriptRoot`, runs `python -m p5r_assistant.app run`, and exits with `$LASTEXITCODE`.

- [ ] **Step 4: Add cmd launch script**

Create `run.cmd` that runs `chcp 65001`, sets `PYTHONUTF8` and `PYTHONIOENCODING`, changes to `%~dp0`, runs `python -m p5r_assistant.app run`, and exits with `%ERRORLEVEL%`.

- [ ] **Step 5: Run tests to verify green**

Run:

```powershell
pytest tests/test_app_cli.py tests/test_windows_launch_scripts.py -q
```

Expected: all selected tests pass.

### Task 3: Tests and Fix for Overlay Text

**Files:**
- Modify: `tests/test_overlay.py`
- Modify: `p5r_assistant/ui/overlay.py`

- [ ] **Step 1: Add failing overlay rich text assertions**

Add tests that assert `format_recommendation_rich_text()` includes `推荐：第`, `项`, `好感：`, and `置信度`, and `format_candidates()` includes `匹配不确定` and `第`.

- [ ] **Step 2: Run tests to verify red**

Run:

```powershell
pytest tests/test_overlay.py -q
```

Expected: failures for currently garbled rich-text/candidate labels.

- [ ] **Step 3: Replace garbled overlay strings**

Update `ROMANCE_CONDITION_RE`, `format_recommendation_rich_text()`, and `format_candidates()` so hard-coded Chinese labels are valid UTF-8 text matching console output semantics.

- [ ] **Step 4: Run tests to verify green**

Run:

```powershell
pytest tests/test_overlay.py -q
```

Expected: all overlay tests pass.

### Task 4: Final Verification

**Files:**
- Verify only.

- [ ] **Step 1: Run focused tests**

Run:

```powershell
pytest tests/test_app_cli.py tests/test_windows_launch_scripts.py tests/test_overlay.py -q
```

Expected: all focused tests pass.

- [ ] **Step 2: Run full suite**

Run:

```powershell
pytest -q
```

Expected: full suite passes, or any unrelated environment failure is reported with exact output.

- [ ] **Step 3: Inspect git diff**

Run:

```powershell
git diff -- p5r_assistant/app.py p5r_assistant/ui/overlay.py tests/test_app_cli.py tests/test_overlay.py tests/test_windows_launch_scripts.py run.ps1 run.cmd
```

Expected: diff is limited to approved spec scope.
