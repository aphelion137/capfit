"""
데스크톱 버전 실행 파일 빌드 스크립트
PyInstaller를 사용하여 독립 실행 파일 생성 (웹 서버 + 브라우저 방식)
"""

import os
import sys
import subprocess
from pathlib import Path


def build_desktop():
    """데스크톱 버전 빌드 (웹 서버 + 브라우저 방식)"""
    print("Capfit 데스크톱 버전 빌드 시작...")
    print("(웹 서버 + 브라우저 자동 실행 방식)")
    
    # PyInstaller 설치 확인
    try:
        import PyInstaller
        print(f"PyInstaller 버전: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller가 설치되지 않았습니다. 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller>=5.0.0"])
    
    # 빌드 명령어 구성 (웹 서버 방식에 최적화)
    build_cmd = [
        "pyinstaller",
        "--onefile",  # 단일 실행 파일로 생성
        "--console",  # 콘솔 창 표시 (웹 서버 로그 확인용)
        "--name=Capfit",
        "--icon=desktop/assets/icon.ico",  # 아이콘 파일 (있는 경우)
        # 웹 서버 관련 모듈 포함 (macOS/Linux용 구문)
        "--add-data=shared:shared",
        "--add-data=web:web",
        # FastAPI 및 웹 서버 의존성
        "--hidden-import=fastapi",
        "--hidden-import=uvicorn",
        "--hidden-import=uvicorn.lifespan",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.websockets",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.loops.asyncio",
        "--hidden-import=uvicorn.loops.uvloop",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.config",
        "--hidden-import=uvicorn.main",
        "--hidden-import=uvicorn.server",
        # Jinja2 템플릿 엔진
        "--hidden-import=jinja2",
        "--hidden-import=jinja2.ext",
        # 이미지 처리
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        "--hidden-import=numpy",
        # 웹 브라우저 제어
        "--hidden-import=webbrowser",
        # 네트워킹
        "--hidden-import=socket",
        "--hidden-import=requests",
        # 기타 의존성
        "--hidden-import=typer",
        "--hidden-import=click",
        "--hidden-import=rich",
        "--hidden-import=starlette",
        "--hidden-import=pydantic",
        "--hidden-import=python_multipart",
        # 웹 서버 메인 파일
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
        print("\n📱 사용법:")
        print("1. 실행 파일을 더블클릭하거나 명령줄에서 실행")
        print("2. 자동으로 웹 서버가 시작되고 브라우저가 열림")
        print("3. 웹 인터페이스에서 이미지 업로드 및 PDF 변환")
        print("4. Ctrl+C로 종료")
        
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
