from __future__ import annotations
import math
from typing import List, Tuple
from PIL import Image
import numpy as np
import os

from .utils import open_rgb, to_gray, ensure_dir, save_images


def _smart_cut_yband(img_gray: np.ndarray, y_start: int, y_end: int, search_band: int = 60) -> int:
    """
    y_end 근처에서 에지/변화가 적은 가로줄을 찾아 그 줄에서 절단.
    너무 위에서 자르는 것 방지를 위해 최소 길이 가드 포함.
    """
    H, W = img_gray.shape
    lo = max(0, y_end - search_band)
    hi = min(H - 1, y_end + search_band)

    band = img_gray[lo:hi + 1, :]
    # 간단한 '라인 복잡도' 지표: 가로 방향 1차 차분 절댓값의 합
    diff = np.abs(np.diff(band, axis=1))
    line_energy = diff.sum(axis=1)
    idx = int(np.argmin(line_energy))
    y_cut = lo + idx

    # 최소 길이 확보(너무 위로 끌려 올라가는 것 방지)
    min_y = y_start + int((y_end - y_start) * 0.5)
    if y_cut < min_y:
        y_cut = min_y
    return y_cut


def split_image(
    input_path: str,
    outdir: str = "out",
    column_width: int = 1000,
    column_height: int = 1400,
    overlap: int = 40,
    smart_cut: bool = True,
    smart_band: int = 60,
) -> list[str]:
    """
    긴 세로 이미지를 '한 칼럼 폭/높이' 기준으로 자동 분할하여 PNG로 저장, 경로 리스트 반환.
    - column_width: 칼럼 폭(px) 기준으로 리사이즈 후 분할
    - column_height: 한 조각의 목표 세로(px)
    - overlap: 조각 간 겹침(px) (문맥 이어짐용)
    - smart_cut: 경계 근처에서 줄 중간이 덜 잘리는 지점 탐색
    """
    ensure_dir(outdir)
    base = os.path.splitext(os.path.basename(input_path))[0]

    img = open_rgb(input_path)
    w, h = img.size

    # 가로 기준 스케일 → column_width에 맞춤
    scale = column_width / w
    new_h = int(round(h * scale))
    img = img.resize((column_width, new_h), Image.LANCZOS)
    w, h = img.size

    img_gray = to_gray(img) if smart_cut else None

    parts: List[Image.Image] = []
    y = 0
    while y < h:
        y_target_end = min(y + column_height, h)
        if smart_cut and y_target_end < h:
            y_cut = _smart_cut_yband(img_gray, y, y_target_end, search_band=smart_band)  # type: ignore
        else:
            y_cut = y_target_end

        crop = img.crop((0, y, w, y_cut))
        parts.append(crop)

        nxt = y_cut - overlap
        y = nxt if nxt > y else y_cut
        if y >= h:
            break

    saved = save_images(parts, outdir, base, ext=".png")
    return saved