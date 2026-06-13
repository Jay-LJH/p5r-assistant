from p5r_assistant.guide.schema import Choice, Confidant, Event, Guide, Question
from p5r_assistant.match.aliases import AliasStore
from p5r_assistant.match.normalize import normalize_text
from p5r_assistant.ocr.engine import OcrLine
from p5r_assistant.recognition import RecognitionService


class FakeCapture:
    def capture_choice_region(self):
        return object()


class FakeOcr:
    def __init__(self, texts):
        self.texts = texts

    def recognize(self, image):
        return [OcrLine(text=text, confidence=0.9, box=(0, index * 10, 100, index * 10 + 8)) for index, text in enumerate(self.texts)]


class FakeOverlay:
    def __init__(self):
        self.confident = None
        self.candidates = None
        self.errors = []

    def show_recommendation(self, result):
        self.confident = result

    def show_candidates(self, result):
        self.candidates = result

    def show_error(self, message):
        self.errors.append(message)


def _guide() -> Guide:
    choices = [
        Choice("ann_rank_2_q1_c1", 1, "什么意思？", normalize_text("什么意思？"), 0),
        Choice("ann_rank_2_q1_c2", 2, "随便他们怎么说吧", normalize_text("随便他们怎么说吧"), 3),
    ]
    return Guide(
        1,
        "now",
        "tests",
        [Confidant("ann", "高卷杏", [Event("ann_rank_2", "rank_up", [Question("ann_rank_2_q1", choices)], 1, 2)])],
    )


def test_recognition_service_shows_confident_recommendation():
    overlay = FakeOverlay()
    service = RecognitionService(FakeCapture(), FakeOcr(["什么意思？", "随便他们怎么说吧"]), _guide(), AliasStore.empty(), overlay)

    result = service.recognize_once()

    assert result.confident is True
    assert overlay.confident.recommendation.choice.index == 2
    assert overlay.candidates is None


def test_recognition_service_shows_candidates_for_low_confidence():
    overlay = FakeOverlay()
    service = RecognitionService(FakeCapture(), FakeOcr(["完全不同", "看不清"]), _guide(), AliasStore.empty(), overlay)

    result = service.recognize_once()

    assert result.confident is False
    assert overlay.candidates is result
    assert overlay.confident is None
