from app.core.orchestrator import Orchestrator


class DummyTextModel:
    def generate(self, message):
        return f"chat:{message}"


class DummyWeather:
    def get_weather(self, city):
        return None

    def summarize_weather(self, city, data):
        return "weather"


class DummyTime:
    def get_current_time(self, timezone):
        return "2026-05-20 12:00:00 KST"


class DummyRobot:
    def __init__(self):
        self.executed = []

    def get_status(self):
        class Status:
            battery = 85
            mode = "idle"
            follow_enabled = False
            active_source = "idle"

        return Status()

    def execute_command(self, command, params=None):
        self.executed.append((command, params))
        raise AssertionError("server must not execute robot commands")


class DummyMemory:
    def save(self, key, content):
        return None

    def get(self, key):
        return None


class DummyNavigation:
    def navigate_to(self, waypoint):
        raise AssertionError("server must not navigate robot")

    def save_waypoint(self, **kwargs):
        raise AssertionError("server must not save robot waypoint")


def _orchestrator(robot=None):
    return Orchestrator(
        ollama_client=DummyTextModel(),
        gemini_client=None,
        weather_tool=DummyWeather(),
        time_tool=DummyTime(),
        robot_tool=robot or DummyRobot(),
        memory_store=DummyMemory(),
        navigation_tool=DummyNavigation(),
    )


def test_robot_motion_intents_are_local_only():
    robot = DummyRobot()
    orchestrator = _orchestrator(robot)

    response = orchestrator.process_message("버디봇 전진")

    assert "Pi" in response
    assert robot.executed == []


def test_stop_intent_is_not_executed_by_server():
    robot = DummyRobot()
    orchestrator = _orchestrator(robot)

    response = orchestrator.process_message("정지")

    assert "Pi" in response
    assert robot.executed == []


def test_general_chat_still_uses_ai_model():
    orchestrator = _orchestrator()

    assert orchestrator.process_message("오늘 할 일 정리해줘") == "chat:오늘 할 일 정리해줘"
