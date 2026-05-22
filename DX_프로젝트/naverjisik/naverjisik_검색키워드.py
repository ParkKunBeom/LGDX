import argparse
import csv
import hashlib
import html
import random
import re
import time
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# 네이버 지식인 전용 크롤링 + 빈도 분석 + 워드클라우드
# 예시:
#   python naverjisik_검색키워드.py
#   python naverjisik_검색키워드.py --keyword "임산부 돌봄" --count 1000
#
# 저장 폴더:
#   data/임산부_돌봄_naverjisik/
# ============================================================


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR

SEARCH_PAGE_SIZE = 10
MAX_SEARCH_PAGES = 1000
MAX_NO_NEW_SAVE_PAGES = 75
SLEEP_SEARCH_SEC = 0.35
SLEEP_BODY_SEC = 0.12
MIN_BODY_LEN = 80

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Referer": "https://kin.naver.com/",
}

AD_PATTERNS = [
    "광고", "협찬", "제공받", "체험단", "공동구매", "구매링크", "할인코드",
    "상담문의", "예약문의", "카톡문의", "오픈채팅", "병원광고", "의료광고",
    "이벤트", "프로모션",
]

EXTRA_AD_PATTERNS = [
    "브라질리언", "임산부왁싱", "임산부 왁싱", "왁싱샵", "왁싱 샵", "슈가링",
    "제모", "레이저제모", "레이저 제모", "시술가격", "시술 가격", "가격문의",
    "가격 문의", "비용문의", "비용 문의", "예약가능", "예약 가능", "예약필수",
    "예약 필수", "네이버 예약", "카카오채널", "카카오 채널", "톡톡상담",
    "톡톡 상담", "방문후기", "방문 후기", "관리샵", "피부관리", "산전마사지",
    "산후마사지", "마사지샵", "클리닉", "피부과", "병원추천", "병원 추천",
]

PROMOTION_TERMS = [
    "가격", "비용", "예약", "문의", "상담", "위치", "주소", "할인", "이벤트",
    "후기", "추천", "업체", "샵", "시술", "관리", "원장", "센터", "병원",
    "클리닉", "피부과", "링크", "구매", "혜택", "쿠폰", "할인가", "무료",
]

SENSITIVE_PROMO_TERMS = [
    "브라질리언", "왁싱", "제모", "슈가링", "마사지", "피부관리", "산전마사지",
    "산후마사지", "클리닉", "피부과",
]

STOPWORDS = {
    "그리고", "그래서", "그러면", "그런데", "하지만", "정말", "진짜", "너무", "아주",
    "많이", "조금", "계속", "오늘", "내일", "어제", "이번", "저번", "제가", "저는",
    "나는", "우리", "때문", "때문에", "있다", "있고", "있는", "있어요", "있습니다",
    "있었다", "있다고", "없다", "없고", "없는", "없어요", "합니다", "됩니다",
    "같아요", "어떻게", "이렇게", "저렇게", "그냥", "혹시", "가능", "관련",
    "질문", "답변", "채택", "지식인", "지식in", "지식iN", "지식i", "네이버", "본문", "보기", "검색", "출처",
    "작성", "등록", "문의", "추천", "확인", "방법", "내용", "경우", "사용",
    "하나요", "인가요", "됩니다", "되어요", "해서", "하면", "하는", "하고",
}


def safe_print(text=""):
    print(str(text).encode("cp949", errors="ignore").decode("cp949"), flush=True)


