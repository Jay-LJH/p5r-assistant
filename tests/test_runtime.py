from pathlib import Path

from p5r_assistant.ocr.engine import OcrLine
from p5r_assistant.runtime import RuntimePaths, build_recognition_service, ensure_guide


class FakeCapture:
    def capture_choice_region(self):
        return object()


class FakeOcr:
    def recognize(self, image):
        return [
            OcrLine("什么意思？", 0.95, (0, 0, 100, 10)),
            OcrLine("随便他们怎么说吧", 0.95, (0, 20, 100, 30)),
        ]


class FakeOverlay:
    def __init__(self):
        self.recommendation = None

    def show_recommendation(self, result):
        self.recommendation = result

    def show_candidates(self, result):
        self.recommendation = result

    def show_error(self, message):
        raise AssertionError(message)


def test_ensure_guide_imports_html_when_json_is_missing(tmp_path: Path):
    htmls = tmp_path / "htmls"
    htmls.mkdir()
    (htmls / "高卷杏.htm").write_text(
        "<html><head><title>高卷杏 - 女神转生WIKI</title></head><body>"
        "<h3>Rank 2</h3><table><tr><td>什么意思？</td><td>0</td></tr>"
        "<tr><td>随便他们怎么说吧</td><td>3</td></tr></table></body></html>",
        encoding="utf-8",
    )
    paths = RuntimePaths(data_dir=tmp_path / "data", htmls_dir=htmls)

    guide = ensure_guide(paths)

    assert paths.guide_path.exists()
    assert guide.confidants[0].name == "高卷杏"


def test_build_recognition_service_wires_runtime_components(tmp_path: Path):
    htmls = tmp_path / "htmls"
    htmls.mkdir()
    (htmls / "高卷杏.htm").write_text(
        "<html><head><title>高卷杏 - 女神转生WIKI</title></head><body>"
        "<h3>Rank 2</h3><table><tr><td>什么意思？</td><td>0</td></tr>"
        "<tr><td>随便他们怎么说吧</td><td>3</td></tr></table></body></html>",
        encoding="utf-8",
    )
    overlay = FakeOverlay()
    paths = RuntimePaths(data_dir=tmp_path / "data", htmls_dir=htmls)

    service = build_recognition_service(paths, capture=FakeCapture(), ocr=FakeOcr(), overlay=overlay)
    result = service.recognize_once()

    assert result.recommendation.choice.index == 2
    assert overlay.recommendation is result
