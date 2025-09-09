from __future__ import annotations
from typing import List, Optional, Tuple
from PIL import Image
import os
import numpy as np


def _load_images(paths: List[str]) -> List[Image.Image]:
    imgs: List[Image.Image] = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        imgs.append(im)
    return imgs


def _a4_page_size(dpi: int) -> Tuple[int, int]:
    # A4 portrait in inches: 8.27 x 11.69
    w = int(round(8.27 * dpi))
    h = int(round(11.69 * dpi))
    return w, h


def _get_resample(fast: bool) -> int:
    return Image.BILINEAR if fast else Image.LANCZOS


def _fit_to_width(img: Image.Image, target_w: int, *, fast: bool = False) -> Image.Image:
    if img.width == target_w:
        return img
    scale = target_w / img.width
    new_h = max(1, int(round(img.height * scale)))
    return img.resize((target_w, new_h), _get_resample(fast))


def compute_two_column_layout(
    *,
    dpi: int,
    margin: int,
    gutter: int,
    page_width: Optional[int] = None,
    page_height: Optional[int] = None,
) -> Tuple[int, int, int, int]:
    """2단 레이아웃 메트릭 계산.

    반환: (page_w, page_h, col_w, usable_h)
    """
    if not page_width or not page_height:
        page_w, page_h = _a4_page_size(dpi)
    else:
        page_w, page_h = page_width, page_height

    # 세로 보장
    if page_w > page_h:
        page_w, page_h = page_h, page_w

    usable_w = page_w - margin * 2
    usable_h = page_h - margin * 2
    col_w = max(1, int((usable_w - gutter) // 2))
    return page_w, page_h, col_w, usable_h


def build_pdf_two_columns(
    image_paths: List[str],
    out_pdf: str,
    *,
    margin: int = 60,
    gutter: int = 50,
    dpi: int = 300,
    page_width: Optional[int] = None,
    page_height: Optional[int] = None,
    fast: bool = False,
) -> str:
    """세로(포트레이트) 페이지를 가로로 반 나눈 2단 레이아웃으로 PDF 생성.

    - 페이지 크기: 명시 없으면 A4 포트레이트(dpi 기준 픽셀)
    - 칼럼 폭: (페이지폭 - 좌우여백 - 거터) / 2
    - 이미지는 칼럼 폭에 맞춰 비율 유지 리사이즈 후 위→아래로 채움
    - 왼쪽 칼럼이 차면 오른쪽, 둘 다 꽉 차면 새 페이지
    """
    if not image_paths:
        raise ValueError("No images to build PDF.")

    imgs = _load_images(image_paths)
    page_w, page_h, col_w, usable_h = compute_two_column_layout(
        dpi=dpi, margin=margin, gutter=gutter,
        page_width=page_width, page_height=page_height,
    )

    pages: List[Image.Image] = []
    page = Image.new("RGB", (page_w, page_h), (255, 255, 255))

    def paste_in_column(dst: Image.Image, src: Image.Image, x: int, y: int) -> None:
        dst.paste(src, (x, margin + y))

    # 페이지 단위 버퍼링으로 순서 보존 + 양 칼럼 사용 보장 시도
    left_buf: List[Image.Image] = []
    right_buf: List[Image.Image] = []
    y_left = 0
    y_right = 0

    def flush_page():
        nonlocal page, left_buf, right_buf, y_left, y_right
        # 오른쪽이 비어 있고 왼쪽에 요소가 2개 이상이면, 좌측의 뒤에서부터 일부를 오른쪽으로 이동
        if not right_buf and len(left_buf) >= 2:
            moved: List[Image.Image] = []
            ry = 0
            # 뒤에서부터 꺼내되, 오른쪽 유효 높이 안에서 가능한 만큼만
            for im in reversed(left_buf):
                h = im.height
                if ry + h <= usable_h:
                    moved.append(im)
                    ry += h
                else:
                    break
            # 최소 1개만이라도 이동
            if moved:
                k = len(moved)
                left_buf = left_buf[: len(left_buf) - k]
                right_buf = list(reversed(moved))

        # 실제 렌더링
        y = 0
        for im in left_buf:
            paste_in_column(page, im, margin, y)
            y += im.height
        y = 0
        for im in right_buf:
            paste_in_column(page, im, margin + col_w + gutter, y)
            y += im.height

        pages.append(page)
        page = Image.new("RGB", (page_w, page_h), (255, 255, 255))
        left_buf = []
        right_buf = []
        y_left = 0
        y_right = 0

    for im in imgs:
        fitted = _fit_to_width(im, col_w, fast=fast)
        h = fitted.height

        # 왼쪽부터 채우고 넘치면 오른쪽, 둘 다 넘치면 페이지 플러시
        if y_left + h <= usable_h:
            left_buf.append(fitted)
            y_left += h
        elif y_right + h <= usable_h:
            right_buf.append(fitted)
            y_right += h
        else:
            flush_page()
            left_buf.append(fitted)
            y_left += h

    # 마지막 페이지 렌더링
    if left_buf or right_buf:
        flush_page()

    # PDF 저장 (Pillow 다중 페이지 PDF)
    first, rest = pages[0], pages[1:]
    os.makedirs(os.path.dirname(out_pdf) or ".", exist_ok=True)
    first.save(out_pdf, save_all=True, append_images=rest, resolution=dpi)
    return out_pdf


def build_pdf_one_per_page(
    image_paths: List[str],
    out_pdf: str,
    *,
    margin: int = 60,
    dpi: int = 300,
) -> str:
    """각 이미지를 한 페이지에 하나씩 배치하여 PDF 생성."""
    if not image_paths:
        raise ValueError("No images to build PDF.")

    imgs = _load_images(image_paths)
    pages: List[Image.Image] = []
    for im in imgs:
        page_w = im.width + margin * 2
        page_h = im.height + margin * 2
        page = Image.new("RGB", (page_w, page_h), (255, 255, 255))
        page.paste(im, (margin, margin))
        pages.append(page)

    first, rest = pages[0], pages[1:]
    os.makedirs(os.path.dirname(out_pdf) or ".", exist_ok=True)
    first.save(out_pdf, save_all=True, append_images=rest, resolution=dpi)
    return out_pdf


def build_pdf_two_columns_from_source(
    input_path: str,
    out_pdf: str,
    *,
    margin: int = 60,
    gutter: int = 50,
    dpi: int = 300,
    page_width: Optional[int] = None,
    page_height: Optional[int] = None,
    fast: bool = False,
    # 버블 컷 튜닝 파라미터(웹/CLI에서 노출 가능)
    search_band: int = 60,
    bg_strip: int = 12,
    bg_thresh: int = 18,
    bg_ratio_hi: float = 0.85,
    bg_ratio_mid: float = 0.70,
    min_height_ratio: float = 0.60,
    sample_stride: int = 4,
) -> str:
    """원본 긴 이미지를 바로 A4 세로 2단 페이지 단위로 잘라 PDF 생성.

    - 원본을 먼저 칼럼 폭(col_w)에 맞춰 리사이즈
    - 이후 세로로 `usable_h`씩 연속 슬라이스 → [L1,R1], [L2,R2], ... 순으로 페이지 구성
    - 마지막 조각은 남은 만큼만 잘리므로 마지막 페이지의 일부 공백은 자연스럽게 발생할 수 있음
    """
    page_w, page_h, col_w, usable_h = compute_two_column_layout(
        dpi=dpi, margin=margin, gutter=gutter,
        page_width=page_width, page_height=page_height,
    )

    src = Image.open(input_path).convert("RGB")
    # 가로 기준 칼럼 폭으로 리사이즈(업스케일/다운스케일 모두 허용)
    scale = col_w / src.width
    new_h = max(1, int(round(src.height * scale)))
    src = src.resize((col_w, new_h), _get_resample(fast))
    _, H = src.size

    # 스마트 컷 준비(버블 인지 우선, 에지 에너지 보조)
    # 1) 배경 추정: 좌/우 가장자리 샘플의 중앙값을 배경으로 간주
    # 2) 행별 배경 비율(row_bg_ratio) 계산(가로 1/4 샘플링으로 경량화)
    # 3) 행별 에지 에너지(row_energy) 계산(보조 지표)
    # 컷은 우선적으로 높은 배경 비율(버블 사이 공백)을 선택, 없으면 에너지 최소 행을 사용
    src_gray_full = np.array(src.convert("L"))
    # 배경 추정: 좌/우 스트립에서 샘플
    strip = max(2, int(bg_strip))
    left_strip = src_gray_full[:, :strip].reshape(-1)
    right_strip = src_gray_full[:, -strip:].reshape(-1)
    bg_samples = np.concatenate([left_strip, right_strip])
    bg_value = int(np.median(bg_samples))
    # 배경 판정 임계값(명암 무관하게 완화)
    BG_THRESH = max(1, int(bg_thresh))  # ±n 정도까지 배경으로 간주

    # 수평 1/4 샘플링으로 배경 비율 계산(연산량 절감)
    stride = max(1, int(sample_stride))
    sub = src_gray_full[:, ::stride]
    # 중앙부의 큰 사진/스티커 영향 완화를 위해: 좌/우 25% 영역만 사용
    w_sub = sub.shape[1]
    q = max(1, w_sub // 4)
    sub_lr = np.concatenate([sub[:, :q], sub[:, -q:]], axis=1)
    row_bg_mask = (np.abs(sub_lr - bg_value) <= BG_THRESH)
    row_bg_ratio = row_bg_mask.mean(axis=1)  # shape: (H,)

    # 추가 지표: 각 행의 '연속된 배경 구간' 최장 길이(비율)
    def _longest_run_len(mask_row: np.ndarray) -> int:
        m = 0
        c = 0
        for v in mask_row:
            if v:
                c += 1
                if c > m:
                    m = c
            else:
                c = 0
        return m

    H_rows = row_bg_mask.shape[0]
    W_sub = row_bg_mask.shape[1]
    row_bg_run_ratio = np.empty(H_rows, dtype=np.float32)
    for i in range(H_rows):
        row_bg_run_ratio[i] = _longest_run_len(row_bg_mask[i]) / max(1, W_sub)

    # 보조 지표: 행별 에너지(수평+수직 결합)
    row_energy_x = np.abs(np.diff(src_gray_full, axis=1)).sum(axis=1)
    dy = np.abs(np.diff(src_gray_full, axis=0))
    row_energy_y = np.vstack([dy[0:1, :], dy]).sum(axis=1)
    rx = row_energy_x / (row_energy_x.max() + 1e-8)
    ry = row_energy_y / (row_energy_y.max() + 1e-8)
    row_energy = 0.5 * rx + 0.5 * ry

    SEARCH_BAND = max(10, int(search_band))  # 버블 경계 탐색 폭

    def smart_cut(y_start: int, y_end: int) -> int:
        """y_end 바로 위쪽 밴드에서 '버블 사이 공백'을 우선 선택.
        - 1순위: row_bg_ratio가 높은(>=0.85) 행 중 y에 가장 가까운 행
        - 2순위: 배경 비율이 중간(>=0.7)인 행 중 y에 가장 가까운 행
        - 3순위: 에너지 최소 행(기존 방식)
        - 컷은 위로만 이동해 여백을 최소화
        """
        if y_end >= H:
            return min(y_end, H)
        lo = max(0, y_end - SEARCH_BAND)
        hi = min(H - 1, y_end)
        # 최소 높이 가드(현재 조각 높이의 일정 비율 이상 확보)
        min_y = y_start + int((y_end - y_start) * float(min_height_ratio))
        lo = max(lo, min_y)
        if lo >= hi:
            return y_end

        band_bg = row_bg_ratio[lo : hi + 1]
        band_run = row_bg_run_ratio[lo : hi + 1]

        # 1순위: 배경 비율 높고(>=hi), 연속 배경구간도 충분(>=0.8)
        cand_mask = (band_bg >= float(bg_ratio_hi)) & (band_run >= 0.8)
        if cand_mask.any():
            idxs = np.where(cand_mask)[0]
            end = int(idxs[-1])
            start = end
            while start - 1 >= 0 and cand_mask[start - 1]:
                start -= 1
            mid = (start + end) // 2
            return lo + int(mid)

        # 2순위: 배경 비율 중간(>=mid) + 연속 배경구간 완화(>=0.6)
        cand_mask = (band_bg >= float(bg_ratio_mid)) & (band_run >= 0.6)
        if cand_mask.any():
            idxs = np.where(cand_mask)[0]
            end = int(idxs[-1])
            start = end
            while start - 1 >= 0 and cand_mask[start - 1]:
                start -= 1
            mid = (start + end) // 2
            return lo + int(mid)

        # 3순위: 에너지 최소(라인/텍스트 절단 최소화 시도)
        band_energy = row_energy[lo : hi + 1]
        idx = int(np.argmin(band_energy))
        cut = lo + idx
        return max(y_start + 1, cut - 2)

    # 스트리밍 조립: 메모리 고정 사용량, 불필요한 리스트 생성 없음
    pages: List[Image.Image] = []
    page = Image.new("RGB", (page_w, page_h), (255, 255, 255))
    left_slot = True

    y = 0
    while y < H:
        y2 = min(y + usable_h, H)
        # 마지막 조각이 아닌 경우만 스마트 컷 적용
        y_cut = smart_cut(y, y2) if y2 < H else y2
        crop = src.crop((0, y, col_w, y_cut))
        if left_slot:
            page.paste(crop, (margin, margin))
            left_slot = False
        else:
            page.paste(crop, (margin + col_w + gutter, margin))
            pages.append(page)
            page = Image.new("RGB", (page_w, page_h), (255, 255, 255))
            left_slot = True
        y = y_cut

    # 마지막 홀수 조각 처리(왼쪽만 채워진 경우)
    if not left_slot:
        pages.append(page)

    # 저장
    first, rest = pages[0], pages[1:] if len(pages) > 1 else []
    os.makedirs(os.path.dirname(out_pdf) or ".", exist_ok=True)
    first.save(out_pdf, save_all=True, append_images=rest, resolution=dpi)
    return out_pdf
