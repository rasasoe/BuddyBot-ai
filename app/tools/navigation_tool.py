from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from app.config import Config
from app.logger import logger


class NavigationTool:
    def __init__(self):
        self.config = Config()
        self.repo_path = Path(self.config.BUDDYBOT_REPO_PATH)
        self.waypoint_file = (
            self.repo_path
            / "software"
            / "pi5"
            / "ros2_ws"
            / "src"
            / "buddybot_nav"
            / "config"
            / "waypoints.yaml"
        )

    def list_waypoints(self) -> List[Dict[str, Any]]:
        data = self._load_data()
        waypoints = data.get("waypoints", {})
        return [
            {
                "name": name,
                "x": float(item.get("pose", {}).get("x", 0.0)),
                "y": float(item.get("pose", {}).get("y", 0.0)),
                "theta": float(item.get("pose", {}).get("theta", 0.0)),
                "description": item.get("description", ""),
            }
            for name, item in waypoints.items()
        ]

    def get_waypoint(self, name: str) -> Optional[Dict[str, Any]]:
        return self._load_data().get("waypoints", {}).get(name)

    def save_waypoint(
        self,
        name: str,
        x: float,
        y: float,
        theta: float = 0.0,
        description: str = "",
    ) -> Dict[str, Any]:
        data = self._load_data()
        data.setdefault("waypoints", {})
        data["waypoints"][name] = {
            "pose": {"x": float(x), "y": float(y), "theta": float(theta)},
            "description": description or f"{name} checkpoint",
            "approach_distance": 0.5,
        }
        self._save_data(data)
        logger.info("Saved waypoint %s to %s", name, self.waypoint_file)
        return data["waypoints"][name]

    def navigate_to(self, name: str) -> Dict[str, Any]:
        waypoint = self.get_waypoint(name)
        if not waypoint:
            return {"success": False, "message": f"'{name}' 체크포인트를 찾지 못했습니다."}

        pose = waypoint.get("pose", {})
        return {
            "success": True,
            "message": (
                f"{name} 체크포인트로 이동을 시작합니다. "
                f"(x={pose.get('x')}, y={pose.get('y')}, theta={pose.get('theta')})"
            ),
            "waypoint": waypoint,
        }

    def analyze_map(self) -> Dict[str, Any]:
        items = self.list_waypoints()
        if not items:
            return {
                "count": 0,
                "bounds": {"min_x": -2.0, "max_x": 2.0, "min_y": -2.0, "max_y": 2.0},
                "zones": [],
                "recommended_destinations": [],
                "summary": "등록된 체크포인트가 아직 없습니다.",
            }

        xs = [item["x"] for item in items]
        ys = [item["y"] for item in items]
        bounds = {"min_x": min(xs), "max_x": max(xs), "min_y": min(ys), "max_y": max(ys)}

        zone_names = {
            "north_west": "좌상단 구역",
            "north_east": "우상단 구역",
            "south_west": "좌하단 구역",
            "south_east": "우하단 구역",
            "center": "중앙 구역",
        }
        zone_map: Dict[str, List[str]] = {name: [] for name in zone_names}

        for item in items:
            zone_map[self._infer_zone(item["x"], item["y"], bounds)].append(item["name"])

        zones = [
            {"name": zone_names[zone], "points": points}
            for zone, points in zone_map.items()
            if points
        ]
        recommended = [
            item["name"]
            for item in sorted(items, key=lambda item: abs(item["x"]) + abs(item["y"]))[:4]
        ]
        summary = (
            f"총 {len(items)}개의 체크포인트가 있습니다. "
            f"현재 좌표 분포상 빠르게 테스트하기 좋은 위치는 {', '.join(recommended[:2])} 입니다."
        )

        return {
            "count": len(items),
            "bounds": bounds,
            "zones": zones,
            "recommended_destinations": recommended,
            "summary": summary,
        }

    def _infer_zone(self, x: float, y: float, bounds: Dict[str, float]) -> str:
        mid_x = (bounds["min_x"] + bounds["max_x"]) / 2
        mid_y = (bounds["min_y"] + bounds["max_y"]) / 2
        if abs(x - mid_x) < 0.75 and abs(y - mid_y) < 0.75:
            return "center"
        if x <= mid_x and y >= mid_y:
            return "north_west"
        if x > mid_x and y >= mid_y:
            return "north_east"
        if x <= mid_x and y < mid_y:
            return "south_west"
        return "south_east"

    def _load_data(self) -> Dict[str, Any]:
        if not self.waypoint_file.exists():
            return {"waypoints": {}, "destinations": {}, "constraints": {}}
        with self.waypoint_file.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {"waypoints": {}, "destinations": {}, "constraints": {}}

    def _save_data(self, data: Dict[str, Any]) -> None:
        self.waypoint_file.parent.mkdir(parents=True, exist_ok=True)
        with self.waypoint_file.open("w", encoding="utf-8") as file:
            yaml.safe_dump(data, file, allow_unicode=True, sort_keys=False)