class ProgressDisplay:
    def __init__(self, keyword, add_count, existing_count):
        self.keyword = keyword
        self.add_count = add_count
        self.existing_count = existing_count
        self.last_line_len = 0
        self.root = None

        try:
            import tkinter as tk
            from tkinter import ttk

            self.root = tk.Tk()
            self.root.title("네이버 지식인 크롤링 진행률")
            self.root.geometry("520x185")
            self.root.resizable(False, False)

            frame = ttk.Frame(self.root, padding=18)
            frame.pack(fill="both", expand=True)

            ttk.Label(frame, text=f"검색 키워드: {keyword}", font=("Malgun Gothic", 11, "bold")).pack(anchor="w")
            self.count_var = tk.StringVar(value=f"이번 실행 추가 수집: 0 / {add_count}")
            self.total_var = tk.StringVar(value=f"전체 저장 데이터: {existing_count}")
            self.status_var = tk.StringVar(value="검색 준비 중...")

            ttk.Label(frame, textvariable=self.count_var).pack(anchor="w", pady=(12, 0))
            ttk.Label(frame, textvariable=self.total_var).pack(anchor="w", pady=(4, 0))
            self.progress = ttk.Progressbar(frame, maximum=max(1, add_count), length=470)
            self.progress.pack(anchor="w", pady=(12, 0))
            ttk.Label(frame, textvariable=self.status_var).pack(anchor="w", pady=(12, 0))
            self.root.update()
        except Exception:
            self.root = None

    def update(self, added_count, status="수집 중"):
        total = self.existing_count + added_count
        percent = int((added_count / max(1, self.add_count)) * 100)
        line = f"진행률 {added_count}/{self.add_count} ({percent}%) / 전체 {total}건 / {status}"
        print("\r" + line + " " * max(0, self.last_line_len - len(line)), end="", flush=True)
        self.last_line_len = len(line)

        if self.root:
            self.count_var.set(f"이번 실행 추가 수집: {added_count} / {self.add_count} ({percent}%)")
            self.total_var.set(f"전체 저장 데이터: {total}")
            self.status_var.set(status)
            self.progress["value"] = added_count
            self.root.update()

    def close(self):
        if self.last_line_len:
            print()
        if self.root:
            self.status_var.set("완료")
            self.root.update()
            self.root.after(700, self.root.destroy)
            self.root.update()


def sanitize_folder_name(keyword):
    name = re.sub(r'[\\/:*?"<>|]+', " ", keyword).strip()
    name = re.sub(r"\s+", "_", name)
    return f"{name}_naverjisik"


def get_paths(keyword):
    file_prefix = sanitize_folder_name(keyword)
    out_dir = DATA_DIR / file_prefix
    out_dir.mkdir(parents=True, exist_ok=True)
    return {
        "dir": out_dir,
        "raw_txt": out_dir / f"{file_prefix}_raw_pipe.txt",
        "filtered_txt": out_dir / f"{file_prefix}_filtered_pipe.txt",
        "frequency_csv": out_dir / f"{file_prefix}_word_frequency.csv",
        "wordcloud_png": out_dir / f"{file_prefix}_wordcloud.png",
        "removed_csv": out_dir / f"{file_prefix}_removed_duplicates_ads.csv",
        "summary_csv": out_dir / f"{file_prefix}_summary.csv",
    }


def request_text(url, timeout=8):
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=timeout) as response:
        raw = response.read()
    return raw.decode("utf-8", errors="ignore")


def read_pipe_rows(path):
    rows = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("||", 2)
            if len(parts) == 3:
                rows.append(tuple(parts))
    return rows


