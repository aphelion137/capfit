# Capfit

긴 캡처 이미지를 **한글(HWP) 2단**에 맞게 자동 분할하고, **2단 PDF**까지 한 번에 생성하는 툴.

## 🚀 버전별 설치 및 사용

### 📱 웹 버전 (권장)
```bash
# 설치
conda create -n capfit python=3.12 -y
conda activate capfit
pip install .

# 실행
capfit-web
# 브라우저에서 http://localhost:8000 접속
```

### 🖥️ 데스크톱 버전 (웹 서버 + 브라우저)
```bash
# 설치
conda create -n capfit python=3.12 -y
conda activate capfit
pip install .

# 실행 (자동으로 웹 서버 시작 + 브라우저 열기)
capfit-desktop
```

### 💻 CLI 버전
```bash
# 설치
conda create -n capfit python=3.12 -y
conda activate capfit
pip install .

# 사용
capfit run --input "examples/test.jpeg" \
  --outdir "out" --column-width 1000 --column-height 1400 \
  --overlap 40 --smart-cut \
  --make-pdf --pdf-mode two_columns --margin 60 --gutter 50 --dpi 300
```

## 📦 실행 파일 빌드

### 데스크톱 실행 파일 생성
```bash
python build_desktop.py
# dist/ 폴더에 독립 실행 파일 생성
# 실행 파일을 더블클릭하면 자동으로 웹 서버가 시작되고 브라우저가 열림
```

## 🏗️ 프로젝트 구조

```
capfit/
├── shared/          # 공통 핵심 로직
│   ├── core/        # 이미지 처리, PDF 생성
│   └── cli/         # CLI 공통 기능
├── web/             # 웹 버전 (FastAPI)
├── desktop/         # 데스크톱 버전 (웹 서버 + 브라우저)
└── cli/             # CLI 버전
```
