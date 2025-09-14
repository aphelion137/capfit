"""
메인 윈도우 GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
from typing import List, Optional

from shared.core import (
    split_image,
    build_pdf_two_columns,
    build_pdf_one_per_page,
    build_pdf_two_columns_from_source,
    build_pdf_two_columns_from_sources,
    compute_two_column_layout,
)
from .settings_dialog import SettingsDialog
from .preview_widget import PreviewWidget


class MainWindow:
    """메인 윈도우 클래스"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Capfit - 캡처 2단 PDF 변환기")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 상태 변수
        self.input_files: List[str] = []
        self.output_dir = ""
        self.settings = {
            "column_width": 1000,
            "column_height": 1400,
            "overlap": 40,
            "smart_cut": True,
            "smart_band": 60,
            "make_pdf": True,
            "pdf_mode": "two_columns",
            "margin": 60,
            "gutter": 50,
            "dpi": 220,
            "page_width": 0,
            "page_height": 0,
            "optimize_slices": True,
        }
        
        self._setup_ui()
        self._setup_menu()
        
    def _setup_menu(self):
        """메뉴바 설정"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="이미지 열기...", command=self._open_files)
        file_menu.add_command(label="출력 폴더 선택...", command=self._select_output_dir)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)
        
        # 설정 메뉴
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="설정", menu=settings_menu)
        settings_menu.add_command(label="고급 설정...", command=self._open_settings)
        
        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="사용법", command=self._show_help)
        help_menu.add_command(label="정보", command=self._show_about)
    
    def _setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 제목
        title_label = ttk.Label(main_frame, text="Capfit - 캡처 2단 PDF 변환기", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 파일 선택 섹션
        file_frame = ttk.LabelFrame(main_frame, text="파일 선택", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, text="이미지 열기", command=self._open_files).grid(row=0, column=0, padx=(0, 10))
        self.file_label = ttk.Label(file_frame, text="선택된 파일 없음", foreground="gray")
        self.file_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Button(file_frame, text="출력 폴더", command=self._select_output_dir).grid(row=1, column=0, padx=(0, 10), pady=(5, 0))
        self.output_label = ttk.Label(file_frame, text="기본 출력 폴더 사용", foreground="gray")
        self.output_label.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 설정 섹션
        settings_frame = ttk.LabelFrame(main_frame, text="변환 설정", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        
        # DPI 설정
        ttk.Label(settings_frame, text="DPI:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.dpi_var = tk.IntVar(value=self.settings["dpi"])
        dpi_spinbox = ttk.Spinbox(settings_frame, from_=72, to=220, textvariable=self.dpi_var, width=10)
        dpi_spinbox.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20))
        
        # 여백 설정
        ttk.Label(settings_frame, text="여백(px):").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.margin_var = tk.IntVar(value=self.settings["margin"])
        margin_spinbox = ttk.Spinbox(settings_frame, from_=0, to=200, textvariable=self.margin_var, width=10)
        margin_spinbox.grid(row=0, column=3, sticky=(tk.W, tk.E))
        
        # 거터 설정
        ttk.Label(settings_frame, text="거터(px):").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.gutter_var = tk.IntVar(value=self.settings["gutter"])
        gutter_spinbox = ttk.Spinbox(settings_frame, from_=0, to=200, textvariable=self.gutter_var, width=10)
        gutter_spinbox.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=(5, 0))
        
        # PDF 모드 설정
        ttk.Label(settings_frame, text="PDF 모드:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.pdf_mode_var = tk.StringVar(value=self.settings["pdf_mode"])
        pdf_mode_combo = ttk.Combobox(settings_frame, textvariable=self.pdf_mode_var, 
                                     values=["two_columns", "one_per_page"], state="readonly", width=15)
        pdf_mode_combo.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 스마트 컷 설정
        self.smart_cut_var = tk.BooleanVar(value=self.settings["smart_cut"])
        smart_cut_check = ttk.Checkbutton(settings_frame, text="스마트 컷 사용", variable=self.smart_cut_var)
        smart_cut_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # 고급 설정 버튼
        ttk.Button(settings_frame, text="고급 설정...", command=self._open_settings).grid(row=2, column=2, columnspan=2, pady=(10, 0))
        
        # 미리보기 섹션
        preview_frame = ttk.LabelFrame(main_frame, text="레이아웃 미리보기", padding="10")
        preview_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        
        self.preview = PreviewWidget(preview_frame, self.settings)
        self.preview.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 변환 버튼
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        self.convert_button = ttk.Button(button_frame, text="PDF 변환 시작", command=self._start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.progress = ttk.Progressbar(button_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 상태 표시
        self.status_label = ttk.Label(main_frame, text="준비됨", foreground="green")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=(10, 0))
        
        # 설정 변경 시 미리보기 업데이트
        self.dpi_var.trace('w', self._update_preview)
        self.margin_var.trace('w', self._update_preview)
        self.gutter_var.trace('w', self._update_preview)
        self.pdf_mode_var.trace('w', self._update_preview)
    
    def _open_files(self):
        """파일 선택 대화상자"""
        files = filedialog.askopenfilenames(
            title="이미지 파일 선택",
            filetypes=[
                ("이미지 파일", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("PNG 파일", "*.png"),
                ("JPEG 파일", "*.jpg *.jpeg"),
                ("모든 파일", "*.*")
            ]
        )
        
        if files:
            self.input_files = list(files)
            if len(files) == 1:
                self.file_label.config(text=f"선택됨: {Path(files[0]).name}", foreground="black")
            else:
                self.file_label.config(text=f"선택됨: {len(files)}개 파일", foreground="black")
            self._update_convert_button()
    
    def _select_output_dir(self):
        """출력 폴더 선택 대화상자"""
        directory = filedialog.askdirectory(title="출력 폴더 선택")
        if directory:
            self.output_dir = directory
            self.output_label.config(text=f"출력: {Path(directory).name}", foreground="black")
    
    def _open_settings(self):
        """고급 설정 대화상자"""
        dialog = SettingsDialog(self.root, self.settings)
        if dialog.result:
            self.settings.update(dialog.result)
            self._update_preview()
    
    def _update_preview(self, *args):
        """미리보기 업데이트"""
        current_settings = {
            "dpi": self.dpi_var.get(),
            "margin": self.margin_var.get(),
            "gutter": self.gutter_var.get(),
            "pdf_mode": self.pdf_mode_var.get(),
        }
        self.preview.update_settings(current_settings)
    
    def _update_convert_button(self):
        """변환 버튼 상태 업데이트"""
        if self.input_files:
            self.convert_button.config(state="normal")
        else:
            self.convert_button.config(state="disabled")
    
    def _start_conversion(self):
        """변환 시작"""
        if not self.input_files:
            messagebox.showerror("오류", "변환할 이미지 파일을 선택해주세요.")
            return
        
        # 설정 업데이트
        self.settings.update({
            "dpi": self.dpi_var.get(),
            "margin": self.margin_var.get(),
            "gutter": self.gutter_var.get(),
            "pdf_mode": self.pdf_mode_var.get(),
            "smart_cut": self.smart_cut_var.get(),
        })
        
        # 백그라운드에서 변환 실행
        self.convert_button.config(state="disabled")
        self.progress.start()
        self.status_label.config(text="변환 중...", foreground="blue")
        
        thread = threading.Thread(target=self._convert_files)
        thread.daemon = True
        thread.start()
    
    def _convert_files(self):
        """파일 변환 (백그라운드 스레드)"""
        try:
            if len(self.input_files) == 1:
                # 단일 파일 처리
                input_path = self.input_files[0]
                base_name = Path(input_path).stem
                output_dir = self.output_dir or "out"
                pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
                
                # 디렉토리 생성
                os.makedirs(output_dir, exist_ok=True)
                
                # PDF 생성
                build_pdf_two_columns_from_source(
                    input_path,
                    pdf_path,
                    margin=self.settings["margin"],
                    gutter=self.settings["gutter"],
                    dpi=self.settings["dpi"],
                    page_width=self.settings["page_width"] or None,
                    page_height=self.settings["page_height"] or None,
                    fast=False,
                )
                
                result_message = f"변환 완료!\nPDF 저장 위치: {pdf_path}"
                
            else:
                # 다중 파일 처리
                base_name = "combined"
                output_dir = self.output_dir or "out"
                pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
                
                # 디렉토리 생성
                os.makedirs(output_dir, exist_ok=True)
                
                # PDF 생성
                build_pdf_two_columns_from_sources(
                    self.input_files,
                    pdf_path,
                    margin=self.settings["margin"],
                    gutter=self.settings["gutter"],
                    dpi=self.settings["dpi"],
                    page_width=self.settings["page_width"] or None,
                    page_height=self.settings["page_height"] or None,
                    fast=False,
                )
                
                result_message = f"변환 완료!\n{len(self.input_files)}개 파일이 하나의 PDF로 합쳐졌습니다.\n저장 위치: {pdf_path}"
            
            # UI 업데이트 (메인 스레드에서)
            self.root.after(0, self._conversion_success, result_message)
            
        except Exception as e:
            error_message = f"변환 중 오류가 발생했습니다:\n{str(e)}"
            self.root.after(0, self._conversion_error, error_message)
    
    def _conversion_success(self, message):
        """변환 성공 처리"""
        self.progress.stop()
        self.convert_button.config(state="normal")
        self.status_label.config(text="변환 완료", foreground="green")
        messagebox.showinfo("변환 완료", message)
    
    def _conversion_error(self, message):
        """변환 오류 처리"""
        self.progress.stop()
        self.convert_button.config(state="normal")
        self.status_label.config(text="변환 실패", foreground="red")
        messagebox.showerror("변환 오류", message)
    
    def _show_help(self):
        """도움말 표시"""
        help_text = """
Capfit 사용법:

1. '이미지 열기' 버튼으로 변환할 이미지 파일을 선택합니다.
2. 필요시 '출력 폴더' 버튼으로 저장 위치를 지정합니다.
3. DPI, 여백, 거터 등의 설정을 조정합니다.
4. '고급 설정'에서 더 세부적인 옵션을 설정할 수 있습니다.
5. 'PDF 변환 시작' 버튼을 클릭하여 변환을 시작합니다.

지원 형식: PNG, JPG, JPEG, BMP, TIFF
출력 형식: PDF (2단 또는 1페이지당 1이미지)
        """
        messagebox.showinfo("사용법", help_text)
    
    def _show_about(self):
        """정보 표시"""
        about_text = """
Capfit v0.1.15

긴 캡처 이미지를 A4 세로 2단 PDF로 변환하는 도구입니다.

특징:
- 스마트 컷으로 자연스러운 분할
- 2단 레이아웃으로 공간 효율성 극대화
- 고품질 PDF 출력 (최대 220 DPI)
- 다중 파일 일괄 처리 지원

개발: Capfit Team
        """
        messagebox.showinfo("정보", about_text)
    
    def run(self):
        """애플리케이션 실행"""
        self.root.mainloop()