def write_pipe_rows(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        for keyword, url, content in rows:
            clean_content = re.sub(r"\s+", " ", content).strip()
            f.write(f"{keyword}||{url}||{clean_content}\n")


def append_pipe_row(path, keyword, url, content):
    clean_content = re.sub(r"\s+", " ", content).strip()
    with path.open("a", encoding="utf-8", newline="") as f:
        f.write(f"{keyword}||{url}||{clean_content}\n")


def normalize_url(url):
    url = html.unescape(url)
    parsed = urlparse(url)
    if "kin.naver.com" not in parsed.netloc:
        return ""
    query = parse_qs(parsed.query)
    d1id = query.get("d1id", [""])[0]
    dir_id = query.get("dirId", [""])[0]
    doc_id = query.get("docId", [""])[0]
    if d1id and dir_id and doc_id:
        return f"https://kin.naver.com/qna/detail.naver?d1id={d1id}&dirId={dir_id}&docId={doc_id}"
    if doc_id and (d1id or dir_id):
        parts = []
        if d1id:
            parts.append(f"d1id={d1id}")
        if dir_id:
            parts.append(f"dirId={dir_id}")
        parts.append(f"docId={doc_id}")
        return "https://kin.naver.com/qna/detail.naver?" + "&".join(parts)
    if doc_id and "/qna/detail.naver" not in parsed.path:
        return f"https://kin.naver.com/qna/detail.naver?docId={doc_id}"
    return parsed._replace(fragment="").geturl()


def content_fingerprint(content):
    normalized = re.sub(r"\s+", " ", content).strip()
    normalized = re.sub(r"\d+", "0", normalized)
    return hashlib.sha1(normalized[:2500].encode("utf-8", errors="ignore")).hexdigest()


def dedupe_raw_file(raw_txt):
    rows = read_pipe_rows(raw_txt)
    seen_urls = set()
    seen_fingerprints = set()
    deduped = []

    for keyword, url, content in rows:
        url_key = normalize_url(url) or url
        if url_key in seen_urls:
            continue
        seen_urls.add(url_key)

        fingerprint = content_fingerprint(content)
        if fingerprint in seen_fingerprints:
            continue
        seen_fingerprints.add(fingerprint)
        deduped.append((keyword, url_key, content))

    if len(deduped) != len(rows):
        write_pipe_rows(raw_txt, deduped)

    return {"rows": deduped, "seen_urls": seen_urls, "seen_fingerprints": seen_fingerprints}


def search_urls(keyword, page):
    encoded = quote(keyword)
    search_url = f"https://kin.naver.com/search/list.naver?query={encoded}&page={page}"
    search_html = request_text(search_url)

    urls = []
    patterns = [
        r"https://kin\.naver\.com/qna/detail\.naver\?[^\"'<> ]+",
        r"/qna/detail\.naver\?[^\"'<> ]+",
    ]
    for pattern in patterns:
        for match in re.findall(pattern, search_html):
            if match.startswith("/"):
                match = "https://kin.naver.com" + match
            url = normalize_url(match)
            if url:
                urls.append(url)

    return list(dict.fromkeys(urls))


def strip_tags(text):
    text = re.sub(r"(?is)<script.*?</script>", " ", text)
    text = re.sub(r"(?is)<style.*?</style>", " ", text)
    text = re.sub(r"(?is)<noscript.*?</noscript>", " ", text)
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)</p>|</div>|</li>|</h\d>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def extract_meta_description(page_html):
    patterns = [
        r'(?is)<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']',
        r'(?is)<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, page_html)
        if match:
            text = strip_tags(match.group(1))
            if len(text) >= 40:
                return text
    return ""


def extract_json_texts(page_html):
    texts = []
    for key in ["questionContents", "answerContents", "contents", "title"]:
        pattern = rf'"{key}"\s*:\s*"((?:\\.|[^"\\])*)"'
        for match in re.findall(pattern, page_html):
            try:
                text = bytes(match, "utf-8").decode("unicode_escape")
            except Exception:
                text = match
            text = strip_tags(text)
            if len(text) >= 20:
                texts.append(text)
    return texts


def extract_first_class_text(page_html, class_name):
    pattern = rf'(?is)<[^>]+class=["\'][^"\']*{re.escape(class_name)}[^"\']*["\'][^>]*>(.*?)</[^>]+>'
    match = re.search(pattern, page_html)
    if not match:
        return ""
    return strip_tags(match.group(1))


def extract_question_texts(page_html):
    texts = []

    title = extract_first_class_text(page_html, "title")
    question = extract_first_class_text(page_html, "questionDetail")

    if title:
        texts.append(title)
    if question:
        texts.append(question)

    if not question:
        for key in ["questionContents", "title"]:
            pattern = rf'"{key}"\s*:\s*"((?:\\.|[^"\\])*)"'
            for match in re.findall(pattern, page_html):
                try:
                    text = bytes(match, "utf-8").decode("unicode_escape")
                except Exception:
                    text = match
                text = strip_tags(text)
                if len(text) >= 20:
                    texts.append(text)

    return texts


def extract_naverjisik_body(url):
    page_html = request_text(url)
    texts = []
    texts.extend(extract_question_texts(page_html))

    if not texts:
        meta = extract_meta_description(page_html)
        body = meta if meta else strip_tags(page_html)
    else:
        body = " ".join(dict.fromkeys(texts))

    remove_phrases = [
        "네이버 지식iN", "질문하기", "답변하기", "프로필 더보기", "알아두세요",
        "위 답변은 답변작성자가 경험과 지식을 바탕으로 작성한 내용입니다",
        "포인트로 감사", "서비스 이용약관", "개인정보처리방침", "고객센터",
    ]
    for phrase in remove_phrases:
        body = body.replace(phrase, " ")

    body = re.sub(r"\s+", " ", body).strip()
    return body


def clean_for_analysis(content):
    content = re.sub(r"https?://\S+", " ", content)
    content = re.sub(r"[^0-9A-Za-z가-힣\s]", " ", content)
    return re.sub(r"\s+", " ", content).strip()


