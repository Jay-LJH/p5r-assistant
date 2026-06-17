# Real Window Test Fix Handoff Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the blockers found during a real P5R window test so `run --recognize-once` can capture the Chinese-titled game window, pass the cropped image to RapidOCR, and produce a meaningful match.

**Architecture:** Keep the current pipeline: window lookup -> screenshot -> crop/preprocess -> OCR -> matcher -> overlay. The immediate fixes should be narrow compatibility changes in window matching, screenshot/OCR adaptation, and diagnostics; do not redesign the app.

**Tech Stack:** Python 3.11+, pywin32, mss, Pillow, numpy, rapidocr-onnxruntime, PySide6, pytest.

---

## Real Test Context

The user launched P5R in windowed mode. The visible window title is:

```text
女神异闻录5皇家版
```

The test machine successfully imports all runtime dependencies:

```text
PySide6: OK
mss: OK
PIL: OK
win32gui: OK
rapidocr_onnxruntime: OK
keyboard: OK
pygame: OK
cv2: OK
```

The current automated test suite also passes:

```powershell
pytest -q
```

Observed result:

```text
36 passed in 0.21s
```

## Observed Runtime Failures

### Failure 1: Window Finder Does Not Match the Chinese Game Title

Current command:

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m p5r_assistant.app run --recognize-once --no-keyboard --no-gamepad
```

The current default lookup in `p5r_assistant/capture/window_finder.py` only searches:

```python
("Persona 5 Royal", "P5R")
```

During real testing, Win32 enumeration found the game window:

```text
WindowInfo(handle=4917330, title='女神异闻录5皇家版', left=1293, top=243, width=1295, height=757)
```

But default lookup can also match the development environment window:

```text
P5R Assistant - Visual Studio Code
```

Root cause:

`"P5R"` is too broad and matches the repository/editor title, while the actual Chinese title is not included in the keyword list.

Recommended fix:

Make the default title keywords include the Chinese title and reduce false positives from development windows. Prefer exact known titles before broad aliases.

### Failure 2: RapidOCR Rejects PIL Images

Observed traceback:

```text
P5R Assistant error: The img type <class 'PIL.Image.Image'> does not in (<class 'str'>, <class 'numpy.ndarray'>, <class 'bytes'>, <class 'pathlib._local.Path'>)
rapidocr_onnxruntime.utils.LoadImageError: The img type <class 'PIL.Image.Image'> does not in (<class 'str'>, <class 'numpy.ndarray'>, <class 'bytes'>, <class 'pathlib._local.Path'>)
```

Root cause:

`p5r_assistant/ocr/rapidocr_engine.py` passes a `PIL.Image.Image` directly to RapidOCR:

```python
result, _ = self._engine(image)
```

The installed `rapidocr-onnxruntime` accepts path, bytes, or `numpy.ndarray`, not PIL images.

Recommended fix:

Convert PIL images to `numpy.ndarray` before calling RapidOCR. Add a unit test that uses a fake RapidOCR callable and asserts the argument type is not PIL.

### Failure 3: `mss` Captures the Screen Rectangle, Including Covering Windows

Debug artifacts generated during testing:

```text
data/debug-full-window.png
data/debug-choice-region.png
```

Observed content:

The saved "window" screenshot contained parts of Codex/VS Code and only part of the P5R window. The crop then OCR'd text from the assistant conversation instead of the game.

Example OCR output after manually converting the image to numpy:

```text
ocr_lines 7
0.689  (3, 71, 182, 110)      窗口名是
0.843  (213, 69, 688, 112)    女神异闻录5皇家版。我先
0.576  (1304, 231, 1408, 301) SNS
0.823  (3, 379, 297, 416)     ind_p5r_window
0.782  (325, 373, 669, 412)   命中了 VS Code 的
```

Root cause:

`mss` captures the current desktop pixels in the target rectangle. It does not capture the game window offscreen or through other windows. If the P5R window is partially covered, the screenshot includes the covering window.

Recommended fix:

For the immediate version, document and detect this limitation: the game window must be visible and unobstructed. Add debug capture output so developers can verify what was actually captured. A later improvement can use Windows window capture APIs instead of `mss` screen-rectangle capture.

### Failure 4: Guide Data Contains Non-Dialogue Tables

Current `data/guide.json` contains entries such as:

```text
['月亮', '三岛由辉']
['姓名', '日文名', '身高']
['Rank等级提升效果', 'RANK', 'Max', '解锁']
```

Root cause:

The importer is still parsing character info tables and Rank-effect tables as dialogue-choice events.

Impact:

Even after screenshot and OCR are fixed, matcher candidates may point to metadata tables instead of actual dialogue choices.

Recommended fix:

Treat guide-import cleanup as a follow-up task after the capture/OCR path is functional. Do not block the OCR/capture fix on full importer quality, but include importer quality in final manual acceptance.

---

## Task 1: Make Window Lookup Match the Chinese P5R Title Safely

**Files:**

- Modify: `p5r_assistant/capture/window_finder.py`
- Test: `tests/test_window_finder.py`

- [ ] **Step 1: Add tests for Chinese title and VS Code false positive**

Create or extend `tests/test_window_finder.py` with tests around a pure matching helper. If no helper exists, first extract one from `find_p5r_window`.

Suggested behavior:

```python
from p5r_assistant.capture.window_finder import is_p5r_window_title


