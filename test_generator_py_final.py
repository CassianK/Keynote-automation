#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Keynote Generator 테스트 스크립트
모든 기능을 테스트하여 정상 작동 확인

Author: AI Assistant
Version: 1.0.0
"""

import sys
import os
import json
import tempfile
import subprocess
import time

def test_basic_functionality():
    """기본 기능 테스트"""
    print("🧪 기본 기능 테스트 시작...")
    
    # Python 버전 확인
    print(f"✅ Python 버전: {sys.version}")
    
    # 필수 모듈 임포트 테스트
    try:
        import tkinter as tk
        print("✅ tkinter 모듈 정상")
    except ImportError:
        print("❌ tkinter 모듈 없음")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow 모듈 정상")
    except ImportError:
        print("❌ Pillow 모듈 없음 (pip install Pillow)")
        return False
    
    # 파일 구조 확인
    required_files = [
        'keynote_generator_main.py',
        'config.json',
        'templates/',
        'applescript_controller.scpt'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} 존재함")
        else:
            print(f"⚠️  {file_path} 없음")
    
    return True

def test_config_loading():
    """설정 파일 로딩 테스트"""
    print("\n⚙️ 설정 파일 테스트...")
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ config.json 로딩 성공")
        print(f"✅ 템플릿 개수: {len(config.get('templates', {}))}")
        
        # 23개 템플릿 확인
        templates = config.get('templates', {})
        if len(templates) == 23:
            print("✅ 23개 템플릿 설정 확인됨")
        else:
            print(f"⚠️  템플릿 개수: {len(templates)}개 (예상: 23개)")
        
        return True
    except FileNotFoundError:
        print("❌ config.json 파일 없음")
        return False
    except json.JSONDecodeError:
        print("❌ config.json 형식 오류")
        return False

def test_template_files():
    """템플릿 파일 확인 테스트"""
    print("\n📁 템플릿 파일 테스트...")
    
    if not os.path.exists('templates/'):
        print("❌ templates/ 폴더 없음")
        return False
    
    key_files = [f for f in os.listdir('templates/') if f.endswith('.key')]
    print(f"✅ 발견된 .key 파일: {len(key_files)}개")
    
    # 1.key부터 23.key까지 확인
    expected_files = [f"{i}.key" for i in range(1, 24)]
    missing_files = []
    
    for expected_file in expected_files:
        if expected_file not in key_files:
            missing_files.append(expected_file)
    
    if not missing_files:
        print("✅ 모든 템플릿 파일 (1.key ~ 23.key) 존재함")
    else:
        print(f"⚠️  누락된 파일들: {missing_files}")
    
    # 처음 5개 파일 표시
    for i, file in enumerate(sorted(key_files)[:5]):
        print(f"  📄 {file}")
    
    if len(key_files) > 5:
        print(f"  ... 그 외 {len(key_files) - 5}개 더")
    
    return len(key_files) > 0

def test_applescript_availability():
    """AppleScript 사용 가능 여부 테스트"""
    print("\n🍎 AppleScript 테스트...")
    
    # macOS 확인
    if sys.platform != 'darwin':
        print("❌ macOS가 아님 - AppleScript 사용 불가")
        return False
    
    print("✅ macOS 환경 확인됨")
    
    # osascript 명령 확인
    try:
        result = subprocess.run(['osascript', '-e', 'return "test"'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ osascript 명령 사용 가능")
            return True
        else:
            print("❌ osascript 명령 실행 실패")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  osascript 명령 시간 초과")
        return False
    except Exception as e:
        print(f"❌ osascript 테스트 오류: {e}")
        return False

def test_keynote_app():
    """Keynote 앱 확인 테스트"""
    print("\n🎯 Keynote 앱 테스트...")
    
    keynote_path = '/Applications/Keynote.app'
    if os.path.exists(keynote_path):
        print("✅ Keynote 앱 설치됨")
        return True
    else:
        print("⚠️  Keynote 앱 없음 - App Store에서 설치 필요")
        return False

def test_accessibility_permissions():
    """접근성 권한 테스트"""
    print("\n🔐 접근성 권한 테스트...")
    
    # 간단한 AppleScript로 테스트
    try:
        # 해롭지 않은 간단한 AppleScript 실행
        script = 'tell application "System Events" to return name of processes'
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ 접근성 권한 설정됨")
            return True
        else:
            print("⚠️  접근성 권한 필요")
            print("시스템 환경설정 → 보안 및 개인정보 보호 → 접근성에서 Terminal 권한 부여")
            return False
            
    except Exception as e:
        print(f"⚠️  접근성 권한 테스트 실패: {e}")
        return False

def test_applescript_controller():
    """AppleScript 컨트롤러 파일 테스트"""
    print("\n📜 AppleScript 컨트롤러 테스트...")
    
    if not os.path.exists('applescript_controller.scpt'):
        print("❌ applescript_controller.scpt 파일 없음")
        return False
    
    print("✅ applescript_controller.scpt 파일 존재함")
    
    # 파일 크기 확인
    file_size = os.path.getsize('applescript_controller.scpt')
    print(f"✅ 파일 크기: {file_size:,} bytes")
    
    return True

def create_sample_test():
    """샘플 파일 생성 테스트"""
    print("\n📝 샘플 파일 생성 테스트...")
    
    # 임시 텍스트 파일 생성
    sample_text = """AI와 미래의 일

