#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🍎 Keynote 자동 생성기
AI 기반 레이아웃 선택과 AppleScript 연동으로 자동 프레젠테이션 생성

Author: AI Assistant
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import json
import os
import time
from PIL import Image, ImageTk
import re
from dataclasses import dataclass
from typing import List, Dict, Optional
import threading

@dataclass
class SlideData:
    """슬라이드 데이터 구조"""
    slide_type: str
    layout: str
    title: str
    content: str = ""
    image_path: Optional[str] = None
    image_position: str = "right"
    image_size: str = "medium"

class ContentAnalyzer:
    """AI 기반 컨텐츠 분석기"""
    
    @staticmethod
    def detect_text_type(text: str) -> str:
        """텍스트 유형 감지"""
        if not text.strip():
            return 'empty'
        
        # 불릿 포인트 감지
        bullet_patterns = [r'^\s*[•·▪▫-]\s', r'^\s*\d+\.\s', r'^\s*[a-zA-Z]\.\s']
        bullet_count = sum(len(re.findall(pattern, text, re.MULTILINE)) 
                          for pattern in bullet_patterns)
        
        if bullet_count >= 3:
            return 'bullet_list'
        elif len(text.split('\n')) <= 2 and len(text) < 100:
            return 'title_subtitle'
        elif len(text) > 500:
            return 'long_content'
        elif text.count(':') >= 2:
            return 'definition_list'
        else:
            return 'standard_content'
    
    @staticmethod
    def analyze_image(image_path: str) -> Dict:
        """이미지 분석"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                aspect_ratio = width / height
                
                return {
                    'aspect_ratio': aspect_ratio,
                    'type': ContentAnalyzer._classify_image_type(aspect_ratio),
                    'size': 'large' if max(width, height) > 1500 else 'medium'
                }
        except Exception:
            return {'aspect_ratio': 1.0, 'type': 'standard', 'size': 'medium'}
    
    @staticmethod
    def _classify_image_type(aspect_ratio: float) -> str:
        """이미지 타입 분류"""
        if aspect_ratio > 1.8:
            return 'wide_chart'
        elif aspect_ratio < 0.6:
            return 'tall_infographic'
        elif 0.9 <= aspect_ratio <= 1.1:
            return 'square_icon'
        else:
            return 'standard_photo'

class LayoutSelector:
    """AI 기반 레이아웃 선택기"""
    
    LAYOUT_RULES = {
        'title_slide': {
            'condition': lambda analysis: (
                analysis['text_type'] == 'title_subtitle' and 
                analysis['image_count'] == 0
            ),
            'keynote_layout': 'Title & Subtitle',
            'priority': 10
        },
        
        'bullet_slide': {
            'condition': lambda analysis: (
                analysis['text_type'] == 'bullet_list' and 
                analysis['text_length'] > 100
            ),
            'keynote_layout': 'Title & Bullets',
            'priority': 9
        },
        
        'image_focus': {
            'condition': lambda analysis: (
                analysis['image_count'] >= 1 and 
                analysis['text_length'] < 150
            ),
            'keynote_layout': 'Title, Bullets & Photo',
            'priority': 8
        },
        
        'text_image_balanced': {
            'condition': lambda analysis: (
                analysis['image_count'] == 1 and 
                150 <= analysis['text_length'] <= 400
            ),
            'keynote_layout': 'Title, Bullets & Photo',
            'priority': 7
        },
        
        'content_heavy': {
            'condition': lambda analysis: (
                analysis['text_length'] > 400 and 
                analysis['image_count'] <= 1
            ),
            'keynote_layout': 'Title & Bullets',
            'priority': 6
        },
        
        'multi_image': {
            'condition': lambda analysis: analysis['image_count'] > 1,
            'keynote_layout': 'Photo - 3 Up',
            'priority': 5
        }
    }
    
    @classmethod
    def select_optimal_layout(cls, analysis: Dict) -> Dict:
        """최적 레이아웃 선택"""
        applicable_layouts = []
        
        for layout_name, rule in cls.LAYOUT_RULES.items():
            if rule['condition'](analysis):
                applicable_layouts.append({
                    'name': layout_name,
                    'keynote_layout': rule['keynote_layout'],
                    'priority': rule['priority']
                })
        
        if applicable_layouts:
            # 우선순위가 높은 레이아웃 선택
            best_layout = max(applicable_layouts, key=lambda x: x['priority'])
            return best_layout
        
        # 기본 레이아웃
        return {
            'name': 'standard',
            'keynote_layout': 'Title & Bullets',
            'priority': 1
        }

class AppleScriptController:
    """AppleScript 컨트롤러"""
    
    @staticmethod
    def create_presentation_from_template(template_path: str, output_path: str) -> bool:
        """템플릿에서 프레젠테이션 생성"""
        script = f'''
        tell application "Keynote"
            activate
            try
                open POSIX file "{template_path}"
                set currentPres to front document
                
                -- 기존 슬라이드 삭제 (첫 번째 제외)
                repeat with i from (count of slides of currentPres) to 2 by -1
                    delete slide i of currentPres
                end repeat
                
                return true
            on error
                return false
            end try
        end tell
        '''
        
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def add_slide_with_layout(slide_data: SlideData) -> bool:
        """레이아웃으로 슬라이드 추가"""
        # 특수 문자 이스케이프
        title = slide_data.title.replace('"', '\\"').replace('\\', '\\\\')
        content = slide_data.content.replace('"', '\\"').replace('\\', '\\\\')
        
        script = f'''
        tell application "Keynote"
            tell front document
                try
                    set newSlide to make new slide with properties {{base layout:layout "{slide_data.layout}"}}
                    
                    -- 제목 설정
                    if "{title}" is not "" then
                        try
                            set object text of text item 1 of newSlide to "{title}"
                        end try
                    end if
                    
                    -- 내용 설정
                    if "{content}" is not "" then
                        try
                            set object text of text item 2 of newSlide to "{content}"
                        end try
                    end if
                    
                    return true
                on error
                    return false
                end try
            end tell
        end tell
        '''
        
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def add_image_to_current_slide(image_path: str, position: str = "right") -> bool:
        """현재 슬라이드에 이미지 추가"""
        script = f'''
        tell application "Keynote"
            tell front document
                try
                    set currentSlide to slide -1
                    set imageFile to POSIX file "{image_path}"
                    set newImage to make new image at currentSlide with properties {{file:imageFile}}
                    
                    -- 이미지 위치 조정 (간단 버전)
                    if "{position}" is "right" then
                        set position of newImage to {{400, 150}}
                        set size of newImage to {{300, 200}}
                    else if "{position}" is "center" then
                        set position of newImage to {{250, 200}}
                        set size of newImage to {{400, 300}}
                    end if
                    
                    return true
                on error
                    return false
                end try
            end tell
        end tell
        '''
        
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def save_presentation(output_path: str) -> bool:
        """프레젠테이션 저장"""
        script = f'''
        tell application "Keynote"
            tell front document
                try
                    save in POSIX file "{output_path}"
                    return true
                on error
                    return false
                end try
            end tell
        end tell
        '''
        
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

class KeynoteGenerator:
    """메인 Keynote 생성기 GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🍎 Keynote 자동 생성기 v1.0")
        self.root.geometry("1200x900")
        self.root.configure(bg='#f0f0f0')
        
        # 데이터 초기화
        self.images = []
        self.templates = self._load_templates()
        self.progress_var = tk.StringVar(value="준비 완료")
        
        self._setup_styles()
        self._create_widgets()
        
    def _setup_styles(self):
        """스타일 설정"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 커스텀 스타일 정의
        style.configure('Title.TLabel', font=('SF Pro Display', 24, 'bold'))
        style.configure('Header.TLabel', font=('SF Pro Display', 14, 'bold'))
        style.configure('Generate.TButton', font=('SF Pro Display', 12, 'bold'))
        
    def _load_templates(self) -> Dict:
        """config.json에서 템플릿 로드"""
        templates = {}
        
        try:
            # config.json에서 템플릿 정보 읽기
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            config_templates = config.get('templates', {})
            
            # 각 템플릿을 GUI에서 사용할 형태로 변환
            for template_id, template_info in config_templates.items():
                template_name = f"템플릿 {template_id}"
                if template_info.get('category'):
                    template_name += f" ({template_info['category']})"
                
                templates[template_name] = {
                    'path': template_info['path'],
                    'description': template_info.get('description', f'템플릿 {template_id}'),
                    'category': template_info.get('category', 'basic')
                }
        
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"config.json 로딩 실패: {e}")
            # 폴백: 기존 방식으로 템플릿 스캔
            templates_dir = "templates"
            if os.path.exists(templates_dir):
                key_files = [f for f in os.listdir(templates_dir) if f.endswith('.key')]
                for key_file in sorted(key_files):
                    template_name = key_file.replace('.key', '')
                    templates[f"템플릿 {template_name}"] = {
                        'path': os.path.join(templates_dir, key_file),
                        'description': f'템플릿 {template_name}',
                        'category': 'basic'
                    }
        
        return templates
    
    def _create_widgets(self):
        """GUI 위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="🍎 Keynote 자동 생성기", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 왼쪽 패널 - 입력
        input_frame = ttk.LabelFrame(main_frame, text="📝 컨텐츠 입력", padding="15")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), 
                        padx=(0, 10))
        
        # 텍스트 입력
        ttk.Label(input_frame, text="프레젠테이션 내용:", 
                 style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.text_area = scrolledtext.ScrolledText(input_frame, height=15, width=50,
                                                  font=('SF Pro Display', 11))
        self.text_area.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                           pady=(0, 10))
        
        # 샘플 텍스트 삽입
        sample_text = """AI와 미래의 일

AI 기술의 급속한 발전
• 머신러닝과 딥러닝의 혁신
• 자연어 처리 기술의 진보
• 컴퓨터 비전의 놀라운 성과

일상 생활의 변화
• 스마트 홈과 IoT 기기
• 자율주행 자동차
• 개인화된 추천 시스템

미래 직업의 변화
• 새로운 직업의 등장
• 기존 업무의 자동화
• 인간-AI 협업의 중요성

결론
AI는 우리의 파트너가 될 것입니다."""
        
        self.text_area.insert("1.0", sample_text)
        
        # 이미지 관리
        image_frame = ttk.Frame(input_frame)
        image_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                        pady=(10, 0))
        
        ttk.Label(image_frame, text="이미지:", 
                 style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(image_frame, text="📁 이미지 추가", 
                  command=self.add_images).grid(row=0, column=1, padx=(10, 0))
        
        # 이미지 리스트
        self.image_listbox = tk.Listbox(image_frame, height=5)
        self.image_listbox.grid(row=1, column=0, columnspan=2, 
                               sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 오른쪽 패널 - 설정
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ 생성 설정", padding="15")
        settings_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 템플릿 선택
        ttk.Label(settings_frame, text="템플릿 선택:", 
                 style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.template_var = tk.StringVar()
        template_names = list(self.templates.keys())
        if template_names:
            self.template_var.set(template_names[0])
        
        template_combo = ttk.Combobox(settings_frame, textvariable=self.template_var,
                                     values=template_names, state='readonly')
        template_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 템플릿 설명
        if template_names:
            initial_desc = self.templates[template_names[0]]['description']
            initial_category = self.templates[template_names[0]].get('category', 'basic')
            display_text = f"{initial_desc} [{initial_category}]"
        else:
            display_text = "템플릿 없음"
            
        self.template_desc = ttk.Label(settings_frame, text=display_text,
                                      font=('SF Pro Display', 10), foreground='gray')
        self.template_desc.grid(row=2, column=0, sticky=tk.W, pady=(0, 15))
        
        template_combo.bind('<<ComboboxSelected>>', self.on_template_change)
        
        # AI 분석 결과
        ttk.Label(settings_frame, text="AI 분석 결과:", 
                 style='Header.TLabel').grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        self.analysis_text = scrolledtext.ScrolledText(settings_frame, height=8, width=40,
                                                      font=('SF Pro Display', 10))
        self.analysis_text.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 분석 버튼
        ttk.Button(settings_frame, text="🧠 컨텐츠 분석", 
                  command=self.analyze_content).grid(row=5, column=0, pady=(0, 15))
        
        # 생성 버튼
        generate_btn = ttk.Button(settings_frame, text="🚀 Keynote 생성", 
                                 command=self.generate_keynote, style='Generate.TButton')
        generate_btn.grid(row=6, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        # 하단 상태바
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                         pady=(20, 0))
        
        ttk.Label(status_frame, text="상태:").grid(row=0, column=0, sticky=tk.W)
        status_label = ttk.Label(status_frame, textvariable=self.progress_var,
                                foreground='blue')
        status_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        input_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(0, weight=1)
        image_frame.columnconfigure(0, weight=1)
        
    def on_template_change(self, event):
        """템플릿 변경 이벤트"""
        template_name = self.template_var.get()
        if template_name in self.templates:
            description = self.templates[template_name]['description']
            category = self.templates[template_name].get('category', 'basic')
            display_text = f"{description} [{category}]"
            self.template_desc.config(text=display_text)
        
    def add_images(self):
        """이미지 추가"""
        file_paths = filedialog.askopenfilenames(
            title="이미지 선택",
            filetypes=[
                ("이미지 파일", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("모든 파일", "*.*")
            ]
        )
        
        for path in file_paths:
            if path not in [img['path'] for img in self.images]:
                self.images.append({
                    'path': path,
                    'name': os.path.basename(path)
                })
                self.image_listbox.insert(tk.END, os.path.basename(path))
        
        self.progress_var.set(f"이미지 {len(self.images)}개 추가됨")
        
    def analyze_content(self):
        """컨텐츠 분석"""
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("경고", "분석할 텍스트를 입력해주세요!")
            return
        
        self.progress_var.set("컨텐츠 분석 중...")
        
        # 텍스트 분석
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        analysis_results = []
        total_slides = len(paragraphs) + 1  # +1 for title slide
        
        for i, paragraph in enumerate(paragraphs):
            analysis = {
                'text_length': len(paragraph),
                'text_type': ContentAnalyzer.detect_text_type(paragraph),
                'image_count': 1 if i < len(self.images) else 0,
                'slide_number': i + 2  # +2 because first is title slide
            }
            
            optimal_layout = LayoutSelector.select_optimal_layout(analysis)
            analysis_results.append({
                'slide': f"슬라이드 {analysis['slide_number']}",
                'text_type': analysis['text_type'],
                'layout': optimal_layout['keynote_layout'],
                'text_length': analysis['text_length']
            })
        
        # 분석 결과 표시
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert("1.0", f"📊 분석 결과\n\n")
        self.analysis_text.insert(tk.END, f"총 슬라이드: {total_slides}개\n")
        self.analysis_text.insert(tk.END, f"이미지: {len(self.images)}개\n\n")
        
        for result in analysis_results:
            self.analysis_text.insert(tk.END, 
                f"{result['slide']}\n"
                f"  타입: {result['text_type']}\n"
                f"  레이아웃: {result['layout']}\n"
                f"  텍스트 길이: {result['text_length']}자\n\n"
            )
        
        self.progress_var.set("분석 완료!")
        
    def generate_keynote(self):
        """Keynote 생성"""
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("오류", "텍스트를 입력해주세요!")
            return
        
        # 백그라운드에서 실행
        thread = threading.Thread(target=self._generate_keynote_async, args=(text,))
        thread.daemon = True
        thread.start()
        
    def _generate_keynote_async(self, text):
        """비동기 Keynote 생성"""
        try:
            self.progress_var.set("Keynote 생성 중...")
            
            # 1. 템플릿 확인
            template_name = self.template_var.get()
            if template_name not in self.templates:
                messagebox.showerror("오류", f"선택된 템플릿을 찾을 수 없습니다: {template_name}")
                return
            
            template_path = self.templates[template_name]['path']
            
            if not os.path.exists(template_path):
                # 기본 템플릿 생성 (실제로는 사용자가 제공해야 함)
                messagebox.showerror("오류", 
                    f"템플릿 파일이 없습니다: {template_path}\n"
                    f"templates/ 폴더에 Keynote 템플릿을 추가해주세요!")
                return
            
            # 2. 출력 경로 설정
            timestamp = int(time.time())
            output_path = os.path.expanduser(f"~/Desktop/auto_presentation_{timestamp}.key")
            
            # 3. 슬라이드 구조 생성
            slides = self._create_slide_structure(text)
            
            # 4. Keynote 생성
            if not AppleScriptController.create_presentation_from_template(
                template_path, output_path):
                messagebox.showerror("오류", "Keynote 앱을 열 수 없습니다!")
                return
            
            # 5. 슬라이드 추가
            for i, slide in enumerate(slides):
                self.progress_var.set(f"슬라이드 {i+1}/{len(slides)} 생성 중...")
                
                if not AppleScriptController.add_slide_with_layout(slide):
                    print(f"슬라이드 {i+1} 생성 실패")
                
                # 이미지 추가
                if slide.image_path and os.path.exists(slide.image_path):
                    AppleScriptController.add_image_to_current_slide(
                        slide.image_path, slide.image_position)
                
                time.sleep(0.5)  # Keynote 처리 시간
            
            # 6. 저장
            if AppleScriptController.save_presentation(output_path):
                self.progress_var.set("생성 완료!")
                messagebox.showinfo("완료", 
                    f"Keynote 파일이 생성되었습니다!\n{output_path}")
            else:
                self.progress_var.set("저장 실패")
                messagebox.showerror("오류", "파일 저장에 실패했습니다!")
                
        except Exception as e:
            self.progress_var.set("생성 실패")
            messagebox.showerror("오류", f"생성 중 오류 발생:\n{str(e)}")
    
    def _create_slide_structure(self, text: str) -> List[SlideData]:
        """슬라이드 구조 생성"""
        slides = []
        
        # 제목 슬라이드
        first_line = text.split('\n')[0]
        slides.append(SlideData(
            slide_type='title',
            layout='Title & Subtitle',
            title=first_line,
            content='AI Assistant가 생성한 프레젠테이션'
        ))
        
        # 내용 슬라이드들
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        for i, paragraph in enumerate(paragraphs[1:] if len(paragraphs) > 1 else paragraphs):
            lines = paragraph.split('\n')
            title = lines[0][:50] + ('...' if len(lines[0]) > 50 else '')
            content = '\n'.join(lines[1:]) if len(lines) > 1 else lines[0]
            
            # AI 분석으로 레이아웃 결정
            analysis = {
                'text_length': len(paragraph),
                'text_type': ContentAnalyzer.detect_text_type(paragraph),
                'image_count': 1 if i < len(self.images) else 0
            }
            
            layout_info = LayoutSelector.select_optimal_layout(analysis)
            
            slide = SlideData(
                slide_type='content',
                layout=layout_info['keynote_layout'],
                title=title,
                content=content,
                image_path=self.images[i]['path'] if i < len(self.images) else None,
                image_position='right',
                image_size='medium'
            )
            
            slides.append(slide)
        
        return slides

def main():
    """메인 함수"""
    root = tk.Tk()
    app = KeynoteGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
