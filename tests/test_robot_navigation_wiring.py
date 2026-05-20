import shutil
from pathlib import Path

import pytest

from app.core.intent_router import IntentRouter
from app.tools import navigation_tool as navigation_tool_module
from app.tools.navigation_tool import NavigationTool
from app.tools.robot_tool import RobotTool


@pytest.fixture(autouse=True)
def reset_robot_tool_singleton():
    RobotTool._instance = None
    yield
    RobotTool._instance = None


def _repo_tmp_dir(name: str) -> Path:
    root = Path(__file__).resolve().parents[1] / ".test_tmp" / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_intent_router_handles_follow_and_manual_variants():
    assert IntentRouter.route("BuddyBot 따라와") == "robot_follow_start"
    assert IntentRouter.route("추종 꺼") == "robot_follow_stop"

    rotate_slots = IntentRouter.extract_slots("좌회전 2초", "robot_manual")
    assert rotate_slots["direction"] == "rotate_left"
    assert rotate_slots["duration"] == pytest.approx(2.0)

    strafe_slots = IntentRouter.extract_slots("오른쪽 이동 0.4 speed", "robot_manual")
    assert strafe_slots["direction"] == "strafe_right"
    assert strafe_slots["speed"] == pytest.approx(0.4)


def test_robot_tool_control_disabled_by_default(monkeypatch):
    tool = RobotTool()
    published = []

    monkeypatch.setattr(
        tool,
        "_publish_manual_velocity",
        lambda linear_x, linear_y, angular_z: published.append(
            ("manual", linear_x, linear_y, angular_z)
        ),
    )
    monkeypatch.setattr(
        tool,
        "_publish_follow_enabled",
        lambda enabled: published.append(("follow", enabled)),
    )
    monkeypatch.setattr(tool, "_cancel_navigation", lambda: published.append(("cancel",)))
    monkeypatch.setattr(
        tool,
        "_publish_navigation_goal",
        lambda name: published.append(("goal", name)),
    )

    follow_result = tool.execute_command("follow")
    assert follow_result["success"] is False
    assert tool.follow_enabled is False
    assert tool.nav_state == "idle"
    assert published == []

    dock_result = tool.execute_command("dock")
    assert dock_result["success"] is False
    assert tool.follow_enabled is False
    assert tool.nav_state == "idle"
    assert published == []


def test_robot_tool_manual_does_not_publish_when_disabled(monkeypatch):
    tool = RobotTool()
    published = []

    monkeypatch.setattr(
        tool,
        "_publish_manual_velocity",
        lambda linear_x, linear_y, angular_z: published.append((linear_x, linear_y, angular_z)),
    )
    monkeypatch.setattr(tool, "_publish_follow_enabled", lambda enabled: None)
    monkeypatch.setattr(tool, "_cancel_navigation", lambda: None)

    tool.execute_command(
        "manual",
        {"direction": "strafe_left", "speed": 0.4, "duration": 0},
    )
    assert published == []
    assert tool.manual_enabled is False
    assert tool.follow_enabled is False

    tool.execute_command(
        "manual",
        {"direction": "rotate_right", "speed": 0.25, "duration": 0},
    )
    assert published == []


def test_navigation_tool_saves_and_navigates_to_waypoints(monkeypatch):
    tmp_path = _repo_tmp_dir("navigation_save")
    monkeypatch.setattr(
        navigation_tool_module.Config,
        "BUDDYBOT_REPO_PATH",
        str(tmp_path),
    )
    published = []

    tool = NavigationTool()
    monkeypatch.setattr(
        tool,
        "_publish_waypoint_save",
        lambda name, waypoint: published.append(("save", name, waypoint)),
    )
    monkeypatch.setattr(
        tool,
        "_publish_waypoint_goal",
        lambda name: published.append(("goal", name)),
    )

    saved = tool.save_waypoint("kitchen", 1.25, -0.5, theta=0.75, description="Kitchen")
    assert saved["pose"] == {"x": 1.25, "y": -0.5, "theta": 0.75}
    assert published == []
    assert tool.waypoint_file.exists()

    tool.use_ros2 = True
    result = tool.navigate_to("kitchen")
    assert result["success"] is False
    assert published == []
    assert "x=1.25" in result["message"]
    assert "y=-0.5" in result["message"]


def test_navigation_tool_reports_missing_waypoint(monkeypatch):
    tmp_path = _repo_tmp_dir("navigation_missing")
    monkeypatch.setattr(
        navigation_tool_module.Config,
        "BUDDYBOT_REPO_PATH",
        str(tmp_path),
    )

    tool = NavigationTool()
    result = tool.navigate_to("missing")

    assert result["success"] is False
