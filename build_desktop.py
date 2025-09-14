"""
데스크톱 버전 실행 파일 빌드 스크립트
PyInstaller를 사용하여 독립 실행 파일 생성
"""

import os
import sys
import subprocess
from pathlib import Path


def build_desktop():
    """데스크톱 버전 빌드"""
    print("Capfit 데스크톱 버전 빌드 시작...")
    
    # PyInstaller 설치 확인
    try:
        import PyInstaller
        print(f"PyInstaller 버전: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller가 설치되지 않았습니다. 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller>=5.0.0"])
    
    # 빌드 명령어 구성
    build_cmd = [
        "pyinstaller",
        "--onefile",  # 단일 실행 파일로 생성
        "--windowed",  # 콘솔 창 숨김 (GUI 앱)
        "--name=Capfit",
        "--icon=desktop/assets/icon.ico",  # 아이콘 파일 (있는 경우)
        "--add-data=shared;shared",  # shared 모듈 포함
        "--hidden-import=PIL",
        "--hidden-import=numpy",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "desktop/main.py"
    ]
    
    # 아이콘 파일이 없으면 해당 옵션 제거
    if not Path("desktop/assets/icon.ico").exists():
        build_cmd = [cmd for cmd in build_cmd if not cmd.startswith("--icon")]
    
    print("빌드 명령어:", " ".join(build_cmd))
    
    try:
        # 빌드 실행
        subprocess.check_call(build_cmd)
        print("✅ 빌드 완료!")
        print("실행 파일 위치: dist/Capfit.exe (Windows) 또는 dist/Capfit (macOS/Linux)")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 빌드 실패: {e}")
        return False
    
    return True


def build_web():
    """웹 버전 빌드 (Docker 이미지 등)"""
    print("웹 버전 빌드는 별도로 Docker를 사용하거나 직접 실행하세요.")
    print("실행 명령어: capfit-web")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        build_web()
    else:
        build_desktop()
