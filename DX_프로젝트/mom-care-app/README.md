# ThinQ Mom Care App

임산부 모드와 보호자 모드를 가진 임신 케어 앱 MVP입니다.  
프론트 화면과 백엔드 API가 함께 들어 있습니다.

## VS Code에서 실행

1. VS Code에서 `C:\Users\Park_kunbeom\Desktop\LGDX` 또는 `C:\Users\Park_kunbeom\Desktop\LGDX\DX_프로젝트\mom-care-app` 폴더를 엽니다.
2. `F5`를 누릅니다.
3. `Open ThinQ Mom Care`를 선택합니다.
4. 자동으로 서버가 켜지고 `http://localhost:5173`이 열립니다.

실행이 안 되면 아래 파일을 더블클릭하세요.

```text
C:\Users\Park_kunbeom\Desktop\LGDX\DX_프로젝트\mom-care-app\open-app.cmd
```

## 터미널로 직접 실행

```powershell
cd C:\Users\Park_kunbeom\Desktop\LGDX\DX_프로젝트\mom-care-app
node server.mjs
```

브라우저에서 아래 주소로 접속합니다.

```text
http://localhost:5173
```

백엔드 연결 확인 주소:

```text
http://localhost:5173/api/health
```

## 백엔드 API

| 기능 | 메서드 | 주소 | 설명 |
| --- | --- | --- | --- |
| 서버 상태 | GET | `/api/health` | 백엔드 실행 여부 확인 |
| 임산부 평가 | POST | `/api/assessments` | 임신 주차, 증상, 스트레스, 상황 입력 후 위험도와 케어 루틴 반환 |
| AI 추천 | GET | `/api/recommendations?week=24&symptom=sleep` | 주차와 증상 기준 추천 |
| 보호자 체크리스트 | GET | `/api/guardian/tasks` | 보호자가 챙길 일 반환 |
| 다이어리 조회 | GET | `/api/diaries` | 저장된 일지 조회 |
| 다이어리 저장 | POST | `/api/diaries` | 산모 일지 저장 |
| 커뮤니티 조회 | GET | `/api/community/posts` | 커뮤니티형 공감 일지 조회 |
| 커뮤니티 작성 | POST | `/api/community/posts` | 커뮤니티 게시글 저장 |
| 커뮤니티 신고 | POST | `/api/community/posts/{id}/report` | 허위 정보 의심 게시글 신고 |
| 신뢰 출처 | GET | `/api/trust/sources` | 공신력 출처와 AI 답변 원칙 반환 |
| 가전 제어 | POST | `/api/appliances/control` | ThinQ 제어 요청 시뮬레이션 저장 |
| 구독 | POST | `/api/subscriptions` | 광고 제거 구독 상태 저장 |

## 데이터 저장

백엔드 데이터는 아래 JSON 파일에 저장됩니다.

```text
backend-data/store.json
```

처음 서버를 실행하면 자동으로 생성됩니다.

## 다음 개발 후보

- 실제 AI API 연결
- 공공 보건/식품 영양 데이터 API 연결
- LG ThinQ API 연동
- 로그인, 보호자 초대, 커뮤니티 신고 관리 화면
- 모바일 앱 전환: React Native 또는 Flutter
