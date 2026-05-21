import re
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "pregnant_full_body"
SOURCE_TXT = DATA_DIR / "pregnant_full_body_pipe_4000.txt"
CLEAN_TXT = DATA_DIR / "pregnant_full_body_only_pipe_4000.txt"

CUT_MARKERS = [
    '{"title":',
    "닫기 카테고리",
    "function ImageLazyLoader",
    "이 블로그 홈",
    "님을 이웃추가하고",
]


def clean_content(content):
    for marker in CUT_MARKERS:
        idx = content.find(marker)
        if idx >= 0:
            content = content[:idx]
    content = content.replace("class=\"se-main-container\">", " ")
    content = re.sub(r"\s+", " ", content)
    return content.strip()


def main():
    counts = Counter()
    rows = 0
    with SOURCE_TXT.open(encoding="utf-8") as src, CLEAN_TXT.open("w", encoding="utf-8") as out:
        for line in src:
            parts = line.rstrip("\n").split("||", 2)
            if len(parts) != 3:
                continue
            crawling_word, url, content = parts
            content = clean_content(content)
            if not content:
                continue
            out.write(f"{crawling_word}||{url}||{content}\n")
            counts[crawling_word] += 1
            rows += 1

    print(f"{rows} rows saved")
    for key, value in counts.items():
        print(f"{key}: {value}")
    print(CLEAN_TXT)


if __name__ == "__main__":
    main()
