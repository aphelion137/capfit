from __future__ import annotations
import os
import uuid
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, Form, BackgroundTasks
import re
import shutil
from typing import List
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..pdf_builder import (
    build_pdf_two_columns_from_source,
    build_pdf_two_columns_from_sources,
)
from .. import __version__ as CAPFIT_VERSION


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
JOBS_DIR = BASE_DIR / "jobs"

app = FastAPI(title="Capfit Web", description="긴 캡처를 A4 세로 2단 PDF로 변환")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/jobs", StaticFiles(directory=str(JOBS_DIR)), name="jobs")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    base_url = str(request.base_url).rstrip('/')
    page_url = str(request.url)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "version": CAPFIT_VERSION,
            "base_url": base_url,
            "page_url": page_url,
        },
    )


@app.post("/upload")
async def upload(
    request: Request,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    dpi: int = Form(220),
    margin: int = Form(60),
    gutter: int = Form(50),
):
    job_id = uuid.uuid4().hex[:12]
    job_dir = JOBS_DIR / job_id
    ensure_dir(job_dir)

    # 저장 경로
    output_path = job_dir / "output.pdf"

    # 업로드 파일 저장 (기본: 파일명 내 숫자 기준 오름차순 정렬)
    saved_paths: List[str] = []
    def _numeric_key(name: str):
        nums = [int(x) for x in re.findall(r"\d+", name or "")]
        # 숫자가 있는 파일을 우선 정렬, 그 다음 원문자열
        return (0, tuple(nums), (name or "").lower()) if nums else (1, (name or "").lower())

    files_sorted = sorted(list(files), key=lambda u: _numeric_key(getattr(u, "filename", "")))

    for idx, up in enumerate(files_sorted, start=1):
        ext = os.path.splitext(up.filename or "upload.png")[1] or ".png"
        input_i = job_dir / f"input_{idx:03d}{ext}"
        # Stream to disk to avoid loading whole file in memory
        with open(input_i, "wb") as f:
            up.file.seek(0)
            shutil.copyfileobj(up.file, f, length=1024 * 1024)
        saved_paths.append(str(input_i))

    # 리뷰 페이지로 이동하여 사용자가 순서 확인/조정 후 변환하도록
    safe_dpi = max(1, min(int(dpi), 220))
    return RedirectResponse(url=f"/review/{job_id}?dpi={safe_dpi}&margin={int(margin)}&gutter={int(gutter)}", status_code=303)


@app.get("/review/{job_id}", response_class=HTMLResponse)
async def review(request: Request, job_id: str, dpi: int = 220, margin: int = 60, gutter: int = 50):
    job_dir = JOBS_DIR / job_id
    if not job_dir.exists():
        return HTMLResponse("잘못된 작업입니다.", status_code=404)
    files = sorted([p.name for p in job_dir.iterdir() if p.name.startswith("input_")])
    base_url = str(request.base_url).rstrip('/')
    page_url = str(request.url)
    return templates.TemplateResponse(
        "review.html",
        {
            "request": request,
            "job_id": job_id,
            "files": files,
            "dpi": max(1, min(int(dpi), 220)),
            "margin": int(margin),
            "gutter": int(gutter),
            "version": CAPFIT_VERSION,
            "base_url": base_url,
            "page_url": page_url,
        },
    )


@app.post("/convert/{job_id}")
async def convert(background_tasks: BackgroundTasks, job_id: str, order: str = Form(""), dpi: int = Form(220), margin: int = Form(60), gutter: int = Form(50)):
    job_dir = JOBS_DIR / job_id
    if not job_dir.exists():
        return HTMLResponse("유효하지 않은 작업 ID입니다.", status_code=404)
    all_files = sorted([p for p in job_dir.iterdir() if p.is_file() and p.name.startswith("input_")])
    name_to_path = {p.name: str(p) for p in all_files}
    ordered: List[str] = []
    if order:
        for name in [s for s in order.split(',') if s]:
            if name in name_to_path:
                ordered.append(name_to_path[name])
    # 누락분은 뒤에 추가
    remain = [str(p) for p in all_files if str(p) not in ordered and p.name not in set(order.split(','))]
    saved_paths = ordered + remain

    output_path = job_dir / "output.pdf"
    safe_dpi = max(1, min(int(dpi), 220))

    def _convert(paths: List[str]) -> None:
        if len(paths) == 1:
            build_pdf_two_columns_from_source(
                paths[0],
                str(output_path),
                margin=margin,
                gutter=gutter,
                dpi=safe_dpi,
                page_width=None,
                page_height=None,
                fast=False,
            )
        else:
            build_pdf_two_columns_from_sources(
                paths,
                str(output_path),
                margin=margin,
                gutter=gutter,
                dpi=safe_dpi,
                page_width=None,
                page_height=None,
                fast=False,
            )

    background_tasks.add_task(_convert, saved_paths)
    return RedirectResponse(url=f"/result/{job_id}", status_code=303)


@app.get("/result/{job_id}", response_class=HTMLResponse)
async def result(request: Request, job_id: str):
    pdf_path = JOBS_DIR / job_id / "output.pdf"
    exists = pdf_path.exists()
    base_url = str(request.base_url).rstrip('/')
    page_url = str(request.url)
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "job_id": job_id,
            "ready": exists,
            "version": CAPFIT_VERSION,
            "base_url": base_url,
            "page_url": page_url,
        },
    )


@app.get("/download/{job_id}")
async def download(job_id: str):
    pdf_path = JOBS_DIR / job_id / "output.pdf"
    if not pdf_path.exists():
        return HTMLResponse("변환된 PDF가 없습니다.", status_code=404)
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"capfit_{job_id}.pdf",
    )


def main() -> None:
    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("capfit.web.server:app", host=host, port=port, reload=False)


@app.get("/og.png")
def og_image():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        # 최소한의 1x1 PNG 투명 이미지 반환 (Pillow 미설치 대비)
        return Response(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc``\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82",
            media_type="image/png",
        )

    W, H = 1200, 630
    bg = (12, 17, 24)
    fg = (234, 241, 251)
    muted = (170, 183, 199)
    accent = (74, 144, 226)
    im = Image.new("RGB", (W, H), bg)
    dr = ImageDraw.Draw(im)
    # frame
    dr.rounded_rectangle((60, 60, W - 60, H - 120), radius=28, outline=accent, width=6)
    # texts
    try:
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 72)
        font_sm = ImageFont.truetype("DejaVuSans.ttf", 36)
    except Exception:
        font_big = ImageFont.load_default()
        font_sm = ImageFont.load_default()
    dr.text((100, 120), "CAPFIT", fill=fg, font=font_big)
    dr.text((100, 220), "긴 캡처 → 신뢰 있게 2단 PDF", fill=muted, font=font_sm)

    from io import BytesIO
    buf = BytesIO()
    im.save(buf, format="PNG")
    return Response(buf.getvalue(), media_type="image/png")
