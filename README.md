# P5R Assistant

Persona 5 Royal 中文对话选项助手。项目面向 Windows 桌面环境，用于从游戏窗口截图中识别中文对话选项，并根据本地攻略数据给出推荐选项。

仓库地址：https://github.com/Jay-LJH/p5r-assistant

## 功能概览

- 定位《女神异闻录 5 皇家版》或 Persona 5 Royal 游戏窗口。
- 截取并裁剪对话选项区域。
- 使用 RapidOCR 识别中文选项文本。
- 使用本地攻略数据匹配协助人、Rank、问题和推荐选项。
- 支持托盘应用、键盘热键、手柄组合键和一次性命令行识别。
- 使用 Qt 覆盖层显示推荐结果，支持右上角显示和 Windows topmost 提升。
- 支持保存调试截图，便于检查实际截取内容。

## 环境要求

- Windows
- Python 3.11+
- Persona 5 Royal

推荐使用窗口化、无边框窗口化或窗口化全屏运行游戏。普通桌面覆盖层通常无法覆盖真正的独占全屏 DirectX 画面。

## 安装

建议在虚拟环境中安装：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[ui,capture,ocr,input,dev]"
```

如果只需要导入攻略或做文本匹配，可以只安装基础包：

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

## 覆盖层显示

Qt 覆盖层会在识别后显示推荐结果：

- 默认显示在当前屏幕右上角。
- 使用更不透明的深色底和浅色边框，便于在游戏画面上阅读。
- 在 Windows 上显示后会调用原生 topmost 提升，减少被游戏窗口压住的情况。
- 显示时不会主动抢占游戏焦点。

如果覆盖层仍不可见，请优先确认游戏不是独占全屏模式，并尝试切换为无边框窗口化或窗口化全屏。

## data 文件

仓库跟踪基础配置文件：

- `data/settings.json`：热键、手柄组合、OCR、置信度、覆盖层超时和裁剪区域配置。
- `data/aliases.json`：OCR 别名修正配置，默认为空数组。

运行时可能生成以下文件，通常不需要提交：

- `data/guide.json`
- `data/guide.before-rank-up-clean.json`
- `data/app.log`
- `data/app.err.log`
- `data/debug-*.png`

## 真实窗口测试

测试真实游戏窗口时请确认：

- 游戏窗口标题能被系统识别为《女神异闻录 5 皇家版》、Persona 5 Royal 或 P5R。
- 游戏窗口没有被 Codex、VS Code、浏览器、终端或其他窗口遮挡。
- 当前画面是实际对话选项，而不是设置菜单、日历、SNS 转场或普通对话。

当前截图实现基于 `mss` 的屏幕矩形截图。它截取桌面当前像素，而不是绕过窗口遮挡直接读取游戏内容。因此，如果游戏窗口被其他窗口覆盖，OCR 可能会识别覆盖窗口里的文字。

调试时可以检查：

- `data/debug-full-window.png`
- `data/debug-choice-region.png`
- `data/debug-candidate-current.png`

## 测试

运行完整测试：

```powershell
pytest -q
```

如果系统临时目录权限异常，可以把 pytest 临时目录放到项目内：

```powershell
pytest -q -p no:cacheprovider --basetemp .tmp-pytest
```

运行窗口定位和截图区域相关测试：

```powershell
pytest tests/test_window_finder.py tests/test_choice_region_capture.py -q
```

运行覆盖层相关测试：

```powershell
pytest tests/test_qt_overlay_fullscreen.py tests/test_overlay.py tests/test_overlay_format.py -q
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
  desktop.py             # 桌面控制器
  capture/               # 窗口查找、截图、裁剪
  config/                # 配置读写
  guide/                 # 攻略数据导入与存取
  input/                 # 键盘和手柄触发
  match/                 # 文本归一化、别名和匹配
  ocr/                   # OCR 接口与 RapidOCR 适配
  ui/                    # 托盘和覆盖层 UI
tests/                   # 单元测试
htmls/                   # 攻略 HTML 来源
data/                    # 本地配置、运行数据和调试输出
```

## 当前限制

- 独占全屏游戏画面可能无法被普通桌面覆盖层覆盖。
- `mss` 不能绕过遮挡窗口捕获游戏内容。
- OCR 区域目前针对常见对话选项布局调校，不保证覆盖所有特殊 UI。
- 同分选项目前会显示第一个匹配项，后续可改为明确提示多个同分候选。
- 攻略导入质量依赖 HTML 来源结构，非对话表格可能仍需要继续清理。
