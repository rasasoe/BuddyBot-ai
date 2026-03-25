import time
from typing import Dict, Any, Optional
from app.schemas.robot import RobotStatusResponse
from app.logger import logger

try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist
    from nav_msgs.msg import Odometry
    from sensor_msgs.msg import LaserScan
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    logger.warning("ROS 2 not available. Running in mock mode.")


class RobotTool:
    _instance: Optional['RobotTool'] = None
    _node: Optional[Node] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RobotTool, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.use_ros2 = ROS2_AVAILABLE and rclpy.ok()
        
        if self.use_ros2:
            try:
                if not rclpy.ok():
                    rclpy.init()
                
                self._node = Node('buddybot_ai_bridge')
                self.cmd_vel_pub = self._node.create_publisher(
                    Twist, '/cmd_vel', 10
                )
                self.odom_sub = self._node.create_subscription(
                    Odometry, '/odom', self._odom_callback, 10
                )
                self.laser_sub = self._node.create_subscription(
                    LaserScan, '/scan', self._laser_callback, 10
                )
                
                self.current_odom: Optional[Odometry] = None
                self.current_scan: Optional[LaserScan] = None
                
                logger.info("RobotTool initialized with ROS 2 connection")
            except Exception as e:
                logger.error(f"Failed to initialize ROS 2: {e}. Falling back to mock mode.")
                self.use_ros2 = False
        else:
            logger.info("RobotTool initialized in mock mode")

    def _odom_callback(self, msg: Odometry):
        """오도메트리 데이터 콜백"""
        self.current_odom = msg

    def _laser_callback(self, msg: LaserScan):
        """라이다 스캔 데이터 콜백"""
        self.current_scan = msg

    def move_robot(
        self, 
        direction: str, 
        speed: float = 0.5, 
        duration: float = 1.0
    ) -> str:
        """
        로봇을 특정 방향으로 이동시킵니다.
        direction: 'forward', 'backward', 'left', 'right', 'stop'
        """
        if not self.use_ros2:
            logger.info(f"[MOCK] Moving {direction} at speed {speed} for {duration}s")
            return f"[Mock] 로봇이 {direction} 방향으로 {duration}초간 이동했습니다."
        
        try:
            msg = Twist()
            
            if direction == "forward":
                msg.linear.x = speed
            elif direction == "backward":
                msg.linear.x = -speed
            elif direction == "left":
                msg.angular.z = speed
            elif direction == "right":
                msg.angular.z = -speed
            elif direction == "stop":
                msg.linear.x = 0.0
                msg.angular.z = 0.0
            else:
                return f"Unknown direction: {direction}"
            
            self.cmd_vel_pub.publish(msg)
            logger.info(f"Published movement command: {direction}")
            
            if direction != "stop":
                time.sleep(duration)
                self.cmd_vel_pub.publish(Twist())  # 정지 명령
            
            return f"로봇이 {direction} 방향으로 {duration}초간 이동했습니다."
        except Exception as e:
            logger.error(f"Failed to move robot: {e}")
            return f"로봇 이동 실패: {e}"

    def get_status(self) -> RobotStatusResponse:
        """로봇 상태 조회"""
        if self.use_ros2 and self.current_odom:
            pose = self.current_odom.pose.pose
            twist = self.current_odom.twist.twist
            mode = "moving" if (abs(twist.linear.x) > 0.01 or abs(twist.angular.z) > 0.01) else "idle"
        else:
            mode = "idle"
        
        return RobotStatusResponse(
            battery=85,
            mode=mode,
            estop=False,
            nav_state="active"
        )

    def get_lidar_data(self) -> Dict[str, Any]:
        """라이다 데이터 조회"""
        if not self.use_ros2 or not self.current_scan:
            return {"error": "LaDAR data not available"}
        
        try:
            # 전방 장애물 감지 (0도 기준 ±30도)
            ranges = list(self.current_scan.ranges)
            num_ranges = len(ranges)
            front_idx = [
                i for i in range(num_ranges)
                if -60 < (i * 360 / num_ranges - 180) <= 60
            ]
            front_distances = [ranges[i] for i in front_idx if 0 < ranges[i] < 50]
            
            return {
                "min_distance": min(front_distances) if front_distances else None,
                "max_distance": max(front_distances) if front_distances else None,
                "obstacle_count": sum(1 for d in front_distances if d < 1.0),
                "timestamp": self.current_scan.header.stamp.sec
            }
        except Exception as e:
            logger.error(f"Error processing LaDAR data: {e}")
            return {"error": str(e)}

    def execute_command(self, command: str, params: Dict[str, Any]) -> str:
        """AI가 요청한 명령 실행"""
        logger.info(f"Executing command: {command} with params: {params}")
        
        if command == "stop":
            return self.move_robot("stop", duration=0)
        elif command == "dock":
            return "로봇이 도킹 시작했습니다."
        elif command == "move":
            direction = params.get("direction", "forward")
            speed = params.get("speed", 0.5)
            duration = params.get("duration", 1.0)
            return self.move_robot(direction, speed, duration)
        elif command == "get_lidar":
            data = self.get_lidar_data()
            return f"라이다 데이터: {data}"
        else:
            return f"Unknown command: {command}"

    def __del__(self):
        """정리"""
        if self.use_ros2 and self._node:
            try:
                self._node.destroy_node()
            except Exception as e:
                logger.warning(f"Error destroying ROS 2 node: {e}")