def looks_like_ad(content):
    compact = re.sub(r"\s+", " ", content)
    compact_no_space = re.sub(r"\s+", "", content)

    for pattern in AD_PATTERNS + EXTRA_AD_PATTERNS:
        if pattern.replace(" ", "") in compact_no_space:
            return True

    promotional_score = sum(compact.count(term) for term in PROMOTION_TERMS)
    promotional_score += len(re.findall(r"문의|예약|상담|링크|할인|이벤트|체험|제공", compact))

    sensitive_score = sum(term.replace(" ", "") in compact_no_space for term in SENSITIVE_PROMO_TERMS)
    if sensitive_score and promotional_score >= 2:
        return True
    return promotional_score >= 10 and len(compact) < 5000


def tokenize(text):
    cleaned = clean_for_analysis(text)
    words = re.findall(r"[가-힣A-Za-z0-9]{2,}", cleaned)
    result = []
    for word in words:
        word = word.lower()
        if word in STOPWORDS:
            continue
        if word.isdigit():
            continue
        result.append(word)
    return result


def filter_rows(rows):
    filtered = []
    removed = []
    seen_urls = set()
    seen_fingerprints = set()

    for keyword, url, content in rows:
        url_key = normalize_url(url) or url
        fingerprint = content_fingerprint(content)
        reason = ""

        if url_key in seen_urls:
            reason = "duplicate_url"
        elif fingerprint in seen_fingerprints:
            reason = "duplicate_content"
        elif looks_like_ad(content):
            reason = "ad_pattern"
        elif len(clean_for_analysis(content)) < MIN_BODY_LEN:
            reason = "short_body"

        if reason:
            removed.append((reason, keyword, url_key, content[:500]))
            continue

        seen_urls.add(url_key)
        seen_fingerprints.add(fingerprint)
        filtered.append((keyword, url_key, content))

    return filtered, removed


def find_font():
    candidates = [
        Path("C:/Windows/Fonts/malgun.ttf"),
        Path("C:/Windows/Fonts/malgunbd.ttf"),
        Path("C:/Windows/Fonts/NanumGothic.ttf"),
    ]
    for font in candidates:
        if font.exists():
            return str(font)
    return None


def random_text_color():
    return random.choice([
        (210, 55, 45), (35, 105, 65), (190, 85, 95), (115, 95, 70),
        (155, 80, 105), (230, 95, 105), (15, 115, 80), (75, 105, 55),
        (95, 70, 160), (165, 50, 50), (45, 125, 130),
    ])


def make_wordcloud(freq, output_png):
    width, height = 1600, 1000
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font_path = find_font()
    items = freq.most_common(180)

    if not items:
        image.save(output_png)
        return

    max_count = items[0][1]
    placed = []
    random.seed(42)

    for word, count in items:
        size = int(24 + (count / max_count) * 92)
        font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()
        box = draw.textbbox((0, 0), word, font=font)
        tw, th = box[2] - box[0], box[3] - box[1]

        if tw >= width or th >= height:
            continue

        for _ in range(500):
            x = random.randint(20, max(21, width - tw - 20))
            y = random.randint(20, max(21, height - th - 20))
            rect = (x, y, x + tw, y + th)
            overlap = any(not (rect[2] < r[0] or rect[0] > r[2] or rect[3] < r[1] or rect[1] > r[3]) for r in placed)
            if not overlap:
                draw.text((x, y), word, fill=random_text_color(), font=font)
                placed.append(rect)
                break

    image.save(output_png)


def save_analysis(paths):
    rows = read_pipe_rows(paths["raw_txt"])
    filtered, removed = filter_rows(rows)
    write_pipe_rows(paths["filtered_txt"], filtered)

    with paths["removed_csv"].open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["reason", "keyword", "url", "content_preview"])
        writer.writerows(removed)

    freq = Counter()
    for _, _, content in filtered:
        freq.update(tokenize(content))

    with paths["frequency_csv"].open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "count"])
        writer.writerows(freq.most_common())

    make_wordcloud(freq, paths["wordcloud_png"])

    with paths["summary_csv"].open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["item", "count"])
        writer.writerow(["raw_total", len(rows)])
        writer.writerow(["filtered_total", len(filtered)])
        writer.writerow(["removed_total", len(removed)])
        writer.writerow(["unique_words", len(freq)])

    return len(rows), len(filtered), len(removed), freq


