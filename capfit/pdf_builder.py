from __future__ import annotations
from typing import List, Optional, Tuple
from PIL import Image
import os


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


def _fit_to_width(img: Image.Image, target_w: int) -> Image.Image:
    if img.width == target_w:
        return img
    scale = target_w / img.width
    new_h = max(1, int(round(img.height * scale)))
    return img.resize((target_w, new_h), Image.LANCZOS)


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
    y_left = 0
    y_right = 0

    def paste_in_column(dst: Image.Image, src: Image.Image, x: int, y: int) -> None:
        # 이미 컬럼 폭에 맞게 준비된 이미지를 그대로 붙임
        dst.paste(src, (x, margin + y))

    for im in imgs:
        # 미리 리사이즈하여 높이 계산 (폭이 이미 동일하면 원본 반환)
        fitted = _fit_to_width(im, col_w)
        h = fitted.height

        # 더 낮은 쪽 컬럼에 우선 배치하여 두 컬럼을 균형 있게 사용
        place_left_first = y_left <= y_right
        placed = False
        for _ in range(2):
            if place_left_first:
                if y_left + h <= usable_h:
                    paste_in_column(page, fitted, margin, y_left)
                    y_left += h
                    placed = True
                    break
                # 왼쪽에 안 들어가면 오른쪽 시도
                place_left_first = False
            else:
                if y_right + h <= usable_h:
                    paste_in_column(page, fitted, margin + col_w + gutter, y_right)
                    y_right += h
                    placed = True
                    break
                # 오른쪽에 안 들어가면 왼쪽 시도
                place_left_first = True

        if not placed:
            # 둘 다 안 들어가면 새 페이지 시작하고 왼쪽부터 배치
            pages.append(page)
            page = Image.new("RGB", (page_w, page_h), (255, 255, 255))
            y_left = 0
            y_right = 0
            paste_in_column(page, fitted, margin, y_left)
            y_left += h

    # 마지막 페이지 추가
    pages.append(page)

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
