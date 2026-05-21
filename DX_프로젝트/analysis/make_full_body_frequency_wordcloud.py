import csv
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "pregnant_full_body"
SOURCE_TXT = DATA_DIR / "pregnant_full_body_only_pipe_4000.txt"
FREQ_CSV = DATA_DIR / "pregnant_full_body_word_frequency.csv"
WORDCLOUD_DIR = DATA_DIR / "wordclouds"
WORDCLOUD_DIR.mkdir(exist_ok=True)

STOPWORDS = {
    "임신", "임산부", "일지", "일기", "다이어리", "스트레스", "오늘", "정도", "진짜",
    "너무", "그냥", "이제", "하루", "이번", "저는", "제가", "우리", "때문", "생각",
    "느낌", "블로그", "포스팅", "사진", "댓글", "공감", "네이버", "입니다", "합니다",
    "있는", "없는", "해서", "하고", "하면", "부터", "까지", "같아요", "그리고",
    "하지만", "그래서", "다시", "많이", "조금", "완전", "정말", "하나", "요즘",
    "계속", "처음", "마지막", "관련", "사람", "부분", "보기", "본문", "카테고리",
    "이웃", "로그인", "검색", "기능", "기타", "바로가기", "열기", "크게", "전체",
    "출산", "아기", "육아", "신생아", "수유", "태아", "엄마", "있어요", "있다",
    "했다", "했다가", "되는", "위해", "같은", "이렇게", "벌써", "가장", "바로",
    "함께", "내가", "나는", "나의", "좋은", "좋다", "사실", "하는", "없어",
    "없이", "안녕하세요", "이번에", "전에", "내돈내산", "광고", "협찬", "문의",
    "예약", "주소", "전화", "클릭", "확인", "추천", "후기", "정보", "준비",
}


def tokenize(text):
    words = re.findall(r"[가-힣]{2,}", text)
    return [word for word in words if word not in STOPWORDS and len(word) >= 2]


def get_font(size):
    for path in [
        "C:/Windows/Fonts/malgunbd.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/gulim.ttc",
    ]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_wordcloud(freq, path, title):
    width, height = 1600, 1000
    image = Image.new("RGB", (width, height), "#FFFDF7")
    draw = ImageDraw.Draw(image)
    random.seed(42)
    palette = ["#A71930", "#204B57", "#2F6F5E", "#C47A22", "#1F2421", "#6B3E75", "#D44731"]
    top_words = freq.most_common(100)

    draw.text((42, 30), title, font=get_font(46), fill="#1F2421")

    if not top_words:
        draw.text((80, 120), "단어가 없습니다.", font=get_font(42), fill="#1F2421")
        image.save(path)
        return

    max_count = top_words[0][1]
    min_count = top_words[-1][1]
    placed = []

    def intersects(box):
        x1, y1, x2, y2 = box
        for px1, py1, px2, py2 in placed:
            if not (x2 < px1 or px2 < x1 or y2 < py1 or py2 < y1):
                return True
        return False

    for rank, (word, count) in enumerate(top_words):
        ratio = (count - min_count) / (max_count - min_count + 1e-9)
        size = int(20 + 118 * (ratio ** 0.55))
        if rank < 5:
            size += 24 - rank * 4

        font = get_font(size)
        bbox = draw.textbbox((0, 0), word, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        color = palette[rank % len(palette)]

        placed_ok = False
        for attempt in range(900):
            if rank < 10 and attempt < 260:
                x = random.randint(max(40, width // 2 - 440), min(width - text_width - 40, width // 2 + 300))
                y = random.randint(120, min(height - text_height - 40, 560))
            else:
                x = random.randint(36, max(37, width - text_width - 36))
                y = random.randint(100, max(101, height - text_height - 36))
            box = (x - 10, y - 10, x + text_width + 10, y + text_height + 10)
            if not intersects(box):
                draw.text((x, y), word, font=font, fill=color)
                placed.append(box)
                placed_ok = True
                break

        if not placed_ok and rank < 45:
            font = get_font(max(22, int(size * 0.68)))
            bbox = draw.textbbox((0, 0), word, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            for _ in range(450):
                x = random.randint(36, max(37, width - text_width - 36))
                y = random.randint(100, max(101, height - text_height - 36))
                box = (x - 8, y - 8, x + text_width + 8, y + text_height + 8)
                if not intersects(box):
                    draw.text((x, y), word, font=font, fill=color)
                    placed.append(box)
                    break

    image.save(path)


def main():
    category_freq = defaultdict(Counter)
    total_freq = Counter()

    with SOURCE_TXT.open(encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("||", 2)
            if len(parts) != 3:
                continue
            crawling_word, _, content = parts
            tokens = tokenize(content)
            category_freq[crawling_word].update(tokens)
            total_freq.update(tokens)

    with FREQ_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["crawling_word", "word", "count"])
        for word, count in total_freq.most_common(300):
            writer.writerow(["전체", word, count])
        for crawling_word, freq in category_freq.items():
            for word, count in freq.most_common(300):
                writer.writerow([crawling_word, word, count])

    make_wordcloud(total_freq, WORDCLOUD_DIR / "전체_wordcloud.png", "전체 키워드 빈도")
    for crawling_word, freq in category_freq.items():
        make_wordcloud(freq, WORDCLOUD_DIR / f"{crawling_word}_wordcloud.png", crawling_word)

    print(FREQ_CSV)
    print(WORDCLOUD_DIR)
    for word, count in total_freq.most_common(20):
        print(f"{word}: {count}")


if __name__ == "__main__":
    main()
