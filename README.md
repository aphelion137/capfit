# capfit

긴 캡처 이미지를 **한글(HWP) 2단**에 맞게 자동 분할하고, **2단 PDF**까지 한 번에 생성하는 툴.

## Install (권장: Conda 환경)
```bash
conda create -n capfit python=3.12 -y
conda activate capfit
pip install .
```

## Usage
```bash
capfit run --input "examples/test.jpeg" \
  --outdir "out" --column-width 1000 --column-height 1400 \
  --overlap 40 --smart-cut \
  --make-pdf --pdf-mode two_columns --margin 60 --gutter 50 --dpi 300
```
