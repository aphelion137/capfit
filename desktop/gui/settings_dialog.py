"""
고급 설정 대화상자
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional


class SettingsDialog:
    """고급 설정 대화상자 클래스"""
    
    def __init__(self, parent, current_settings: Dict[str, Any]):
        self.parent = parent
        self.settings = current_settings.copy()
        self.result: Optional[Dict[str, Any]] = None
        
        self._create_dialog()
        self._setup_ui()
        self._load_settings()
    
    def _create_dialog(self):
        """대화상자 생성"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("고급 설정")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 중앙에 배치
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
    
    def _setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(main_frame, text="고급 설정", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 스크롤 가능한 프레임
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 설정 섹션들
        self._create_image_settings(scrollable_frame)
        self._create_pdf_settings(scrollable_frame)
        self._create_smart_cut_settings(scrollable_frame)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="기본값으로 재설정", command=self._reset_defaults).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="취소", command=self._cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="확인", command=self._ok).pack(side=tk.RIGHT)
    
    def _create_image_settings(self, parent):
        """이미지 처리 설정 섹션"""
        frame = ttk.LabelFrame(parent, text="이미지 처리 설정", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # 칼럼 폭
        ttk.Label(frame, text="칼럼 폭 (px):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.column_width_var = tk.IntVar()
        ttk.Spinbox(frame, from_=100, to=2000, textvariable=self.column_width_var, width=15).grid(row=0, column=1, sticky=tk.W)
        
        # 칼럼 높이
        ttk.Label(frame, text="칼럼 높이 (px):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.column_height_var = tk.IntVar()
        ttk.Spinbox(frame, from_=100, to=3000, textvariable=self.column_height_var, width=15).grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # 겹침
        ttk.Label(frame, text="조각 간 겹침 (px):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.overlap_var = tk.IntVar()
        ttk.Spinbox(frame, from_=0, to=200, textvariable=self.overlap_var, width=15).grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        # 스마트 컷
        self.smart_cut_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="스마트 컷 사용", variable=self.smart_cut_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # 스마트 컷 탐색 범위
        ttk.Label(frame, text="스마트 컷 탐색 범위 (px):").grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.smart_band_var = tk.IntVar()
        ttk.Spinbox(frame, from_=10, to=200, textvariable=self.smart_band_var, width=15).grid(row=4, column=1, sticky=tk.W, pady=(5, 0))
    
    def _create_pdf_settings(self, parent):
        """PDF 설정 섹션"""
        frame = ttk.LabelFrame(parent, text="PDF 설정", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # 페이지 크기
        ttk.Label(frame, text="페이지 가로 (px, 0=자동):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.page_width_var = tk.IntVar()
        ttk.Spinbox(frame, from_=0, to=5000, textvariable=self.page_width_var, width=15).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(frame, text="페이지 세로 (px, 0=자동):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.page_height_var = tk.IntVar()
        ttk.Spinbox(frame, from_=0, to=5000, textvariable=self.page_height_var, width=15).grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # 최적화
        self.optimize_slices_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="PDF 2단에 맞춰 분할 크기 자동 최적화", variable=self.optimize_slices_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def _create_smart_cut_settings(self, parent):
        """스마트 컷 고급 설정 섹션"""
        frame = ttk.LabelFrame(parent, text="스마트 컷 고급 설정", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # 배경 스트립
        ttk.Label(frame, text="배경 추정 스트립 (px):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.bg_strip_var = tk.IntVar()
        ttk.Spinbox(frame, from_=2, to=50, textvariable=self.bg_strip_var, width=15).grid(row=0, column=1, sticky=tk.W)
        
        # 배경 임계값
        ttk.Label(frame, text="배경 판정 임계값:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.bg_thresh_var = tk.IntVar()
        ttk.Spinbox(frame, from_=1, to=50, textvariable=self.bg_thresh_var, width=15).grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # 배경 비율 높음
        ttk.Label(frame, text="높은 배경 비율:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.bg_ratio_hi_var = tk.DoubleVar()
        ttk.Spinbox(frame, from_=0.5, to=1.0, increment=0.05, textvariable=self.bg_ratio_hi_var, width=15).grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        # 배경 비율 중간
        ttk.Label(frame, text="중간 배경 비율:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.bg_ratio_mid_var = tk.DoubleVar()
        ttk.Spinbox(frame, from_=0.3, to=0.9, increment=0.05, textvariable=self.bg_ratio_mid_var, width=15).grid(row=3, column=1, sticky=tk.W, pady=(5, 0))
        
        # 최소 높이 비율
        ttk.Label(frame, text="최소 높이 비율:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.min_height_ratio_var = tk.DoubleVar()
        ttk.Spinbox(frame, from_=0.3, to=0.9, increment=0.05, textvariable=self.min_height_ratio_var, width=15).grid(row=4, column=1, sticky=tk.W, pady=(5, 0))
        
        # 샘플 스트라이드
        ttk.Label(frame, text="샘플 스트라이드:").grid(row=5, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.sample_stride_var = tk.IntVar()
        ttk.Spinbox(frame, from_=1, to=10, textvariable=self.sample_stride_var, width=15).grid(row=5, column=1, sticky=tk.W, pady=(5, 0))
    
    def _load_settings(self):
        """현재 설정 로드"""
        self.column_width_var.set(self.settings.get("column_width", 1000))
        self.column_height_var.set(self.settings.get("column_height", 1400))
        self.overlap_var.set(self.settings.get("overlap", 40))
        self.smart_cut_var.set(self.settings.get("smart_cut", True))
        self.smart_band_var.set(self.settings.get("smart_band", 60))
        self.page_width_var.set(self.settings.get("page_width", 0))
        self.page_height_var.set(self.settings.get("page_height", 0))
        self.optimize_slices_var.set(self.settings.get("optimize_slices", True))
        
        # 스마트 컷 고급 설정
        self.bg_strip_var.set(self.settings.get("bg_strip", 12))
        self.bg_thresh_var.set(self.settings.get("bg_thresh", 18))
        self.bg_ratio_hi_var.set(self.settings.get("bg_ratio_hi", 0.85))
        self.bg_ratio_mid_var.set(self.settings.get("bg_ratio_mid", 0.70))
        self.min_height_ratio_var.set(self.settings.get("min_height_ratio", 0.60))
        self.sample_stride_var.set(self.settings.get("sample_stride", 4))
    
    def _reset_defaults(self):
        """기본값으로 재설정"""
        self.column_width_var.set(1000)
        self.column_height_var.set(1400)
        self.overlap_var.set(40)
        self.smart_cut_var.set(True)
        self.smart_band_var.set(60)
        self.page_width_var.set(0)
        self.page_height_var.set(0)
        self.optimize_slices_var.set(True)
        
        # 스마트 컷 고급 설정 기본값
        self.bg_strip_var.set(12)
        self.bg_thresh_var.set(18)
        self.bg_ratio_hi_var.set(0.85)
        self.bg_ratio_mid_var.set(0.70)
        self.min_height_ratio_var.set(0.60)
        self.sample_stride_var.set(4)
    
    def _ok(self):
        """확인 버튼 처리"""
        self.result = {
            "column_width": self.column_width_var.get(),
            "column_height": self.column_height_var.get(),
            "overlap": self.overlap_var.get(),
            "smart_cut": self.smart_cut_var.get(),
            "smart_band": self.smart_band_var.get(),
            "page_width": self.page_width_var.get(),
            "page_height": self.page_height_var.get(),
            "optimize_slices": self.optimize_slices_var.get(),
            "bg_strip": self.bg_strip_var.get(),
            "bg_thresh": self.bg_thresh_var.get(),
            "bg_ratio_hi": self.bg_ratio_hi_var.get(),
            "bg_ratio_mid": self.bg_ratio_mid_var.get(),
            "min_height_ratio": self.min_height_ratio_var.get(),
            "sample_stride": self.sample_stride_var.get(),
        }
        self.dialog.destroy()
    
    def _cancel(self):
        """취소 버튼 처리"""
        self.result = None
        self.dialog.destroy()
