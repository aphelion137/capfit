from __future__ import annotations
from PIL import Image
import numpy as np
import os
from typing import List


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def open_rgb(path: str) -> Image.Image:
    """이미지를 RGB로 열기 (일부 PNG의 팔레트/투명 채널 이슈 방지)."""
    return Image.open(path).convert("RGB")


def to_gray(img: Image.Image) -> np.ndarray:
    """Pillow 이미지를 그레이스케일 numpy(uint8)로 변환."""
    return np.array(img.convert("L"))


def save_images(imgs: List[Image.Image], outdir: str, base: str, ext: str = ".png") -> list[str]:
    """[img1, img2, ...]를 outdir에 base_partXX.ext로 저장하고 경로 리스트 반환."""
    ensure_dir(outdir)
    pad = max(2, len(str(max(1, len(imgs)))))
    paths = []
    for i, p in enumerate(imgs, start=1):
        outname = f"{base}_part{str(i).zfill(pad)}{ext}"
        outpath = os.path.join(outdir, outname)
        p.save(outpath, optimize=True)
        paths.append(outpath)
    return paths