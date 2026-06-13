# P5R Assistant V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable Python v1 that imports local P5R guide HTML, normalizes and matches OCR text to guide choices, persists settings and aliases, and exposes a tray/overlay application shell.

**Architecture:** Keep risky integrations behind small interfaces. The guide importer, matcher, config store, and overlay presenter are testable without Windows game state; capture, hotkey, and OCR engines have safe fallbacks so the app can start on a development machine.

**Tech Stack:** Python 3.11+, PySide6 for UI, BeautifulSoup/lxml for HTML parsing, rapidfuzz for matching, pytest for tests, optional mss/pywin32/rapidocr/opencv/keyboard/pygame integrations.

---

### Task 1: Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `p5r_assistant/__init__.py`
- Create: `p5r_assistant/app.py`
- Create: `tests/test_smoke.py`

- [ ] **Step 1: Write the failing test**

```python
def test_package_imports():
    import p5r_assistant

    assert p5r_assistant.__version__
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_smoke.py -v`
Expected: FAIL because package or version is missing.

- [ ] **Step 3: Write minimal implementation**

Create metadata, package version, and an app entrypoint with `main()`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_smoke.py -v`
Expected: PASS.

### Task 2: Data Schemas And JSON Stores

**Files:**
- Create: `p5r_assistant/guide/schema.py`
- Create: `p5r_assistant/config/settings.py`
- Create: `p5r_assistant/match/aliases.py`
- Create: `tests/test_settings_aliases.py`

- [ ] **Step 1: Write failing tests**

Test default settings creation and alias round-trip persistence.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_settings_aliases.py -v`
Expected: FAIL because modules are missing.

- [ ] **Step 3: Implement dataclasses and atomic JSON writes**

Add guide dataclasses, settings defaults, and alias store read/write helpers.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_settings_aliases.py -v`
Expected: PASS.

### Task 3: Text Normalization

**Files:**
- Create: `p5r_assistant/match/normalize.py`
- Create: `tests/test_normalize.py`

- [ ] **Step 1: Write failing normalization tests**

Cover whitespace, full-width forms, punctuation variants, ellipsis, and known OCR noise.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_normalize.py -v`
Expected: FAIL because normalizer is missing.

- [ ] **Step 3: Implement normalization**

Use `unicodedata.normalize("NFKC", text)`, punctuation mapping, and noise removal.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_normalize.py -v`
Expected: PASS.

### Task 4: Guide Importer

**Files:**
- Create: `p5r_assistant/guide/importer.py`
- Create: `p5r_assistant/guide/repository.py`
- Create: `tests/test_guide_importer.py`

- [ ] **Step 1: Write failing importer tests**

Use synthetic Chinese HTML table fixtures and one real local HTML page when available.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_guide_importer.py -v`
Expected: FAIL because importer is missing.

- [ ] **Step 3: Implement conservative parser**

Extract title/name, rank-like headings, table rows with choice text and point values, and collect import warnings for unsupported tables.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_guide_importer.py -v`
Expected: PASS.

### Task 5: Matcher

**Files:**
- Create: `p5r_assistant/match/matcher.py`
- Create: `tests/test_matcher.py`

- [ ] **Step 1: Write failing matcher tests**

Cover exact match, fuzzy OCR typo, alias-improved match, low confidence candidate list, and highest-points recommendation.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_matcher.py -v`
Expected: FAIL because matcher is missing.

- [ ] **Step 3: Implement scorer**

Compare visible option groups against guide questions using rapidfuzz when present and `difflib` fallback otherwise.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_matcher.py -v`
Expected: PASS.

### Task 6: Capture And OCR Interfaces

**Files:**
- Create: `p5r_assistant/capture/window_finder.py`
- Create: `p5r_assistant/capture/screenshot.py`
- Create: `p5r_assistant/capture/crop.py`
- Create: `p5r_assistant/ocr/engine.py`
- Create: `p5r_assistant/ocr/preprocess.py`
- Create: `p5r_assistant/ocr/rapidocr_engine.py`
- Create: `tests/test_capture_ocr_interfaces.py`

- [ ] **Step 1: Write failing interface tests**

Verify crop region math and fake OCR engine line grouping.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_capture_ocr_interfaces.py -v`
Expected: FAIL because interfaces are missing.

- [ ] **Step 3: Implement interfaces and fallbacks**

Add pure-Python crop calculations, optional dependency imports, and explicit errors for unavailable Windows/OCR dependencies.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_capture_ocr_interfaces.py -v`
Expected: PASS.

### Task 7: UI Shell And Recognition Service

**Files:**
- Create: `p5r_assistant/ui/overlay.py`
- Create: `p5r_assistant/ui/tray.py`
- Create: `p5r_assistant/ui/settings_window.py`
- Create: `p5r_assistant/input/keyboard_hotkey.py`
- Create: `p5r_assistant/input/gamepad.py`
- Create: `p5r_assistant/recognition.py`
- Create: `tests/test_recognition.py`

- [ ] **Step 1: Write failing recognition tests**

Inject fake capture, OCR, guide repository, and overlay presenter; verify confident and low-confidence paths.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_recognition.py -v`
Expected: FAIL because recognition service is missing.

- [ ] **Step 3: Implement service and UI shell**

Add dependency-injected recognition flow, PySide6 overlay/tray if available, and console fallback if PySide6 is absent.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_recognition.py -v`
Expected: PASS.

### Task 8: CLI Commands And Verification

**Files:**
- Modify: `p5r_assistant/app.py`
- Create: `tests/test_app_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Verify `import-guide`, `match-text`, and `run` argument parsing.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_app_cli.py -v`
Expected: FAIL because commands are missing.

- [ ] **Step 3: Implement CLI**

Add `python -m p5r_assistant.app import-guide --htmls htmls --out data/guide.json`, `match-text`, and `run`.

- [ ] **Step 4: Run full verification**

Run: `python -m pytest -v`
Expected: PASS.

