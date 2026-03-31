import threading
from pathlib import Path
from typing import Dict, Optional

from app.config import Config
from app.logger import logger
from app.schemas.robot import RobotStatusResponse

try:
    import rclpy
    from geometry_msgs.msg import Twist
    from rclpy.node import Node

    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    rclpy = None
    Twist = None
    Node = object


class RobotTool:
    _instance: Optional["RobotTool"] = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.config = Config()
        self.workspace = str(Path(self.config.BUDDYBOT_REPO_PATH).resolve())
        self.follow_enabled = False
        self.manual_enabled = False
        self.estop = False
        self.battery = 85
        self.nav_state = "idle"
        self.active_source = "idle"
        self.last_command = "idle"
        self.use_ros2 = False
        self._ros_node = None
        self._manual_pub = None

        self._init_ros2()

    def _init_ros2(self) -> None:
        if not ROS2_AVAILABLE:
            logger.info("ROS 2 not available. RobotTool will run in mock mode.")
            return
        try:
            if not rclpy.ok():
                rclpy.init(args=None)
            self._ros_node = Node("buddybot_ai_bridge")
            self._manual_pub = self._ros_node.create_publisher(Twist, "/cmd_vel_manual", 10)
            self.use_ros2 = True
            logger.info("RobotTool connected to ROS 2 topics.")
        except Exception as exc:
            logger.warning("Failed to initialize ROS 2 bridge: %s", exc)
            self.use_ros2 = False

    def get_status(self) -> RobotStatusResponse:
        if self.follow_enabled:
            mode = "follow"
        elif self.manual_enabled:
            mode = "manual"
        elif self.nav_state == "docking":
            mode = "dock"
        else:
            mode = "idle"

        return RobotStatusResponse(
            battery=self.battery,
            mode=mode,
            estop=self.estop,
            nav_state=self.nav_state,
            follow_enabled=self.follow_enabled,
            manual_enabled=self.manual_enabled,
            ros2_connected=self.use_ros2,
            active_source=self.active_source,
            last_command=self.last_command,
            buddybot_workspace=self.workspace if Path(self.workspace).exists() else None,
        )

    def execute_command(self, command: str, params: Optional[Dict[str, float]] = None) -> Dict[str, object]:
        params = params or {}
        normalized = command.lower().strip()
        logger.info("Executing command=%s params=%s", normalized, params)

        if normalized == "status":
            return self._result("현재 로봇 상태를 확인했습니다.")
        if normalized == "stop":
            self.follow_enabled = False
            self.manual_enabled = False
            self.nav_state = "stopped"
            self.active_source = "manual_stop"
            self._publish_manual_velocity(0.0, 0.0)
            return self._result("로봇을 정지했습니다.")
        if normalized == "dock":
            self.follow_enabled = False
            self.manual_enabled = False
            self.nav_state = "docking"
            self.active_source = "nav"
            return self._result("도킹 모드로 전환했습니다.")
        if normalized in {"follow", "follow_start"}:
            self.follow_enabled = True
            self.manual_enabled = False
            self.nav_state = "tracking_user"
            self.active_source = "follow"
            return self._result("사용자 추종을 시작했습니다.")
        if normalized in {"follow_stop", "unfollow"}:
            self.follow_enabled = False
            self.nav_state = "idle"
            self.active_source = "idle"
            return self._result("사용자 추종을 중지했습니다.")
        if normalized in {"manual", "move"}:
            return self._handle_manual_move(params)

        return self._result(f"지원하지 않는 명령입니다: {command}", success=False)

    def _handle_manual_move(self, params: Dict[str, float]) -> Dict[str, object]:
        direction = str(params.get("direction", "forward")).lower()
        speed = float(params.get("speed", 0.3))
        duration = float(params.get("duration", 1.5))

        linear_x = 0.0
        angular_z = 0.0
        if direction == "forward":
            linear_x = speed
        elif direction == "backward":
            linear_x = -speed
        elif direction == "left":
            angular_z = speed
        elif direction == "right":
            angular_z = -speed
        elif direction == "stop":
            linear_x = 0.0
            angular_z = 0.0
        else:
            return self._result(f"지원하지 않는 수동 이동 방향입니다: {direction}", success=False)

        self.follow_enabled = False
        self.manual_enabled = direction != "stop"
        self.nav_state = "manual_control"
        self.active_source = "manual"
        self._publish_manual_velocity(linear_x, angular_z)

        if direction != "stop" and duration > 0:
            timer = threading.Timer(duration, self._publish_manual_velocity, args=(0.0, 0.0))
            timer.daemon = True
            timer.start()

        return self._result(f"수동 조작: {direction}, 속도 {speed}, 시간 {duration}초")

    def _publish_manual_velocity(self, linear_x: float, angular_z: float) -> None:
        self.last_command = f"manual({linear_x:.2f},{angular_z:.2f})"

        if not self.use_ros2 or self._manual_pub is None:
            logger.info("[MOCK] publish /cmd_vel_manual linear_x=%s angular_z=%s", linear_x, angular_z)
            if linear_x == 0.0 and angular_z == 0.0:
                self.manual_enabled = False
                if not self.follow_enabled and self.nav_state == "manual_control":
                    self.nav_state = "idle"
                    self.active_source = "idle"
            return

        twist = Twist()
        twist.linear.x = linear_x
        twist.angular.z = angular_z
        self._manual_pub.publish(twist)

        if linear_x == 0.0 and angular_z == 0.0:
            self.manual_enabled = False
            if not self.follow_enabled and self.nav_state == "manual_control":
                self.nav_state = "idle"
                self.active_source = "idle"

    def _result(self, message: str, success: bool = True) -> Dict[str, object]:
        self.last_command = message
        return {"success": success, "message": message, "status": self.get_status()}
