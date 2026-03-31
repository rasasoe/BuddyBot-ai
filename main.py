from machine import Pin, PWM
import time
import math
import sys
import uselect

# --- [클래스 정의] 기존 준혁님 코드 유지 ---

class Motor:
    """단일 모터를 제어하는 클래스"""
    def __init__(self, en_pin, in1_pin, in2_pin, pwm_freq=10000):
        self.en = PWM(Pin(en_pin))
        self.en.freq(pwm_freq)
        self.in1 = Pin(in1_pin, Pin.OUT)
        self.in2 = Pin(in2_pin, Pin.OUT)
        self.stop()

    def move(self, speed):
        duty = int(min(abs(speed), 65535))
        if speed > 0:
            self.in1.value(1)
            self.in2.value(0)
            self.en.duty_u16(duty)
        elif speed < 0:
            self.in1.value(0)
            self.in2.value(1)
            self.en.duty_u16(duty)
        else:
            self.stop()

    def stop(self):
        self.in1.value(0)
        self.in2.value(0)
        self.en.duty_u16(0)

class Encoder:
    """단일 엔코더의 펄스 수를 세는 클래스"""
    def __init__(self, pin_a):
        self.pin_a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.count = 0
        self.last_tick = 0
        self.pin_a.irq(trigger=Pin.IRQ_RISING, handler=self._pulse)

    def _pulse(self, pin):
        current_tick = time.ticks_us()
        if time.ticks_diff(current_tick, self.last_tick) > 200:
            self.count += 1
        self.last_tick = current_tick

    def get_count(self):
        return self.count

    def reset(self):
        self.count = 0

class OmniRobot:
    """옴니휠 로봇의 모든 제어를 총괄하는 클래스"""
    def __init__(self):
        # 로봇 사양
        self.WHEEL_DIAMETER_M = 0.06
        self.GEAR_RATIO = 30
        self.PPR = 11
        self.PULSE_PER_WHEEL_REV = self.PPR * self.GEAR_RATIO
        self.WHEEL_CIRCUMFERENCE = self.WHEEL_DIAMETER_M * math.pi
        self.WHEEL_DISTANCE_FROM_CENTER = 0.1
        self.MOTOR_ANGLES_DEG = [0, 120, 240] 
        
        # P 제어 게인
        self.kp = 1000.0
        
        # [준혁님 수정본] 핀 매핑 반영
        self.motors = [Motor(12, 10, 11), Motor(2, 0, 1), Motor(8, 6, 7)]
        self.encoders = [Encoder(13), Encoder(3), Encoder(9)]
        
        # 상태 변수
        self.target_rpms = [0.0, 0.0, 0.0]
        self.current_rpms = [0.0, 0.0, 0.0]
        self.pwm_outputs = [0.0, 0.0, 0.0]
        self.last_update_time = time.ticks_ms()
        self.last_encoder_counts = [0, 0, 0]

    def _calculate_target_rpms(self, vx, vy, angular_velocity_radps):
        L = self.WHEEL_DISTANCE_FROM_CENTER
        for i in range(3):
            motor_angle_rad = math.radians(self.MOTOR_ANGLES_DEG[i])
            wheel_linear_velocity = -math.sin(motor_angle_rad) * vx + math.cos(motor_angle_rad) * vy + L * angular_velocity_radps
            self.target_rpms[i] = (wheel_linear_velocity / self.WHEEL_CIRCUMFERENCE) * 60

    def stop(self):
        for motor in self.motors:
            motor.stop()
        self.target_rpms = [0.0, 0.0, 0.0]

    def update(self):
        current_time = time.ticks_ms()
        dt_ms = time.ticks_diff(current_time, self.last_update_time)
        if dt_ms < 10: return
        dt_s = dt_ms / 1000.0

        for i in range(3):
            current_count = self.encoders[i].get_count()
            pulse_diff = current_count - self.last_encoder_counts[i]
            direction = 1 if self.pwm_outputs[i] >= 0 else -1
            revolutions = pulse_diff / self.PULSE_PER_WHEEL_REV
            self.current_rpms[i] = (revolutions / dt_s) * 60 * direction if dt_s > 0 else 0
            self.last_encoder_counts[i] = current_count
            
            error = self.target_rpms[i] - self.current_rpms[i]
            self.pwm_outputs[i] = self.kp * error
            self.pwm_outputs[i] = max(-65535, min(65535, self.pwm_outputs[i]))
            self.motors[i].move(self.pwm_outputs[i])
            
        self.last_update_time = current_time

# --- [메인 실행 루프] ROS 2 통신 대응 ---

def main():
    robot = OmniRobot()
    poll_obj = uselect.poll()
    poll_obj.register(sys.stdin, uselect.POLLIN)

    print("BuddyBot Pico: ROS 2 Bridge Active") # 시작 알림
    last_feedback_time = time.ticks_ms()

    while True:
        # 1. 시리얼 명령 확인 (라즈베리파이 5 -> Pico)
        poll_results = poll_obj.poll(1) # 1ms 대기
        if poll_results:
            line = sys.stdin.readline().strip()
            if line:
                try:
                    # "vx,vy,w_dps" 형식 파싱 (예: "0.1,0.0,45.0")
                    parts = line.split(',')
                    if len(parts) == 3:
                        vx, vy, w_dps = map(float, parts)
                        w_radps = math.radians(w_dps) # 도 -> 라디안 변환
                        robot._calculate_target_rpms(vx, vy, w_radps)
                    elif line == "STOP":
                        robot.stop()
                except:
                    pass

        # 2. 로봇 하드웨어 업데이트 (P제어)
        robot.update()

        # 3. 오도메트리 피드백 송신 (Pico -> 라즈베리파이 5)
        # 20Hz(50ms) 주기로 현재 각 바퀴의 RPM 전송
        curr_time = time.ticks_ms()
        if time.ticks_diff(curr_time, last_feedback_time) > 50:
            print(f"FEEDBACK:{robot.current_rpms[0]:.2f},{robot.current_rpms[1]:.2f},{robot.current_rpms[2]:.2f}")
            last_feedback_time = curr_time

if __name__ == "__main__":
    main()