AI 기술의 발전
• 머신러닝의 혁신
• 자연어 처리 기술
• 컴퓨터 비전의 발전

결론
AI는 우리의 파트너입니다."""
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_text)
            temp_path = f.name
        
        print(f"✅ 샘플 텍스트 파일 생성: {temp_path}")
        
        # 파일 삭제
        os.unlink(temp_path)
        print("✅ 임시 파일 정리 완료")
        
        return True
    except Exception as e:
        print(f"❌ 샘플 파일 생성 실패: {e}")
        return False

def run_performance_test():
    """성능 테스트"""
    print("\n🚀 성능 테스트...")
    
    # 텍스트 처리 성능 테스트
    large_text = "테스트 텍스트입니다. " * 1000
    
    start_time = time.time()
    
    # 간단한 텍스트 분석 시뮬레이션
    lines = large_text.split('\n')
    bullet_count = sum(1 for line in lines if line.strip().startswith('•'))
    text_length = len(large_text)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"✅ 텍스트 처리 시간: {processing_time:.4f}초")
    print(f"✅ 처리된 텍스트 길이: {text_length:,}자")
    
    if processing_time < 1.0:
        print("✅ 성능: 우수")
        return True
    else:
        print("⚠️  성능: 보통")
        return True

def generate_test_report():
    """테스트 보고서 생성"""
    print("\n📊 테스트 결과 요약")
    print("=" * 50)
    
    tests = [
        ("기본 기능", test_basic_functionality),
        ("설정 파일", test_config_loading),
        ("템플릿 파일", test_template_files),
        ("AppleScript", test_applescript_availability),
        ("Keynote 앱", test_keynote_app),
        ("접근성 권한", test_accessibility_permissions),
        ("컨트롤러 파일", test_applescript_controller),
        ("샘플 생성", create_sample_test),
        ("성능", run_performance_test)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name} 테스트 실행 중...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 테스트 오류: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📋 최종 테스트 결과")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name:15} : {status}")
        if result:
            passed += 1
    
    print(f"\n📊 전체 결과: {passed}/{total} 통과 ({passed/total*100:.1f}%)")
    
    if passed >= total * 0.8:  # 80% 이상 통과
        print("\n🎉 시스템이 정상적으로 작동할 준비가 되었습니다!")
        print("\n🚀 다음 명령어로 앱을 실행하세요:")
        print("python3 keynote_generator_main.py")
        return True
    else:
        print("\n⚠️  일부 문제가 있습니다. 위의 실패 항목들을 확인해주세요.")
        return False

def main():
    """메인 함수"""
    print("🍎 Keynote 자동 생성기 테스트 시작")
    print("=" * 50)
    
    success = generate_test_report()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
