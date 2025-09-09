from __future__ import annotations
import os
import uuid
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, Form
import shutil
from typing import List
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..pdf_builder import (
    build_pdf_two_columns_from_source,
    build_pdf_two_columns_from_sources,
    compute_two_column_layout,
)
from .. import __version__ as CAPFIT_VERSION


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
JOBS_DIR = BASE_DIR / "jobs"

app = FastAPI(title="Capfit Web", description="긴 캡처를 A4 세로 2단 PDF로 변환")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "version": CAPFIT_VERSION})


@app.post("/upload")
async def upload(
    request: Request,
    files: List[UploadFile] = File(...),
    dpi: int = Form(300),
    margin: int = Form(60),
    gutter: int = Form(50),
):
    job_id = uuid.uuid4().hex[:12]
    job_dir = JOBS_DIR / job_id
    ensure_dir(job_dir)

    # 저장 경로
    output_path = job_dir / "output.pdf"

    # 업로드 파일 저장 (선택 순서 유지)
    saved_paths: List[str] = []
    for idx, up in enumerate(files, start=1):
        ext = os.path.splitext(up.filename or "upload.png")[1] or ".png"
        input_i = job_dir / f"input_{idx:03d}{ext}"
        # Stream to disk to avoid loading whole file in memory
        with open(input_i, "wb") as f:
            up.file.seek(0)
            shutil.copyfileobj(up.file, f, length=1024 * 1024)
        saved_paths.append(str(input_i))

    # 업로드 후 즉시 변환까지 동기 처리 → 결과 페이지로 리다이렉트(가장 단순/신뢰 경로)
    output_path = job_dir / "output.pdf"
    if len(saved_paths) == 1:
        build_pdf_two_columns_from_source(
            saved_paths[0],
            str(output_path),
            margin=margin,
            gutter=gutter,
            dpi=dpi,
            page_width=None,
            page_height=None,
            fast=False,
        )
    else:
        build_pdf_two_columns_from_sources(
            saved_paths,
            str(output_path),
            margin=margin,
            gutter=gutter,
            dpi=dpi,
            page_width=None,
            page_height=None,
            fast=False,
        )

    return RedirectResponse(url=f"/result/{job_id}", status_code=303)


@app.get("/result/{job_id}", response_class=HTMLResponse)
async def result(request: Request, job_id: str):
    pdf_path = JOBS_DIR / job_id / "output.pdf"
    exists = pdf_path.exists()
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "job_id": job_id,
            "ready": exists,
            "version": CAPFIT_VERSION,
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