def test_p5r_window_title_accepts_chinese_release_title():
    assert is_p5r_window_title("女神异闻录5皇家版")


def test_p5r_window_title_accepts_english_release_title():
    assert is_p5r_window_title("Persona 5 Royal")


def test_p5r_window_title_rejects_project_editor_title():
    assert not is_p5r_window_title("P5R Assistant - Visual Studio Code")
```

- [ ] **Step 2: Run the focused test and confirm it fails**

```powershell
pytest tests/test_window_finder.py -q
```

Expected before implementation: import error or assertion failure for `is_p5r_window_title`.

- [ ] **Step 3: Implement title matching helper**

In `p5r_assistant/capture/window_finder.py`, add a helper with exact-title priority:

```python
_EXACT_TITLES = {
    "Persona 5 Royal",
    "女神异闻录5皇家版",
}


def is_p5r_window_title(title: str) -> bool:
    normalized = title.strip()
    if normalized in _EXACT_TITLES:
        return True
    lowered = normalized.lower()
    if "visual studio code" in lowered or "codex" in lowered:
        return False
    return lowered == "p5r"
```

Then use this helper inside `find_p5r_window()`.

- [ ] **Step 4: Run tests**

```powershell
pytest tests/test_window_finder.py tests/test_choice_region_capture.py -q
```

Expected: all selected tests pass.

---

## Task 2: Convert PIL Images Before RapidOCR

**Files:**

- Modify: `p5r_assistant/ocr/rapidocr_engine.py`
- Test: `tests/test_rapidocr_engine.py`

- [ ] **Step 1: Add a unit test for image conversion**

Use a fake OCR callable so the test does not load actual OCR models:

```python
import numpy as np
from PIL import Image

from p5r_assistant.ocr.rapidocr_engine import RapidOcrEngine


class FakeRapidOCR:
    def __init__(self):
        self.seen = None

    def __call__(self, image):
        self.seen = image
        return [], None


def test_rapidocr_engine_converts_pil_image_to_numpy_array():
    fake = FakeRapidOCR()
    engine = RapidOcrEngine.__new__(RapidOcrEngine)
    engine._engine = fake

    image = Image.new("RGB", (8, 6), "white")
    lines = engine.recognize(image)

    assert lines == []
    assert isinstance(fake.seen, np.ndarray)
    assert fake.seen.shape == (6, 8, 3)
```

- [ ] **Step 2: Run the focused test and confirm it fails**

```powershell
pytest tests/test_rapidocr_engine.py -q
```

Expected before implementation: fake sees a `PIL.Image.Image`, not a numpy array.

- [ ] **Step 3: Implement conversion**

In `p5r_assistant/ocr/rapidocr_engine.py`, convert PIL-like images:

```python
def _to_rapidocr_input(image):
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        return image

    if isinstance(image, Image.Image):
        return np.array(image.convert("RGB"))
    return image
