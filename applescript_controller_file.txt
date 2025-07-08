-- 🍎 Keynote Controller AppleScript
-- Keynote 자동화를 위한 AppleScript 컨트롤러
-- Version: 1.0.0

-- 프레젠테이션 생성 함수
on createPresentationFromTemplate(templatePath, outputPath)
    tell application "Keynote"
        activate
        
        try
            -- 템플릿 열기
            open POSIX file templatePath
            set currentPresentation to front document
            
            -- 기존 슬라이드 삭제 (템플릿의 첫 슬라이드 제외)
            set slideCount to count of slides of currentPresentation
            if slideCount > 1 then
                repeat with i from slideCount to 2 by -1
                    delete slide i of currentPresentation
                end repeat
            end if
            
            return true
        on error errorMessage
            display dialog "프레젠테이션 생성 오류: " & errorMessage
            return false
        end try
    end tell
end createPresentationFromTemplate

-- 슬라이드 추가 함수 (레이아웃 지정)
on addSlideWithLayout(layoutName, slideTitle, slideContent, imagePath)
    tell application "Keynote"
        tell front document
            try
                -- 새 슬라이드 생성
                set newSlide to make new slide with properties {base layout:layout layoutName}
                
                -- 제목 설정
                if slideTitle is not "" then
                    try
                        set object text of text item 1 of newSlide to slideTitle
                    on error
                        -- 제목 텍스트 상자가 없는 경우 무시
                    end try
                end if
                
                -- 내용 설정
                if slideContent is not "" then
                    try
                        -- 두 번째 텍스트 상자에 내용 추가
                        if (count of text items of newSlide) ≥ 2 then
                            set object text of text item 2 of newSlide to slideContent
                        end if
                    on error
                        -- 내용 텍스트 상자가 없는 경우 무시
                    end try
                end if
                
                -- 이미지 추가
                if imagePath is not "" then
                    try
                        set imageFile to POSIX file imagePath
                        set newImage to make new image at newSlide with properties {file:imageFile}
                        
                        -- 이미지 위치 및 크기 조정
                        set position of newImage to {400, 150}
                        set size of newImage to {300, 200}
                    on error imageError
                        display dialog "이미지 추가 오류: " & imageError
                    end try
                end if
                
                return true
            on error slideError
                display dialog "슬라이드 추가 오류: " & slideError
                return false
            end try
        end tell
    end tell
end addSlideWithLayout

-- 이미지 추가 함수 (현재 슬라이드에)
on addImageToCurrentSlide(imagePath, position, imageSize)
    tell application "Keynote"
        tell front document
            try
                set currentSlide to slide -1 -- 마지막(현재) 슬라이드
                set imageFile to POSIX file imagePath
                set newImage to make new image at currentSlide with properties {file:imageFile}
                
                -- 위치별 설정
                if position is "right" then
                    set position of newImage to {500, 150}
                    set size of newImage to {280, 180}
                else if position is "left" then
                    set position of newImage to {50, 150}
                    set size of newImage to {280, 180}
                else if position is "center" then
                    set position of newImage to {250, 200}
                    set size of newImage to {400, 300}
                else if position is "top" then
                    set position of newImage to {200, 50}
                    set size of newImage to {400, 200}
                else if position is "bottom" then
                    set position of newImage to {200, 350}
                    set size of newImage to {400, 150}
                end if
                
                -- 크기별 조정
                if imageSize is "small" then
                    set size of newImage to {200, 150}
                else if imageSize is "large" then
                    set size of newImage to {500, 350}
                end if
                
                return true
            on error imageError
                display dialog "이미지 추가 오류: " & imageError
                return false
            end try
        end tell
    end tell
end addImageToCurrentSlide

-- 프레젠테이션 저장 함수
on savePresentation(outputPath)
    tell application "Keynote"
        tell front document
            try
                save in POSIX file outputPath
                return true
            on error saveError
                display dialog "저장 오류: " & saveError
                return false
            end try
        end tell
    end tell
end savePresentation

