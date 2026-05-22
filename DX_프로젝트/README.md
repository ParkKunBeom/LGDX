# DX 프로젝트 폴더 안내

소스별로 코드와 결과 폴더를 같이 볼 수 있게 정리했습니다. 예를 들어 네이버 지식인은 `naverjisik` 폴더 안에 실행 코드와 `임산부_힘듦_naverjisik` 같은 수집 결과 폴더가 같이 있습니다.

## 전체 구조

```text
DX_프로젝트/
  naverblog/     네이버 블로그 크롤링 코드와 블로그 결과 폴더
  navercafe/     네이버 카페 크롤링 코드와 카페 결과 폴더
  naverjisik/    네이버 지식인 크롤링 코드와 지식인 결과 폴더
  analysis/      예전 4000개 통합 데이터 분석 코드와 결과
  docs/          발표자료
  mom-care-app/  맘다이어리 앱 코드
  README.md
```

## 네이버 블로그

위치:

```text
naverblog/naverblog_검색키워드.py
```

역할:

- 네이버 블로그 검색 결과에서 본문을 수집합니다.
- 검색 키워드와 크롤링 수를 입력하면 실행됩니다.
- 같은 키워드로 다시 실행하면 기존 URL/본문 중복을 제외하고 추가 수집합니다.
- 빈도수 CSV와 워드클라우드 PNG를 같이 만듭니다.

저장 예시:

```text
naverblog/임산부_다이어리_naverblog/
  naverblog_raw_pipe.txt
  naverblog_filtered_pipe.txt
  naverblog_word_frequency.csv
  naverblog_wordcloud.png
  removed_duplicates_ads.csv
  summary.csv
```

실행:

```powershell
& "C:\Users\Park_kunbeom\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -u "C:\Users\Park_kunbeom\Desktop\LGDX\DX_프로젝트\naverblog\naverblog_검색키워드.py"
```

## 네이버 카페

위치:

```text
navercafe/navercafe_검색키워드.py
```

역할:

- 네이버 카페 검색 결과에서 본문을 수집합니다.
- 로그인 브라우저 옵션을 사용하면 사용자가 실제로 볼 수 있는 카페 글만 본문 수집을 시도합니다.
- 권한 없는 글, 삭제된 글, 본문 추출이 안 되는 글은 건너뜁니다.
- 빈도수 CSV와 워드클라우드 PNG를 같이 만듭니다.

저장 예시:

```text
navercafe/임산부_다이어리_navercafe/
  navercafe_raw_pipe.txt
  navercafe_filtered_pipe.txt
  navercafe_word_frequency.csv
  navercafe_wordcloud.png
  removed_duplicates_ads.csv
  summary.csv
```

실행:

```powershell
& "C:\Users\Park_kunbeom\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -u "C:\Users\Park_kunbeom\Desktop\LGDX\DX_프로젝트\navercafe\navercafe_검색키워드.py"
```

로그인 브라우저 실행:

```powershell
& "C:\Users\Park_kunbeom\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -u "C:\Users\Park_kunbeom\Desktop\LGDX\DX_프로젝트\navercafe\navercafe_검색키워드.py" --keyword "임산부 다이어리" --count 1000 --use-browser-login
```

## 네이버 지식인

위치:

```text
naverjisik/naverjisik_검색키워드.py
```

역할:

- 네이버 지식인 검색 결과에서 질문자 본문만 수집합니다.
- 답변자 본문은 저장하지 않습니다.
- 75페이지 연속 새 저장 글이 없으면 자동 종료합니다.
- 저장 파일명에도 검색 키워드가 붙습니다.
- 빈도수 CSV와 워드클라우드 PNG를 같이 만듭니다.

저장 예시:

```text
naverjisik/임산부_힘듦_naverjisik/
  임산부_힘듦_naverjisik_raw_pipe.txt
  임산부_힘듦_naverjisik_filtered_pipe.txt
  임산부_힘듦_naverjisik_word_frequency.csv
  임산부_힘듦_naverjisik_wordcloud.png
  임산부_힘듦_naverjisik_removed_duplicates_ads.csv
  임산부_힘듦_naverjisik_summary.csv
```

실행:

```powershell
& "C:\Users\Park_kunbeom\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -u "C:\Users\Park_kunbeom\Desktop\LGDX\DX_프로젝트\naverjisik\naverjisik_검색키워드.py"
```

## 분석 코드

위치:

```text
analysis/
```

주요 파일:

- `make_filtered_combined_wordcloud.py`: 기존 4000개 본문 데이터를 중복/광고 제외 후 빈도수와 워드클라우드로 재생성합니다.
- `make_full_body_frequency_wordcloud.py`: 기존 본문 txt에서 빈도수와 워드클라우드를 만듭니다.
- `clean_full_body_pipe_txt.py`: 수집 본문을 정리하는 보조 코드입니다.

예전 크롤링 실험 코드는 현재 `naverblog`, `navercafe`, `naverjisik` 전용 코드와 기능이 겹쳐서 정리했습니다.

## GitHub 업로드 기준

GitHub에는 코드와 설명 문서 위주로 올리고, 크롤링 결과물과 로컬 설치 패키지는 제외합니다.

제외 대상:

- `.python_packages/`
- `naverblog/*_naverblog/`
- `navercafe/*_navercafe/`
- `navercafe/_naver_cafe_chrome_profile/`
- `naverjisik/*_naverjisik/`
- `analysis/pregnant_full_body/`
- `__pycache__/`, `*.pyc`

업로드 가능:

- `naverblog/naverblog_검색키워드.py`
- `navercafe/navercafe_검색키워드.py`
- `naverjisik/naverjisik_검색키워드.py`
- `analysis/*.py`
- `README.md`
- `docs/`
- `mom-care-app/`

## 다른 사람에게 공유할 때

`.py` 파일만 전달한다고 모든 PC에서 바로 자동 실행되는 것은 아닙니다. 실행하는 사람의 PC에도 Python과 필요한 패키지가 있어야 합니다.

필요한 것:

- Python 3.10 이상 권장
- 인터넷 연결
- `pillow`: 워드클라우드 이미지 생성용
- `selenium`: 네이버 카페 로그인 브라우저 기능을 사용할 때 필요

패키지 설치:

```powershell
pip install -r requirements.txt
```

만약 `pip` 명령이 안 되면 Python을 직접 지정해서 설치합니다.

```powershell
python -m pip install -r requirements.txt
```

소스별 실행 가능 조건:

- `naverblog/naverblog_검색키워드.py`: 공개 네이버 블로그 검색 결과 기준으로 실행됩니다.
- `naverjisik/naverjisik_검색키워드.py`: 공개 네이버 지식인 질문 본문 기준으로 실행됩니다.
- `navercafe/navercafe_검색키워드.py`: 공개 카페 글은 일반 수집을 시도하고, 로그인 브라우저 옵션은 Selenium 설치 후 직접 네이버 로그인이 필요합니다.

주의할 점:

- 네이버 카페 비공개 글, 등급 제한 글, 가입하지 않은 카페 글은 코드만으로 가져올 수 없습니다.
- 로그인 브라우저를 써도 실제 로그인 계정이 볼 수 있는 글만 수집됩니다.
- 네이버 페이지 구조가 바뀌면 본문 추출 코드도 수정이 필요할 수 있습니다.
- 크롤링 결과 폴더는 GitHub에 올리지 않는 것을 기준으로 합니다.