def crawl_raw(keyword, add_count, raw_txt):
    dedupe = dedupe_raw_file(raw_txt)
    existing_count = len(dedupe["rows"])
    seen_urls = set(dedupe["seen_urls"])
    seen_fingerprints = set(dedupe["seen_fingerprints"])

    progress = ProgressDisplay(keyword, add_count, existing_count)
    added = 0
    page = 1
    empty_pages = 0
    no_new_save_pages = 0

    try:
        while added < add_count and page <= MAX_SEARCH_PAGES:
            progress.update(added, f"검색 page {page}")
            added_before_page = added

            try:
                urls = search_urls(keyword, page)
            except Exception as exc:
                safe_print(f"\n검색 실패 page={page}: {exc}")
                urls = []

            if not urls:
                empty_pages += 1
                if empty_pages >= 5:
                    break
                page += 1
                time.sleep(SLEEP_SEARCH_SEC)
                continue

            empty_pages = 0

            for url in urls:
                if added >= add_count:
                    break

                url_key = normalize_url(url) or url
                if url_key in seen_urls:
                    continue

                try:
                    content = extract_naverjisik_body(url_key)
                    time.sleep(SLEEP_BODY_SEC)
                except Exception:
                    continue

                if len(clean_for_analysis(content)) < MIN_BODY_LEN:
                    continue

                fingerprint = content_fingerprint(content)
                if fingerprint in seen_fingerprints:
                    continue

                seen_urls.add(url_key)
                seen_fingerprints.add(fingerprint)
                append_pipe_row(raw_txt, keyword, url_key, content)
                added += 1
                progress.update(added, "본문 수집 중")

            if added == added_before_page:
                no_new_save_pages += 1
                if no_new_save_pages >= MAX_NO_NEW_SAVE_PAGES:
                    safe_print(f"\n{MAX_NO_NEW_SAVE_PAGES}페이지 연속 새 저장 글이 없어 자동 종료합니다.")
                    break
            else:
                no_new_save_pages = 0

            page += 1
            time.sleep(SLEEP_SEARCH_SEC)
    finally:
        progress.close()

    return {"existing_count": existing_count, "added_count": added, "total_count": existing_count + added}


def parse_args():
    parser = argparse.ArgumentParser(description="네이버 지식인 검색 키워드 크롤링 + 빈도 분석 + 워드클라우드")
    parser.add_argument("--keyword", help="검색 키워드 예: 임산부 다이어리")
    parser.add_argument("--count", type=int, help="크롤링할 본문 수 예: 3000")
    return parser.parse_args()


def main():
    args = parse_args()
    keyword = args.keyword or input("검색 키워드를 입력하세요: ").strip()
    count = args.count or int(input("크롤링 수를 입력하세요: ").strip())

    if not keyword:
        raise ValueError("검색 키워드가 비어 있습니다.")
    if count <= 0:
        raise ValueError("크롤링 수는 1 이상이어야 합니다.")

    paths = get_paths(keyword)

    safe_print("\n네이버 지식인 전용 크롤링 시작")
    safe_print(f"- 검색 키워드: {keyword}")
    safe_print(f"- 이번 실행 추가 크롤링 수: {count}")
    safe_print("- 검색 방식: 네이버 지식인 검색 페이지")
    safe_print("- 본문 방식: 공개 지식인 질문/답변 본문")
    safe_print(f"- 저장 폴더: {paths['dir']}")

    crawl_result = crawl_raw(keyword, count, paths["raw_txt"])
    raw_total, filtered_total, removed_total, freq = save_analysis(paths)

    safe_print("\n완료")
    safe_print(f"- 이번 실행 추가 수집: {crawl_result['added_count']}")
    safe_print(f"- 원본 저장 데이터: {raw_total}")
    safe_print(f"- 분석 사용 데이터: {filtered_total}")
    safe_print(f"- 중복/광고/짧은본문 제외: {removed_total}")
    safe_print(f"- 원본 txt: {paths['raw_txt']}")
    safe_print(f"- 필터링 txt: {paths['filtered_txt']}")
    safe_print(f"- 빈도 CSV: {paths['frequency_csv']}")
    safe_print(f"- 워드클라우드 PNG: {paths['wordcloud_png']}")

    safe_print("\n상위 빈도")
    for word, count_value in freq.most_common(30):
        safe_print(f"{word}, {count_value}")


if __name__ == "__main__":
    main()
