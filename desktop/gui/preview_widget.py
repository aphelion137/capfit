"""
레이아웃 미리보기 위젯
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class PreviewWidget(ttk.Frame):
    """PDF 레이아웃 미리보기 위젯"""
    
    def __init__(self, parent, settings: Dict[str, Any]):
        super().__init__(parent)
        self.settings = settings.copy()
        
        self._setup_ui()
        self._update_preview()
    
    def _setup_ui(self):
        """UI 구성"""
        # 캔버스 생성
        self.canvas = tk.Canvas(self, width=300, height=400, bg="white", relief="sunken", bd=1)
        self.canvas.pack(pady=10)
        
        # 범례
        legend_frame = ttk.Frame(self)
        legend_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 여백 범례
        margin_frame = ttk.Frame(legend_frame)
        margin_frame.pack(side=tk.LEFT, padx=(0, 20))
        margin_color = tk.Frame(margin_frame, width=20, height=15, bg="#f0f0f0")
        margin_color.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(margin_frame, text="여백").pack(side=tk.LEFT)
        
        # 거터 범례
        gutter_frame = ttk.Frame(legend_frame)
        gutter_frame.pack(side=tk.LEFT, padx=(0, 20))
        gutter_color = tk.Frame(gutter_frame, width=20, height=15, bg="#e0e0e0")
        gutter_color.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(gutter_frame, text="거터").pack(side=tk.LEFT)
        
        # 콘텐츠 범례
        content_frame = ttk.Frame(legend_frame)
        content_frame.pack(side=tk.LEFT)
        content_color = tk.Frame(content_frame, width=20, height=15, bg="#d0d0d0")
        content_color.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(content_frame, text="콘텐츠").pack(side=tk.LEFT)
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """설정 업데이트 및 미리보기 갱신"""
        self.settings.update(new_settings)
        self._update_preview()
    
    def _update_preview(self):
        """미리보기 업데이트"""
        self.canvas.delete("all")
        
        # 캔버스 크기
        canvas_width = 300
        canvas_height = 400
        
        # A4 비율 계산 (세로가 더 긴 비율)
        a4_ratio = 11.69 / 8.27  # A4 세로/가로 비율
        
        # 페이지 크기 계산 (캔버스에 맞게 스케일링)
        if canvas_width / canvas_height > 1 / a4_ratio:
            # 캔버스가 너무 넓음 - 높이 기준으로 스케일링
            page_height = canvas_height - 40  # 여백
            page_width = int(page_height / a4_ratio)
        else:
            # 캔버스가 너무 높음 - 너비 기준으로 스케일링
            page_width = canvas_width - 40  # 여백
            page_height = int(page_width * a4_ratio)
        
        # 페이지 위치 (중앙)
        page_x = (canvas_width - page_width) // 2
        page_y = (canvas_height - page_height) // 2
        
        # 페이지 배경
        self.canvas.create_rectangle(
            page_x, page_y, page_x + page_width, page_y + page_height,
            fill="white", outline="black", width=2
        )
        
        # 설정값 가져오기
        margin = self.settings.get("margin", 60)
        gutter = self.settings.get("gutter", 50)
        dpi = self.settings.get("dpi", 220)
        pdf_mode = self.settings.get("pdf_mode", "two_columns")
        
        # 실제 픽셀을 미리보기 픽셀로 스케일링
        scale_factor = page_width / (8.27 * dpi)  # A4 가로 기준 스케일링
        
        margin_px = int(margin * scale_factor)
        gutter_px = int(gutter * scale_factor)
        
        if pdf_mode == "two_columns":
            # 2단 레이아웃
            col_width = (page_width - 2 * margin_px - gutter_px) // 2
            
            # 왼쪽 칼럼
            left_x = page_x + margin_px
            left_y = page_y + margin_px
            self.canvas.create_rectangle(
                left_x, left_y, left_x + col_width, page_y + page_height - margin_px,
                fill="#d0d0d0", outline="gray", width=1
            )
            
            # 오른쪽 칼럼
            right_x = left_x + col_width + gutter_px
            right_y = page_y + margin_px
            self.canvas.create_rectangle(
                right_x, right_y, right_x + col_width, page_y + page_height - margin_px,
                fill="#d0d0d0", outline="gray", width=1
            )
            
            # 거터 표시
            if gutter_px > 0:
                self.canvas.create_rectangle(
                    left_x + col_width, left_y, right_x, page_y + page_height - margin_px,
                    fill="#e0e0e0", outline="gray", width=1
                )
            
            # 여백 표시
            # 상단 여백
            self.canvas.create_rectangle(
                page_x, page_y, page_x + page_width, left_y,
                fill="#f0f0f0", outline="", width=0
            )
            # 하단 여백
            self.canvas.create_rectangle(
                page_x, page_y + page_height - margin_px, page_x + page_width, page_y + page_height,
                fill="#f0f0f0", outline="", width=0
            )
            # 좌측 여백
            self.canvas.create_rectangle(
                page_x, left_y, left_x, page_y + page_height - margin_px,
                fill="#f0f0f0", outline="", width=0
            )
            # 우측 여백
            self.canvas.create_rectangle(
                right_x + col_width, left_y, page_x + page_width, page_y + page_height - margin_px,
                fill="#f0f0f0", outline="", width=0
            )
            
        else:
            # 1페이지당 1이미지 레이아웃
            content_x = page_x + margin_px
            content_y = page_y + margin_px
            content_width = page_width - 2 * margin_px
            content_height = page_height - 2 * margin_px
            
            self.canvas.create_rectangle(
                content_x, content_y, content_x + content_width, content_y + content_height,
                fill="#d0d0d0", outline="gray", width=1
            )
            
            # 여백 표시
            # 상단 여백
            self.canvas.create_rectangle(
                page_x, page_y, page_x + page_width, content_y,
                fill="#f0f0f0", outline="", width=0
            )
            # 하단 여백
            self.canvas.create_rectangle(
                page_x, content_y + content_height, page_x + page_width, page_y + page_height,
                fill="#f0f0f0", outline="", width=0
            )
            # 좌측 여백
            self.canvas.create_rectangle(
                page_x, content_y, content_x, content_y + content_height,
                fill="#f0f0f0", outline="", width=0
            )
            # 우측 여백
            self.canvas.create_rectangle(
                content_x + content_width, content_y, page_x + page_width, content_y + content_height,
                fill="#f0f0f0", outline="", width=0
            )
        
        # 정보 텍스트
        info_text = f"DPI: {dpi}\n여백: {margin}px\n거터: {gutter}px"
        if pdf_mode == "two_columns":
            info_text += "\n2단 레이아웃"
        else:
            info_text += "\n1페이지당 1이미지"
        
        self.canvas.create_text(
            page_x + page_width + 10, page_y + 20,
            text=info_text, anchor="nw", font=("Arial", 9)
        )
