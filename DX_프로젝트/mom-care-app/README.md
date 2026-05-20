# ThinQ Mom Care App

임산부 모드와 보호자 모드를 가진 임신 케어 앱 MVP입니다.

## VS Code에서 실행: 가장 쉬운 방법

1. VS Code에서 `C:\Users\Park_kunbeom\Desktop\LGDX\DX_프로젝트\mom-care-app` 폴더를 엽니다.
2. 왼쪽 실행 및 디버그 메뉴를 엽니다.
3. `Open ThinQ Mom Care`를 선택하고 `F5`를 누릅니다.

서버 없이 브라우저에서 바로 실행되도록 세팅되어 있습니다.

## 서버로 실행하고 싶을 때

PC에 Node.js가 설치되어 있다면 터미널에서 아래 명령어를 실행합니다.

```powershell
node server.mjs
```

브라우저에서 `http://localhost:5173`으로 접속합니다.

Node.js가 없다면 설치 없이 `public/index.html` 파일을 브라우저로 열어도 됩니다.

## GitHub Pages 배포

루트 저장소의 GitHub Actions가 `DX_프로젝트/mom-care-app/public` 폴더만 GitHub Pages로 배포합니다.

1. 변경사항을 `main` 브랜치에 push합니다.
2. GitHub 저장소에서 `Settings > Pages`로 이동합니다.
3. `Build and deployment`의 `Source`를 `GitHub Actions`로 설정합니다.
4. `Actions` 탭에서 `Deploy Mom Care App` 실행이 끝나면 배포 주소가 표시됩니다.

## 포함 기능

- 임신 주차, 불편사항, 스트레스 지수 기반 케어 루틴 추천
- 음식, 행동, 정신케어 추천
- LG ThinQ 가전 제어 추천 시뮬레이션
- 보호자 체크리스트와 공유 알림
- 맘 다이어리 저장
- 커뮤니티형 일지 화면
- 광고 영역과 구독 시뮬레이션
- 신뢰 정보 기준과 API 연동 후보 정리

## 다음 개발 후보

- 실제 AI API 연결
- 공공 보건/식품 영양 데이터 API 연결
- LG ThinQ API 연동
- 로그인, 보호자 초대, 커뮤니티 신고 기능
- 모바일 앱 전환: React Native 또는 Flutter
