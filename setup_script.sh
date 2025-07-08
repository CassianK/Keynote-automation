#!/bin/bash

# 🍎 Keynote 자동 생성기 설치 및 실행 스크립트
# Version: 1.0.0

set -e  # 오류 시 스크립트 종료

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 이모지 정의
APPLE="🍎"
ROCKET="🚀"
CHECK="✅"
WARNING="⚠️"
ERROR="❌"
FOLDER="📁"
GEAR="⚙️"
FIRE="🔥"

echo -e "${PURPLE}${APPLE} Keynote 자동 생성기 설치 스크립트${NC}"
echo -e "${BLUE}===================================${NC}"
echo

# 시스템 확인
check_system() {
    echo -e "${CYAN}${GEAR} 시스템 환경 확인 중...${NC}"
    
    # macOS 확인
    if [[ "$OSTYPE" != "darwin"* ]]; then
        echo -e "${ERROR} 이 앱은 macOS에서만 작동합니다!"
        exit 1
    fi
    echo -e "${CHECK} macOS 확인됨"
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        echo -e "${ERROR} Python 3이 설치되어 있지 않습니다!"
        echo "Homebrew로 설치: brew install python3"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo -e "${CHECK} Python ${PYTHON_VERSION} 확인됨"
    
    # Keynote 확인
    if ! ls /Applications/Keynote.app &> /dev/null; then
        echo -e "${WARNING} Keynote가 설치되어 있지 않습니다!"
        echo "App Store에서 Keynote를 설치해주세요."
        read -p "계속하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${CHECK} Keynote 앱 확인됨"
    fi
    
    echo
}

# 프로젝트 디렉토리 생성
create_project_structure() {
    echo -e "${CYAN}${FOLDER} 프로젝트 구조 생성 중...${NC}"
    
    # 메인 디렉토리들
    mkdir -p templates
    mkdir -p layouts
    mkdir -p samples/sample_images
    mkdir -p output
    mkdir -p tests
    
    echo -e "${CHECK} 디렉토리 구조 생성 완료"
    echo
}

# Python 의존성 설치
install_dependencies() {
    echo -e "${CYAN}${GEAR} Python 의존성 설치 중...${NC}"
    
    # requirements.txt가 없으면 생성
    if [ ! -f "requirements.txt" ]; then
        cat > requirements.txt << 'EOF'
# GUI Framework
# tkinter is included in Python standard library

# Image Processing
Pillow>=8.0.0

# Data Processing
typing-extensions>=4.0.0

# Development Tools (Optional)
pytest>=6.0.0
black>=21.0.0
flake8>=3.8.0
EOF
    fi
    
    # pip 업그레이드
    python3 -m pip install --upgrade pip
    
    # 의존성 설치
    python3 -m pip install -r requirements.txt
    
    echo -e "${CHECK} Python 의존성 설치 완료"
    echo
}

