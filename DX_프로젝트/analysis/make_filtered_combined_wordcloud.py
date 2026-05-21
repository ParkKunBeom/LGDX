import csv
import hashlib
import random
import re
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "pregnant_full_body"
SOURCE_TXT = DATA_DIR / "pregnant_full_body_only_pipe_4000.txt"
OUT_DIR = DATA_DIR / "filtered_combined"
OUT_DIR.mkdir(exist_ok=True)

FILTERED_TXT = OUT_DIR / "pregnant_filtered_combined_pipe.txt"
REMOVED_CSV = OUT_DIR / "removed_duplicates_ads.csv"
FREQ_CSV = OUT_DIR / "filtered_combined_word_frequency.csv"
WORDCLOUD_PATH = OUT_DIR / "filtered_combined_wordcloud.png"

AD_PATTERNS = [
    "소정의 원고료", "원고료를", "원고료 지급", "광고비", "광고료",
    "제품을 제공", "제품 제공", "서비스를 제공", "서비스 제공", "무료 제공",
    "협찬", "체험단", "서포터즈", "공동구매", "공구", "업체로부터",
    "브랜드로부터", "업체에서", "브랜드에서", "제휴", "파트너스",
    "쿠팡 파트너스", "구매 링크", "구매링크", "할인코드", "할인 코드",
    "예약문의", "예약 문의", "상담문의", "상담 문의", "문의주세요",
    "문의 주세요", "카카오톡 문의", "톡톡 문의", "오픈채팅",
    "이 포스팅은", "본 포스팅은", "해당 포스팅은", "유료광고",
    "대가를", "경제적 대가", "광고입니다",
]

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
    "먹고", "다른", "있어서", "시간", "그래도", "근데", "같이", "엄청", "특히",
    "있습니다", "했는데", "이런", "같다", "거의", "한다", "보고", "하면",
    "대한", "동안", "위한", "통해", "또는", "에서", "에게", "보다", "아래",
    "위에", "여기", "저기", "관련된", "가능", "사용", "경우", "방법",
    "체크인", "블로그의", "장소의", "오늘은", "시간이", "것도", "지금", "아주",
    "있고", "해요", "많은", "가서", "먹는", "아직", "자주", "열심히", "생각보다",
    "갑자기", "것이", "일차", "매일", "해서는", "같아서", "있는데", "싶은", "때문에",
    "있었다", "있다고"
}


def normalize_content(text):
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"#[가-힣A-Za-z0-9_]+", " ", text)
    text = re.sub(r"[^가-힣A-Za-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def content_fingerprint(text):
    normalized = normalize_content(text)
    tokens = normalized.split()
    sample = " ".join(tokens[:450])
    return hashlib.sha1(sample.encode("utf-8")).hexdigest()


def is_ad(content):
    compact = re.sub(r"\s+", " ", content)
    matched = [pattern for pattern in AD_PATTERNS if pattern in compact]
    if len(matched) >= 1:
        return True, matched[0]

    promotional_score = 0
    promotional_score += len(re.findall(r"문의|예약|상담|링크|할인|이벤트|체험|제공", compact))
    promotional_score += len(re.findall(r"센터|업체|브랜드|제품|구매|가격|비용", compact))
    if promotional_score >= 12 and len(compact) < 5000:
        return True, f"광고성 키워드 점수 {promotional_score}"
    return False, ""


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


def make_wordcloud(freq):
    width, height = 1700, 1050
    image = Image.new("RGB", (width, height), "#FFFDF7")
    draw = ImageDraw.Draw(image)
    random.seed(2027)
    palette = ["#A71930", "#204B57", "#2F6F5E", "#C47A22", "#1F2421", "#6B3E75", "#D44731"]
    top_words = freq.most_common(110)

    draw.text((46, 34), "전체 통합 정제본 키워드 워드클라우드", font=get_font(46), fill="#1F2421")
    if not top_words:
        image.save(WORDCLOUD_PATH)
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
        size = int(22 + 126 * (ratio ** 0.56))
        if rank < 5:
            size += 24 - rank * 4

        font = get_font(size)
        bbox = draw.textbbox((0, 0), word, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        color = palette[rank % len(palette)]

        placed_ok = False
        for attempt in range(1000):
            if rank < 10 and attempt < 300:
                x = random.randint(max(42, width // 2 - 500), min(width - text_width - 42, width // 2 + 360))
                y = random.randint(130, min(height - text_height - 42, 600))
            else:
                x = random.randint(38, max(39, width - text_width - 38))
                y = random.randint(108, max(109, height - text_height - 38))
            box = (x - 10, y - 10, x + text_width + 10, y + text_height + 10)
            if not intersects(box):
                draw.text((x, y), word, font=font, fill=color)
                placed.append(box)
                placed_ok = True
                break

        if not placed_ok and rank < 50:
            font = get_font(max(22, int(size * 0.68)))
            bbox = draw.textbbox((0, 0), word, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            for _ in range(500):
                x = random.randint(38, max(39, width - text_width - 38))
                y = random.randint(108, max(109, height - text_height - 38))
                box = (x - 8, y - 8, x + text_width + 8, y + text_height + 8)
                if not intersects(box):
                    draw.text((x, y), word, font=font, fill=color)
                    placed.append(box)
                    break

    image.save(WORDCLOUD_PATH)


def main():
    seen_urls = set()
    seen_fingerprints = set()
    freq = Counter()
    kept = 0
    removed = Counter()

    with (
        SOURCE_TXT.open(encoding="utf-8") as src,
        FILTERED_TXT.open("w", encoding="utf-8") as out,
        REMOVED_CSV.open("w", encoding="utf-8-sig", newline="") as removed_file,
    ):
        writer = csv.writer(removed_file)
        writer.writerow(["reason", "crawling_word", "url", "detail"])

        for line in src:
            parts = line.rstrip("\n").split("||", 2)
            if len(parts) != 3:
                continue
            crawling_word, url, content = parts

            if url in seen_urls:
                removed["duplicate_url"] += 1
                writer.writerow(["duplicate_url", crawling_word, url, ""])
                continue
            seen_urls.add(url)

            fingerprint = content_fingerprint(content)
            if fingerprint in seen_fingerprints:
                removed["duplicate_content"] += 1
                writer.writerow(["duplicate_content", crawling_word, url, ""])
                continue
            seen_fingerprints.add(fingerprint)

            ad, reason = is_ad(content)
            if ad:
                removed["ad"] += 1
                writer.writerow(["ad", crawling_word, url, reason])
                continue

            out.write(f"{crawling_word}||{url}||{content}\n")
            freq.update(tokenize(content))
            kept += 1

    with FREQ_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "count"])
        writer.writerows(freq.most_common(500))

    make_wordcloud(freq)

    print(f"kept: {kept}")
    for key, value in removed.items():
        print(f"removed_{key}: {value}")
    print(FILTERED_TXT)
    print(FREQ_CSV)
    print(WORDCLOUD_PATH)
    for word, count in freq.most_common(30):
        print(f"{word}: {count}")


if __name__ == "__main__":
    main()
