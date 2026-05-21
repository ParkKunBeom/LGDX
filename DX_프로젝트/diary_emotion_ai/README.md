# Diary Emotion AI

사용자가 작성한 다이어리 문장을 감정으로 분류하기 위한 실험 폴더입니다.

## 폴더 구조

- `requirements.txt`
  - 데이터셋을 다시 만들 때 필요한 파이썬 패키지 목록입니다. 감정 예측만 할 때는 설치가 필요 없습니다.
- `run_diary_emotion.cmd`
  - 더블클릭으로 실행하는 감정분석 파일입니다. Windows 기본 PowerShell로 동작합니다.
- `build_dataset.cmd`
  - 원본 엑셀 데이터로 학습 CSV를 다시 만드는 실행 파일입니다.
- `train_model.cmd`
  - 생성된 CSV로 모델을 다시 학습하는 실행 파일입니다.
- `data/source/source_info.md`
  - 원본 데이터가 어디에서 왔는지, 어떤 컬럼을 사용하는지 설명합니다.
- `data/source/raw/`
  - 원본 `018.감성대화` 폴더를 복사해 둘 위치입니다. 이 폴더는 재학습할 때만 필요합니다.
- `data/processed/diary_emotion_train.csv`
  - 학습용 데이터입니다. AI Hub 감성대화 말뭉치를 다이어리 문체로 바꾼 문장과 합성 다이어리 문장이 들어갑니다.
- `data/processed/diary_emotion_validation.csv`
  - 검증용 데이터입니다. 모델 성능을 확인할 때 사용합니다.
- `data/processed/label_map.json`
  - 감정 라벨 목록과 설명입니다.
- `data/processed/dataset_summary.json`
  - 생성된 데이터 개수와 감정별 분포 요약입니다.
- `models/diary_emotion_nb_model.json`
  - 학습된 감정분류 모델입니다.
- `reports/evaluation.json`
  - 검증 데이터 기준 정확도와 감정별 성능입니다.
- `scripts/01_build_diary_dataset.py`
  - 원본 감성대화 데이터를 읽고 다이어리형 학습 데이터를 생성합니다.
- `scripts/02_train_naive_bayes.py`
  - 생성된 CSV로 감정분류 모델을 학습합니다.
- `scripts/03_predict_diary_emotion.py`
  - Python으로 다이어리 문장의 감정을 예측합니다.
- `scripts/03_predict_diary_emotion.ps1`
  - PowerShell로 다이어리 문장의 감정을 예측합니다. 더블클릭 실행 파일이 이 스크립트를 사용합니다.

## 감정 라벨

기본 감정은 다음 7개입니다.

- `기쁨`
- `슬픔`
- `분노`
- `불안`
- `상처`
- `당황`
- `중립`

AI Hub 감성대화 말뭉치에는 `중립`이 없어서, 중립 데이터는 별도 합성 문장으로 보강했습니다.

## 실행 순서

### 1. 이미 학습된 모델로 바로 예측

아래 파일을 더블클릭하면 바로 실행됩니다.

```cmd
run_diary_emotion.cmd
```

실행 후 `Diary text>` 옆에 다이어리 문장을 입력하면 됩니다. 빈 문장으로 Enter를 누르면 종료됩니다.

Python이 설치되어 있다면 아래처럼 직접 실행할 수도 있습니다.

```cmd
python scripts\03_predict_diary_emotion.py "오늘은 아무것도 하기 싫고 계속 누워만 있었다."
```

### 2. 원본 데이터로 다시 만들고 학습

재학습하려면 `openpyxl`이 필요합니다.

```cmd
pip install -r requirements.txt
```

원본 데이터 폴더를 아래 위치에 복사합니다.

```text
data/source/raw/018.감성대화
```

그다음 실행합니다.

```cmd
build_dataset.cmd
train_model.cmd
```

원본 데이터가 다른 위치에 있으면 경로를 직접 지정할 수 있습니다.

```cmd
build_dataset.cmd --source-root "D:\data\018.감성대화"
train_model.cmd
```

## 주의점

이 모델은 실제 임상 진단 모델이 아닙니다. 다이어리의 감정 경향을 분류하는 용도입니다.
우울증, 자해 위험, 위기 감지처럼 높은 정확도가 필요한 영역은 별도 안전 설계와 전문가 검토가 필요합니다.
