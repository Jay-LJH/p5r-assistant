# P5R Assistant

Persona 5 Royal 中文对话选项助手。项目面向 Windows 桌面环境，用于从游戏窗口截图中识别中文对话选项，并根据本地攻略数据给出推荐候选。

## 功能概览

- 定位窗口化运行的《女神异闻录5 皇家版》游戏窗口。
- 截取并裁剪对话选项区域。
- 使用 RapidOCR 识别中文选项文本。
- 使用本地攻略数据匹配协助人、Rank、问题和推荐选项。
- 支持托盘应用、键盘热键、手柄组合键和一次性命令行识别。
- 支持保存调试截图，便于检查实际截取内容。

## 环境要求

- Windows
- Python 3.11+
- P5R 以窗口化方式运行

基础依赖在 `pyproject.toml` 中声明。运行真实窗口识别通常需要安装 `ui`、`capture`、`ocr`、`input` 和 `dev` 这些可选依赖组。

## 安装

建议在虚拟环境中安装：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[ui,capture,ocr,input,dev]"
```

如果只做攻略导入或文本匹配，可以安装基础包：

```powershell
python -m pip install -e .
```

## 常用命令

查看命令帮助：

```powershell
python -m p5r_assistant.app --help
```

导入攻略 HTML：

```powershell
python -m p5r_assistant.app import-guide --htmls htmls --out data/guide.json
```

清理攻略数据：

```powershell
python -m p5r_assistant.app clean-guide --guide data/guide.json
```

直接用文本测试匹配：

```powershell
python -m p5r_assistant.app match-text 金钱 爱情 出人头地 --guide data/guide.json
```

启动前检查运行时文件：

```powershell
python -m p5r_assistant.app run --startup-check --no-keyboard --no-gamepad
```

执行一次真实窗口识别：

```powershell
python -m p5r_assistant.app run --recognize-once --no-keyboard --no-gamepad
```

执行一次识别并保存调试截图：

```powershell
python -m p5r_assistant.app run --recognize-once --no-keyboard --no-gamepad --debug-capture-dir data
```

启动桌面托盘应用：

```powershell
python -m p5r_assistant.app run
```

## 真实窗口测试

真实窗口测试时请确认：

- 游戏窗口标题能被系统识别为《女神异闻录5 皇家版》或 Persona 5 Royal。
- 游戏处于窗口化模式。
- 游戏窗口没有被 Codex、VS Code、浏览器、终端或其他窗口遮挡。
- 当前画面是实际对话选项，而不是设置菜单、日历、SNS 转场或普通对话。

当前截图实现基于 `mss` 的屏幕矩形截图。它会截取桌面当前像素，而不是独立捕获游戏窗口内容。因此，如果游戏窗口被其他窗口覆盖，OCR 会识别覆盖窗口里的文字。

项目已处理 Windows DPI 缩放下 Win32 窗口坐标和屏幕像素坐标不一致的问题。调试时可以检查：

- `data/debug-full-window.png`
- `data/debug-choice-region.png`

如果 OCR 结果明显来自其他应用，先检查调试截图是否真的包含游戏画面。

## 测试

运行完整测试：

```powershell
pytest -q
```

运行窗口定位和截图区域相关测试：

```powershell
pytest tests/test_window_finder.py tests/test_choice_region_capture.py -q
```

运行 OCR 适配测试：

```powershell
pytest tests/test_rapidocr_engine.py -q
```

## 项目结构

```text
p5r_assistant/
  app.py                 # CLI 入口
  runtime.py             # 运行时组装
  capture/               # 窗口查找、截图、裁剪
  ocr/                   # OCR 接口与 RapidOCR 适配
  match/                 # 文本归一化、别名和匹配
  guide/                 # 攻略数据导入与存取
  input/                 # 键盘和手柄触发
  ui/                    # 托盘和覆盖层 UI
tests/                   # 单元测试
htmls/                   # 攻略 HTML 来源
data/                    # 本地运行数据和调试截图
```

## 当前限制

- `mss` 不能绕过遮挡窗口捕获游戏内容。
- OCR 区域目前针对常见对话选项布局调校，不保证覆盖所有特殊 UI。
- 同分选项目前会显示第一个匹配选项；后续应改为明确提示“三项同分”。
- 攻略导入质量依赖 HTML 来源结构，非对话表格可能仍需要继续清理。
