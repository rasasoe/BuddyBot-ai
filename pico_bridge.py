import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
import serial
import time
import math
from tf2_ros import TransformBroadcaster

class PicoBridge(Node):
    def __init__(self):
        super().__init__('pico_bridge')
        
        # 1. 시리얼 설정 (피코 연결 포트 확인: 보통 /dev/ttyACM0)
        try:
            self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
        except:
            self.ser = serial.Serial('/dev/ttyACM1', 115200, timeout=0.1)

        # 2. ROS 2 설정
        self.subscription = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        # 3. 로봇 상태 변수 (오도메트리용)
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        self.last_time = self.get_clock().now()

        # 타이머: 피코로부터 피드백 읽기 (20Hz)
        self.timer = self.create_timer(0.05, self.read_feedback)
        self.get_logger().info("Pico Bridge Node Started")

    def cmd_vel_callback(self, msg):
        # Twist 메시지를 피코 형식으로 변환 (vx, vy, angular_z_dps)
        vx = msg.linear.x
        vy = msg.linear.y
        w_dps = math.degrees(msg.angular.z)
        
        command = f"{vx:.2f},{vy:.2f},{w_dps:.2f}\n"
        self.ser.write(command.encode())

    def read_feedback(self):
        if self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8').strip()
            if line.startswith("FEEDBACK:"):
                try:
                    # FEEDBACK:rpm1,rpm2,rpm3 파싱
                    rpms = list(map(float, line.replace("FEEDBACK:", "").split(',')))
                    self.calculate_odometry(rpms)
                except:
                    pass

    def calculate_odometry(self, rpms):
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9
        
        # 3륜 옴니휠 역기구학 (피코 코드의 반대 과정)
        # 단순화를 위해 명령값 기준으로 위치를 추정하거나, 실제 RPM 기반 정기구학 식 적용
        # 여기서는 피코에서 계산된 값을 기반으로 dt 동안의 이동량 계산 (예시 로직)
        
        # 실제로는 RPM -> vx, vy, vth 계산 식이 들어가야 함
        # 임시로 cmd_vel 값을 적분하여 로봇 위치 시뮬레이션 가능
        # (매핑을 위해서는 반드시 이 부분에서 실제 이동량을 TF로 쏴줘야 함)
        
        # ... (정기구학 계산 생략 - 필요시 추가 구현) ...

        self.last_time = current_time

def main():
    rclpy.init()
    node = PicoBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
