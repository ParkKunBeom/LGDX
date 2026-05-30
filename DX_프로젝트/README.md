# DX 프로젝트 크롤링 코드

네이버 블로그, 네이버 카페, 네이버 지식인, 맘스홀릭베이비 카페 글을 검색 키워드 기준으로 수집하고 텍스트 빈도 분석과 워드클라우드를 생성하는 코드입니다.

## 폴더 구조

```text
DX_프로젝트/
  naverblog/
    naverblog_검색키워드.py
  navercafe/
    navercafe_검색키워드.py
  naverjisik/
    naverjisik_검색키워드.py
  맘스홀릭_크롤링/
    맘스홀릭_크롤링.py
  requirements.txt
  README.md
```

## 공통 기능

- 실행 시 검색 키워드와 크롤링 수를 입력할 수 있습니다.
- 같은 키워드로 다시 실행하면 기존 저장 URL/본문 중복을 제외하고 추가 수집합니다.
- 광고성 글, 중복 URL, 중복 본문을 제거합니다.
- `kiwipiepy`가 있으면 Kiwi 형태소 분석으로 명사 중심 빈도 분석을 합니다.
- `kiwipiepy`가 없으면 자동 설치를 시도하고, 실패하면 기존 정규식 방식으로 분석합니다.
- 검색 키워드 자체와 키워드 명사 변형은 빈도 분석에서 제외합니다.
  예: `남편` 검색 시 `남편`, `남편은`, `남편의`, `남편에게` 같은 표현이 워드클라우드에 덜 나오도록 처리합니다.
- `wordcloud` 라이브러리가 있으면 주피터 노트북에서 만든 것과 같은 방식의 워드클라우드를 생성합니다.
- 원본 TXT, 원본 CSV, 정제 TXT, 정제 CSV, 단어 빈도 CSV, 워드클라우드 PNG, 요약 CSV를 저장합니다.

## 설치

```powershell
pip install -r requirements.txt
```

`pip` 명령이 안 되면 Python을 직접 지정합니다.

```powershell
python -m pip install -r requirements.txt
```

필요 패키지:

- `pillow`
- `selenium`
- `wordcloud`
- `kiwipiepy`

각 스크립트는 필요한 패키지가 없을 때 `.python_packages/` 폴더에 자동 설치를 시도합니다.

## 네이버 블로그

위치:

```text
naverblog/naverblog_검색키워드.py
```

실행:

```powershell
python DX_프로젝트\naverblog\naverblog_검색키워드.py
```

예시:

```powershell
python DX_프로젝트\naverblog\naverblog_검색키워드.py --keyword "임산부 가사분담" --count 3000
```

저장 예시:

```text
naverblog/임산부_가사분담_naverblog/
  naverblog_raw_pipe.txt
  naverblog_raw.csv
  naverblog_filtered_pipe.txt
  naverblog_filtered.csv
  naverblog_word_frequency.csv
  naverblog_wordcloud.png
  removed_duplicates_ads.csv
  summary.csv
```

## 네이버 카페

위치:

```text
navercafe/navercafe_검색키워드.py
```

실행:

```powershell
python DX_프로젝트\navercafe\navercafe_검색키워드.py
```

로그인이 필요한 카페 글까지 수집하려면 실행 중 로그인 브라우저 사용을 선택하거나 옵션을 붙입니다.

```powershell
python DX_프로젝트\navercafe\navercafe_검색키워드.py --keyword "임산부 다이어리" --count 1000 --use-browser-login
```

주의:

- 비공개 글, 등급 제한 글, 가입하지 않은 카페 글은 로그인해도 볼 수 없으면 수집할 수 없습니다.
- 본문 선택자를 우선 사용하고 댓글, 이전글, 다음글, 목록 영역은 제거합니다.

## 네이버 지식인

위치:

```text
naverjisik/naverjisik_검색키워드.py
```

실행:

```powershell
python DX_프로젝트\naverjisik\naverjisik_검색키워드.py
```

예시:

```powershell
python DX_프로젝트\naverjisik\naverjisik_검색키워드.py --keyword "임산부 돌봄" --count 1000
```

특징:

- 지식인 질문 본문 중심으로 수집합니다.
- 답변 본문은 저장하지 않습니다.
- 75페이지 연속 새 저장 글이 없으면 자동 종료합니다.
- Kiwi 형태소 분석과 WordCloud 방식이 다른 크롤러와 동일하게 적용됩니다.

## 맘스홀릭베이비 카페

위치:

```text
맘스홀릭_크롤링/맘스홀릭_크롤링.py
```

대상 카페:

```text
https://cafe.naver.com/imsanbu
```

실행:

```powershell
python DX_프로젝트\맘스홀릭_크롤링\맘스홀릭_크롤링.py
```

예시:

```powershell
python DX_프로젝트\맘스홀릭_크롤링\맘스홀릭_크롤링.py --keyword "남편" --count 1000
```

동작 방식:

- API 키를 사용하지 않습니다.
- 항상 로그인 브라우저 방식으로 본문을 수집합니다.
- 실행하면 크롬 로그인 창이 열립니다.
- 네이버 로그인 후 터미널에서 Enter를 누르면 수집을 시작합니다.
- 맘스홀릭베이비 카페 안에서만 검색합니다.
- 댓글, 이전글, 다음글, 목록 영역을 제거하고 본문 후보 영역만 저장합니다.

저장 예시:

```text
맘스홀릭_크롤링/남편_맘스홀릭/
  moms_holic_raw_pipe.txt
  moms_holic_raw.csv
  moms_holic_filtered_pipe.txt
  moms_holic_filtered.csv
  moms_holic_word_frequency.csv
  moms_holic_wordcloud.png
  removed_duplicates_ads.csv
  summary.csv
```

## GitHub 업로드 기준

GitHub에는 코드와 문서만 올리고, 크롤링 결과와 로그인 프로필은 올리지 않습니다.

올릴 파일:

```text
DX_프로젝트/README.md
DX_프로젝트/requirements.txt
DX_프로젝트/naverblog/naverblog_검색키워드.py
DX_프로젝트/navercafe/navercafe_검색키워드.py
DX_프로젝트/naverjisik/naverjisik_검색키워드.py
DX_프로젝트/맘스홀릭_크롤링/맘스홀릭_크롤링.py
```

올리지 않을 파일:

```text
.python_packages/
*_naverblog/
*_navercafe/
*_naverjisik/
*_맘스홀릭/
_naver_cafe_chrome_profile/
_moms_holic_chrome_profile/
__pycache__/
*.pyc
```

## 주의

- 네이버 페이지 구조가 바뀌면 본문 추출 선택자를 수정해야 할 수 있습니다.
- 로그인 브라우저를 쓰더라도 실제 계정이 볼 수 없는 글은 수집할 수 없습니다.
- 크롤링 결과에는 개인정보가 포함될 수 있으므로 GitHub에 업로드하지 마세요.
