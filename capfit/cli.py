from __future__ import annotations
import typer
from pathlib import Path

from .splitter import split_image
from .pdf_builder import build_pdf_two_columns, build_pdf_one_per_page, compute_two_column_layout

app = typer.Typer(help="capfit: 긴 캡처를 두 칼럼/페이지에 맞춰 자동 분할하고 PDF까지 생성합니다.")


@app.command()
def run(
    input: str = typer.Option(..., "--input", "-i", help="세로로 긴 캡처 이미지 경로 (PNG/JPG 등)"),
    outdir: str = typer.Option("out", "--outdir", "-o", help="조각 PNG 저장 폴더"),
    column_width: int = typer.Option(1000, help="한 칼럼 폭(px)"),
    column_height: int = typer.Option(1400, help="한 칼럼 높이(px)"),
    overlap: int = typer.Option(40, help="조각 간 겹침(px)"),
    smart_cut: bool = typer.Option(True, help="경계 근처에서 줄을 덜 자르는 스마트 컷"),
    smart_band: int = typer.Option(60, help="스마트 컷 탐색 범위(px)"),
    make_pdf: bool = typer.Option(True, help="PDF도 함께 생성"),
    pdf_mode: str = typer.Option("two_columns", help="'two_columns' 또는 'one_per_page'"),
    pdf_path: str = typer.Option("", help="PDF 저장 경로(미지정 시 out/<입력이름>.pdf)"),
    margin: int = typer.Option(60, help="PDF 페이지 여백(px)"),
    gutter: int = typer.Option(50, help="2단 사이 간격(px) - two_columns 모드에서만 사용"),
    dpi: int = typer.Option(300, help="PDF 메타 DPI 및 페이지 픽셀 계산 기준"),
    page_width: int = typer.Option(0, help="PDF 페이지 가로(px). 0이면 A4 세로(DPI 기준)"),
    page_height: int = typer.Option(0, help="PDF 페이지 세로(px). 0이면 A4 세로(DPI 기준)"),
    optimize_slices: bool = typer.Option(True, help="PDF 2단에 맞춰 분할 폭/높이 자동 최적화"),
):
    """긴 캡처 → PNG 조각 + (옵션) PDF 생성."""
    # 2단 PDF를 생성할 경우, 불필요한 리사이즈/붙이기 최소화를 위해
    # 분할 폭/높이를 페이지 레이아웃에 맞춰 최적화
    eff_column_width = column_width
    eff_column_height = column_height
    if make_pdf and pdf_mode == "two_columns" and optimize_slices:
        _, _, col_w, usable_h = compute_two_column_layout(
            dpi=dpi,
            margin=margin,
            gutter=gutter,
            page_width=(page_width or None),
            page_height=(page_height or None),
        )
        eff_column_width = col_w
        # 두 컬럼 모두에 최소 1개 이상 들어가도록, 한 조각의 목표 높이를
        # 페이지 유효 높이의 절반으로 제한
        eff_column_height = max(1, min(column_height, usable_h // 2))

    paths = split_image(
        input_path=input,
        outdir=outdir,
        column_width=eff_column_width,
        column_height=eff_column_height,
        overlap=overlap,
        smart_cut=smart_cut,
        smart_band=smart_band,
    )
    typer.echo(f"[PNG saved] {len(paths)} files")

    if make_pdf:
        base = Path(input).stem
        pdf_file = pdf_path or str(Path(outdir) / f"{base}.pdf")
        if pdf_mode == "two_columns":
            pw = page_width or None
            ph = page_height or None
            out_pdf = build_pdf_two_columns(
                paths,
                pdf_file,
                margin=margin,
                gutter=gutter,
                dpi=dpi,
                page_width=pw,
                page_height=ph,
            )
        elif pdf_mode == "one_per_page":
            out_pdf = build_pdf_one_per_page(paths, pdf_file, margin=margin, dpi=dpi)
        else:
            raise typer.BadParameter("pdf_mode must be 'two_columns' or 'one_per_page'.")
        typer.echo(f"[PDF saved] {out_pdf}")
        typer.echo("✅ Done!")
    else:
        typer.echo("✅ Done! (PDF skipped)")


if __name__ == "__main__":
    app()
