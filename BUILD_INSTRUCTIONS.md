# Capfit EXE 빌드 가이드

## 📋 개요

Capfit 데스크톱 버전을 독립 실행 파일(EXE)로 빌드하는 방법을 안내합니다.

## 🛠️ 빌드 환경 요구사항

### 필수 소프트웨어
- **Python 3.12+** (conda 환경 권장)
- **PyInstaller 6.16.0+**
- **모든 프로젝트 의존성** (requirements.txt에 명시된 패키지들)

### 설치된 패키지 확인
```bash
# 현재 환경에서 필요한 패키지들이 설치되어 있는지 확인
pip list | grep -E "(fastapi|uvicorn|pillow|numpy|typer|requests)"
```

## 🚀 빌드 방법

### 1. 환경 준비
```bash
# 프로젝트 디렉토리로 이동
cd /path/to/capfit

# conda 환경 활성화 (권장)
conda activate capfit

# 또는 가상환경 활성화
# source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate     # Windows
```

### 2. 의존성 설치
```bash
# 프로젝트 의존성 설치
pip install -e .

# PyInstaller 설치 (자동으로 설치됨)
pip install pyinstaller>=6.16.0
```

### 3. 빌드 실행
```bash
# 자동 빌드 스크립트 실행
python build_desktop.py
```

### 4. 수동 빌드 (고급 사용자)
```bash
# PyInstaller 직접 실행
pyinstaller \
  --onefile \
  --console \
  --name=Capfit \
  --add-data=shared:shared \
  --add-data=web:web \
  --hidden-import=fastapi \
  --hidden-import=uvicorn \
  --hidden-import=jinja2 \
  --hidden-import=PIL \
  --hidden-import=numpy \
  --hidden-import=webbrowser \
  --hidden-import=socket \
  --hidden-import=requests \
  --hidden-import=typer \
  --hidden-import=click \
  --hidden-import=rich \
  --hidden-import=starlette \
  --hidden-import=pydantic \
  --hidden-import=python_multipart \
  desktop/main.py
```

## 📁 빌드 결과

### 생성되는 파일들
```
dist/
├── Capfit          # macOS/Linux 실행 파일
└── Capfit.exe      # Windows 실행 파일 (Windows에서 빌드 시)

build/              # 빌드 임시 파일들 (삭제 가능)
├── Capfit/
└── ...

Capfit.spec         # PyInstaller 설정 파일
```

### 파일 크기
- **macOS**: 약 192MB
- **Windows**: 약 200MB (예상)

## 🎯 사용법

### 실행 방법
1. **더블클릭**: `dist/Capfit` (또는 `dist/Capfit.exe`) 파일을 더블클릭
2. **명령줄**: `./dist/Capfit` (macOS/Linux) 또는 `dist\Capfit.exe` (Windows)

### 실행 과정
1. 🚀 **자동 시작**: 웹 서버가 자동으로 시작됩니다
2. 🌐 **브라우저 열기**: 기본 브라우저에서 애플리케이션이 열립니다
3. 📱 **웹 인터페이스**: 웹 버전과 동일한 기능을 사용할 수 있습니다
4. 🛑 **종료**: `Ctrl+C`로 애플리케이션을 종료합니다

## 🔧 문제 해결

### 빌드 오류
```bash
# PyInstaller 재설치
pip uninstall pyinstaller
pip install pyinstaller>=6.16.0

# 캐시 정리
rm -rf build/ dist/ *.spec
python build_desktop.py
```

### 실행 오류
```bash
# 권한 확인 (macOS/Linux)
chmod +x dist/Capfit

# 의존성 확인
ldd dist/Capfit  # Linux
otool -L dist/Capfit  # macOS
```

### 포트 충돌
- 애플리케이션이 자동으로 사용 가능한 포트를 찾습니다
- 8000-8099, 9000-9099 범위에서 포트를 검색합니다

## 📦 배포 방법

### 단일 파일 배포
```bash
# 실행 파일만 복사
cp dist/Capfit /path/to/distribution/
```

### 압축 배포
```bash
# macOS/Linux
tar -czf capfit-desktop.tar.gz dist/Capfit

# Windows
zip capfit-desktop.zip dist/Capfit.exe
```

## 🎨 커스터마이징

### 아이콘 변경
1. `desktop/assets/icon.ico` 파일을 원하는 아이콘으로 교체
2. 빌드 스크립트에서 아이콘 경로 확인

### 이름 변경
```bash
# 빌드 스크립트에서 --name 옵션 수정
--name=MyCapfit
```

## 📋 체크리스트

빌드 전 확인사항:
- [ ] Python 3.12+ 설치됨
- [ ] 모든 의존성 설치됨 (`pip install -e .`)
- [ ] PyInstaller 설치됨
- [ ] 프로젝트 디렉토리에서 실행
- [ ] 충분한 디스크 공간 (최소 500MB)

빌드 후 확인사항:
- [ ] `dist/` 폴더에 실행 파일 생성됨
- [ ] 실행 파일이 정상 작동함
- [ ] 웹 서버가 자동으로 시작됨
- [ ] 브라우저가 자동으로 열림
- [ ] 모든 기능이 정상 작동함

## 🆘 지원

문제가 발생하면:
1. **로그 확인**: 콘솔 출력에서 오류 메시지 확인
2. **의존성 확인**: `pip list`로 필요한 패키지 설치 여부 확인
3. **환경 확인**: Python 버전과 가상환경 상태 확인
4. **재빌드**: 캐시를 정리하고 다시 빌드 시도

---

**참고**: 이 가이드는 macOS 환경에서 작성되었습니다. Windows 환경에서는 일부 명령어가 다를 수 있습니다.
