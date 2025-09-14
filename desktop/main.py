"""
Capfit 데스크톱 애플리케이션 - 웹 서버 + 브라우저 방식
EXE 배포에 최적화된 구조
"""

import sys
import os
import socket
import webbrowser
import threading
import time
import signal
from pathlib import Path
from typing import Optional

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from web.server import app


class DesktopApp:
    """데스크톱 애플리케이션 - 웹 서버 + 브라우저 자동 실행"""
    
    def __init__(self):
        self.server_thread: Optional[threading.Thread] = None
        self.server_process: Optional[uvicorn.Server] = None
        self.port = self._find_available_port()
        self.host = "127.0.0.1"  # 로컬호스트만 사용 (보안)
        self.url = f"http://{self.host}:{self.port}"
        
    def _find_available_port(self, start_port: int = 8000) -> int:
        """사용 가능한 포트 찾기"""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        
        # 8000-8099 범위에서 포트를 찾지 못한 경우 9000부터 시도
        for port in range(9000, 9100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        
        raise RuntimeError("사용 가능한 포트를 찾을 수 없습니다.")
    
    def _start_server(self):
        """웹 서버 시작 (백그라운드 스레드)"""
        try:
            config = uvicorn.Config(
                app=app,
                host=self.host,
                port=self.port,
                log_level="warning",  # 로그 레벨을 warning으로 설정하여 콘솔 출력 최소화
                access_log=False,     # 액세스 로그 비활성화
            )
            self.server_process = uvicorn.Server(config)
            self.server_process.run()
        except Exception as e:
            print(f"서버 시작 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def _wait_for_server(self, timeout: int = 10) -> bool:
        """서버가 시작될 때까지 대기"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                import requests
                response = requests.get(f"{self.url}/health", timeout=1)
                if response.status_code == 200:
                    return True
            except:
                pass
            time.sleep(0.5)
        return False
    
    def _open_browser(self):
        """기본 브라우저에서 애플리케이션 열기"""
        try:
            webbrowser.open(self.url)
            print(f"브라우저에서 {self.url} 을 열었습니다.")
        except Exception as e:
            print(f"브라우저 열기 실패: {e}")
            print(f"수동으로 {self.url} 을 브라우저에서 열어주세요.")
    
    def _setup_signal_handlers(self):
        """시그널 핸들러 설정 (Ctrl+C 등)"""
        def signal_handler(signum, frame):
            print("\n애플리케이션을 종료합니다...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start(self):
        """애플리케이션 시작"""
        print("🐱 Capfit 데스크톱 애플리케이션을 시작합니다...")
        print(f"포트: {self.port}")
        
        # 시그널 핸들러 설정
        self._setup_signal_handlers()
        
        # 웹 서버 시작
        self.server_thread = threading.Thread(target=self._start_server, daemon=True)
        self.server_thread.start()
        
        # 서버 시작 대기
        print("웹 서버를 시작하는 중...")
        if not self._wait_for_server():
            print("❌ 서버 시작에 실패했습니다.")
            return False
        
        print("✅ 웹 서버가 시작되었습니다.")
        
        # 브라우저 열기
        self._open_browser()
        
        print(f"\n📱 Capfit이 실행 중입니다!")
        print(f"🌐 URL: {self.url}")
        print(f"💡 브라우저를 닫아도 서버는 계속 실행됩니다.")
        print(f"🛑 종료하려면 Ctrl+C를 누르세요.")
        
        # 메인 스레드에서 서버 스레드 대기
        try:
            self.server_thread.join()
        except KeyboardInterrupt:
            print("\n애플리케이션을 종료합니다...")
            self.stop()
        
        return True
    
    def stop(self):
        """애플리케이션 종료"""
        if self.server_process:
            try:
                self.server_process.should_exit = True
                print("웹 서버를 종료합니다...")
            except Exception as e:
                print(f"서버 종료 중 오류: {e}")


def main():
    """메인 함수 - EXE 진입점"""
    try:
        app = DesktopApp()
        success = app.start()
        if not success:
            print("❌ 애플리케이션 시작에 실패했습니다.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 애플리케이션 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()