```

Then call:

```python
result, _ = self._engine(_to_rapidocr_input(image))
```

- [ ] **Step 4: Run OCR tests**

```powershell
pytest tests/test_rapidocr_engine.py tests/test_capture_ocr_interfaces.py -q
```

Expected: all selected tests pass.

---

## Task 3: Add Debug Capture Diagnostics for Manual Testing

**Files:**

- Modify: `p5r_assistant/app.py`
- Modify or create: `p5r_assistant/runtime.py`
- Test: `tests/test_app_runtime_cli.py`

- [ ] **Step 1: Add CLI flag tests**

Extend `tests/test_app_runtime_cli.py`:

```python
def test_run_command_accepts_debug_capture_dir():
    args = build_parser().parse_args(
        [
            "run",
            "--debug-capture-dir",
            "debug-output",
            "--no-keyboard",
            "--no-gamepad",
        ]
    )

    assert args.command == "run"
    assert args.debug_capture_dir == "debug-output"
```

- [ ] **Step 2: Run the focused test and confirm it fails**

```powershell
pytest tests/test_app_runtime_cli.py -q
```

Expected before implementation: argparse does not know `--debug-capture-dir`.

- [ ] **Step 3: Add the parser option**

In `p5r_assistant/app.py`, add to the `run` subparser:

```python
run.add_argument("--debug-capture-dir", default=None)
```

The first implementation can only parse and store the option. If wiring debug capture into the pipeline would require a larger refactor, keep this task scoped to parser support and add runtime wiring in a separate task.

- [ ] **Step 4: Run parser tests**

```powershell
pytest tests/test_app_runtime_cli.py -q
```

Expected: pass.

---

## Task 4: Manual Real-Window Verification

**Files:**

- No source modification required for this task after Tasks 1 and 2.
- Artifacts to inspect: `data/debug-full-window.png`, `data/debug-choice-region.png` if debug capture is wired.

- [ ] **Step 1: Start P5R in windowed mode**

Ensure the game window title is visible as:

```text
女神异闻录5皇家版
```

- [ ] **Step 2: Move P5R so it is fully visible and unobstructed**

Because current capture uses `mss`, the game must not be covered by Codex, VS Code, browser, terminal, or overlay windows.

- [ ] **Step 3: Enter a real dialogue-choice screen**

Do not test on the calendar/SNS transition screen. The crop needs visible selectable dialogue options.

- [ ] **Step 4: Run one-shot recognition**

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m p5r_assistant.app run --recognize-once --no-keyboard --no-gamepad
```

Expected after Tasks 1 and 2:

- No `WindowNotFoundError`.
- No `LoadImageError` about `PIL.Image.Image`.
- OCR runs and prints either a recommendation or candidates.

- [ ] **Step 5: If output is wrong, inspect capture first**

If OCR text contains Codex/VS Code/terminal text, the game was still covered or screen-coordinate capture is still wrong. Fix capture visibility before tuning OCR or matcher.

---

## Task 5: Follow-Up Importer Quality Check

**Files:**

- Modify later: `p5r_assistant/guide/importer.py`
- Test later: `tests/test_guide_importer.py`

- [ ] **Step 1: Quantify non-dialogue pollution**

Run:

```powershell
$env:PYTHONIOENCODING='utf-8'
@'
import json
from pathlib import Path
p=json.loads(Path("data/guide.json").read_text(encoding="utf-8"))
bad = []
for c in p["confidants"]:
    for e in c["events"]:
        for q in e["questions"]:
            texts = [ch["text"] for ch in q["choices"]]
            if any(t in texts for t in ["姓名", "日文名", "身高", "Rank等级提升效果", "出现条件"]):
                bad.append((c["name"], e["id"], texts[:5]))
print("bad_tables", len(bad))
for row in bad[:20]:
    print(row)
'@ | python -
```

- [ ] **Step 2: Decide whether importer cleanup blocks release**

If real OCR produces dialogue options but matcher returns metadata candidates, importer cleanup becomes a release blocker. If real OCR is still unstable, finish capture/OCR diagnostics first.

---

## Final Verification Commands

After implementing Tasks 1 and 2:

```powershell
pytest -q
```

Expected:

```text
all tests pass
```

Then run:

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m p5r_assistant.app run --startup-check --no-keyboard --no-gamepad
python -m p5r_assistant.app run --recognize-once --no-keyboard --no-gamepad
```

Expected:

- Startup check exits with code 0.
- One-shot recognition does not fail on window lookup or RapidOCR input type.
- If recognition quality is poor, the saved/observed screenshot must be checked before changing matcher thresholds.
