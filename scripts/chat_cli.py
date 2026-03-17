#!/usr/bin/env python3
"""
BuddyBot CLI Chat Client
자연어로 BuddyBot과 대화할 수 있는 간단한 CLI 클라이언트
"""

import requests
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 설정
BASE_URL = os.getenv("BUDDYBOT_BASE_URL", "http://localhost:8000")

def chat_with_buddybot():
    print("🤖 BuddyBot과 대화를 시작합니다! (종료하려면 'exit' 또는 'quit' 입력)")
    print("-" * 50)

    while True:
        try:
            # 사용자 입력
            user_input = input("나: ").strip()

            # 종료 조건
            if user_input.lower() in ['exit', 'quit', '종료']:
                print("🤖 BuddyBot: 안녕히 가세요!")
                break

            # 빈 입력 무시
            if not user_input:
                continue

            # API 요청
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": user_input},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                bot_response = data.get("response", "응답을 받지 못했습니다.")
                print(f"🤖 BuddyBot: {bot_response}")
            else:
                print(f"❌ 오류: {response.status_code} - {response.text}")

        except KeyboardInterrupt:
            print("\n🤖 BuddyBot: 대화를 종료합니다.")
            break
        except requests.RequestException as e:
            print(f"❌ 네트워크 오류: {e}")
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")

        print()  # 빈 줄

if __name__ == "__main__":
    chat_with_buddybot()