-- 사용 가능한 레이아웃 목록 가져오기
on getAvailableLayouts()
    tell application "Keynote"
        tell front document
            try
                set layoutList to {}
                repeat with i from 1 to count of layouts of theme of front document
                    set layoutName to name of layout i of theme of front document
                    set end of layoutList to layoutName
                end repeat
                return layoutList
            on error
                -- 기본 레이아웃 반환
                return {"Title & Subtitle", "Title & Bullets", "Title, Bullets & Photo", "Photo - 3 Up", "Blank"}
            end try
        end tell
    end tell
end getAvailableLayouts

-- 테마 정보 가져오기
on getThemeInfo()
    tell application "Keynote"
        tell front document
            try
                set themeName to name of theme of front document
                set themeSize to slide size of theme of front document
                return {themeName:themeName, slideSize:themeSize}
            on error
                return {themeName:"Unknown", slideSize:"1024x768"}
            end try
        end tell
    end tell
end getThemeInfo

-- 슬라이드 개수 가져오기
on getSlideCount()
    tell application "Keynote"
        tell front document
            try
                return count of slides
            on error
                return 0
            end try
        end tell
    end tell
end getSlideCount

-- 특정 슬라이드로 이동
on goToSlide(slideNumber)
    tell application "Keynote"
        tell front document
            try
                show slide slideNumber
                return true
            on error
                return false
            end try
        end tell
    end tell
end goToSlide

-- 프레젠테이션 시작
on startPresentation()
    tell application "Keynote"
        tell front document
            try
                start
                return true
            on error
                return false
            end try
        end tell
    end tell
end startPresentation

-- 프레젠테이션 정지
on stopPresentation()
    tell application "Keynote"
        try
            stop
            return true
        on error
            return false
        end try
    end tell
end stopPresentation

-- 텍스트 서식 설정
on formatText(slideNumber, textItemNumber, fontName, fontSize, textColor)
    tell application "Keynote"
        tell front document
            try
                tell slide slideNumber
                    tell text item textItemNumber
                        set font of object text to fontName
                        set size of object text to fontSize
                        -- 색상 설정은 Keynote 버전에 따라 다를 수 있음
                    end tell
                end tell
                return true
            on error formatError
                display dialog "텍스트 서식 오류: " & formatError
                return false
            end try
        end tell
    end tell
end formatText

-- 슬라이드 복제
on duplicateSlide(slideNumber)
    tell application "Keynote"
        tell front document
            try
                set sourceSlide to slide slideNumber
                set newSlide to duplicate sourceSlide
                return true
            on error
                return false
            end try
        end tell
    end tell
end duplicateSlide

-- 슬라이드 삭제
on deleteSlide(slideNumber)
    tell application "Keynote"
        tell front document
            try
                delete slide slideNumber
                return true
            on error
                return false
            end try
        end tell
    end tell
end deleteSlide

-- 발표자 노트 추가
on addPresenterNotes(slideNumber, noteText)
    tell application "Keynote"
        tell front document
            try
                tell slide slideNumber
                    set presenter notes to noteText
                end tell
                return true
            on error
                return false
            end try
        end tell
    end tell
end addPresenterNotes

-- PDF로 내보내기
on exportToPDF(outputPath)
    tell application "Keynote"
        tell front document
            try
                export to POSIX file outputPath as PDF
                return true
            on error exportError
                display dialog "PDF 내보내기 오류: " & exportError
                return false
            end try
        end tell
    end tell
end exportToPDF

-- PowerPoint로 내보내기
on exportToPowerPoint(outputPath)
    tell application "Keynote"
        tell front document
            try
                export to POSIX file outputPath as Microsoft PowerPoint
                return true
            on error exportError
                display dialog "PowerPoint 내보내기 오류: " & exportError
                return false
            end try
        end tell
    end tell
end exportToPowerPoint

-- 간단한 테스트 함수
on testKeynoteConnection()
    tell application "Keynote"
        try
            activate
            set appVersion to version
            display dialog "Keynote 연결 성공! 버전: " & appVersion
            return true
        on error connectionError
            display dialog "Keynote 연결 실패: " & connectionError
            return false
        end try
    end tell
end testKeynoteConnection

-- 메인 실행 함수 (테스트용)
on run
    display dialog "🍎 Keynote Controller AppleScript가 로드되었습니다!" buttons {"테스트", "취소"} default button "테스트"
    
    if button returned of result is "테스트" then
        testKeynoteConnection()
    end if
end run
