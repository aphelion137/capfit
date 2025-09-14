"""
Capfit 데스크톱 애플리케이션 메인 진입점
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from desktop.gui.main_window import MainWindow


def main():
    """데스크톱 애플리케이션 메인 함수"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"애플리케이션 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