# 설정 파일 생성
create_config_files() {
    echo -e "${CYAN}${GEAR} 설정 파일 생성 중...${NC}"
    
    # config.json 생성 (기본 설정)
    if [ ! -f "config.json" ]; then
        cat > config.json << 'EOF'
{
    "app_settings": {
        "name": "Keynote 자동 생성기",
        "version": "1.0.0",
        "debug": false
    },
    "templates": {
        "business": {
            "path": "templates/business.key",
            "description": "비즈니스 프레젠테이션"
        },
        "creative": {
            "path": "templates/creative.key", 
            "description": "창의적 디자인"
        },
        "minimal": {
            "path": "templates/minimal.key",
            "description": "미니멀 스타일"
        }
    },
    "image_settings": {
        "default_position": "right",
        "default_size": "medium"
    }
}
EOF
        echo -e "${CHECK} config.json 생성됨"
    fi
    
    # .gitignore 생성
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Keynote files (large)
templates/*.key
output/*.key

# Logs
*.log

# Temporary files
tmp/
temp/
EOF
        echo -e "${CHECK} .gitignore 생성됨"
    fi
    
    echo
}

# 샘플 파일 생성
create_sample_files() {
    echo -e "${CYAN}${FOLDER} 샘플 파일 생성 중...${NC}"
    
    # 샘플 텍스트 파일
    if [ ! -f "samples/sample_content.txt" ]; then
        cat > samples/sample_content.txt << 'EOF'
AI와 미래의 일

AI 기술의 급속한 발전
• 머신러닝과 딥러닝의 혁신
• 자연어 처리 기술의 진보
• 컴퓨터 비전의 놀라운 성과

일상 생활의 변화
• 스마트 홈과 IoT 기기
• 자율주행 자동차
• 개인화된 추천 시스템

미래 직업의 변화
새로운 직업의 등장과 기존 업무의 자동화로 인해 인간-AI 협업이 중요해질 것입니다.

결론
AI는 우리의 위협이 아닌 파트너가 될 것입니다.
EOF
        echo -e "${CHECK} 샘플 텍스트 파일 생성됨"
    fi
    
    echo
}

# 접근성 권한 확인
check_accessibility_permissions() {
    echo -e "${CYAN}${GEAR} 접근성 권한 확인 중...${NC}"
    
    echo -e "${YELLOW}중요: AppleScript 실행을 위해 접근성 권한이 필요합니다.${NC}"
    echo
    echo "다음 단계를 따라주세요:"
    echo "1. 시스템 환경설정 → 보안 및 개인정보 보호"
    echo "2. 개인정보 보호 탭 → 접근성"
    echo "3. 🔒 자물쇠 클릭하여 잠금 해제"
    echo "4. Terminal (또는 사용 중인 터미널) 추가"
    echo "5. ✅ 체크박스 활성화"
    echo
    
    read -p "접근성 권한을 설정했습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${WARNING} 접근성 권한 없이는 AppleScript가 작동하지 않습니다."
    else
        echo -e "${CHECK} 접근성 권한 설정 확인됨"
    fi
    echo
}

# 템플릿 파일 안내
template_guidance() {
    echo -e "${CYAN}${FOLDER} Keynote 템플릿 파일 안내${NC}"
    echo
    echo -e "${YELLOW}templates/ 폴더에 다음 파일들을 추가해주세요:${NC}"
    echo "• business.key (비즈니스용 템플릿)"
    echo "• creative.key (창의적 디자인 템플릿)"
    echo "• minimal.key (미니멀 스타일 템플릿)"
    echo "• academic.key (학술 발표용 템플릿)"
    echo
    echo "템플릿 파일은 Keynote에서 '다른 이름으로 저장'으로 생성할 수 있습니다."
    echo
    
    read -p "템플릿 파일을 준비했습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${WARNING} 템플릿 파일 없이도 기본 기능은 사용 가능합니다."
    fi
    echo
}

# 테스트 실행
run_tests() {
    echo -e "${CYAN}🧪 테스트 실행 중...${NC}"
    
    if [ -f "test_generator.py" ]; then
        python3 test_generator.py --unit
        if [ $? -eq 0 ]; then
            echo -e "${CHECK} 모든 테스트 통과!"
        else
            echo -e "${WARNING} 일부 테스트 실패 (정상적으로 작동할 수 있습니다)"
        fi
    else
        echo -e "${WARNING} 테스트 파일이 없습니다."
    fi
    echo
}

# 메인 앱 실행
launch_app() {
    echo -e "${CYAN}${ROCKET} Keynote 자동 생성기 실행...${NC}"
    echo
    
    if [ -f "keynote_generator.py" ]; then
        echo -e "${FIRE} GUI 앱을 시작합니다!"
        python3 keynote_generator.py
    else
        echo -e "${ERROR} keynote_generator.py 파일이 없습니다!"
        echo "메인 Python 파일을 먼저 생성해주세요."
        exit 1
    fi
}

# 사용법 안내
show_usage() {
    echo -e "${BLUE}사용법:${NC}"
    echo "./setup.sh [옵션]"
    echo
    echo "옵션:"
    echo "  install    - 전체 설치 과정 실행"
    echo "  run        - 앱 실행만"
    echo "  test       - 테스트만 실행"
    echo "  clean      - 생성된 파일들 정리"
    echo "  help       - 도움말 표시"
    echo
}

# 정리 함수
clean_project() {
    echo -e "${CYAN}🧹 프로젝트 정리 중...${NC}"
    
    # Python 캐시 삭제
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # 임시 파일 삭제
    rm -rf tmp/ temp/ 2>/dev/null || true
    
    # 출력 파일들 삭제 (선택적)
    read -p "출력된 Keynote 파일들도 삭제하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf output/*.key 2>/dev/null || true
        echo -e "${CHECK} 출력 파일들 삭제됨"
    fi
    
    echo -e "${CHECK} 프로젝트 정리 완료"
}

# 전체 설치 과정
full_install() {
    echo -e "${PURPLE}${APPLE} Keynote 자동 생성기 전체 설치 시작${NC}"
    echo -e "${BLUE}====================================${NC}"
    echo
    
    check_system
    create_project_structure
    install_dependencies
    create_config_files
    create_sample_files
    check_accessibility_permissions
    template_guidance
    
    echo -e "${GREEN}${CHECK} 설치가 완료되었습니다!${NC}"
    echo
    echo -e "${YELLOW}다음 명령어로 앱을 실행하세요:${NC}"
    echo "python3 keynote_generator.py"
    echo
    echo -e "${YELLOW}또는:${NC}"
    echo "./setup.sh run"
    echo
}

# 메인 로직
case "${1:-install}" in
    "install")
        full_install
        ;;
    "run")
        check_system
        launch_app
        ;;
    "test")
        check_system
        run_tests
        ;;
    "clean")
        clean_project
        ;;
    "help"|"--help"|"-h")
        show_usage
        ;;
    *)
        echo -e "${ERROR} 알 수 없는 옵션: $1"
        show_usage
        exit 1
        ;;
esac
