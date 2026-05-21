import argparse
import csv
import hashlib
import html
import importlib
import json
import random
import re
import site
import sys
import time
from collections import Counter
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# 네이버 카페 전용 크롤러 + 빈도 분석 + 워드클라우드
# 예시:
#   python navercafe_검색키워드.py
#   python navercafe_검색키워드.py --keyword "임산부 다이어리" --count 3000
#
# 저장 폴더:
#   data/임산부_다이어리_navercafe/
# ============================================================


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR
LOCAL_PACKAGE_DIR = BASE_DIR.parents[1] / ".python_packages"

if LOCAL_PACKAGE_DIR.exists():
    local_package_path = str(LOCAL_PACKAGE_DIR.resolve())
    sys.path = [path for path in sys.path if path != local_package_path]
    sys.path.insert(0, local_package_path)
    site.addsitedir(local_package_path)
    importlib.invalidate_caches()

SEARCH_PAGE_SIZE = 10
MAX_SEARCH_PAGES = 500
SLEEP_SEARCH_SEC = 0.55
SLEEP_BODY_SEC = 0.15

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def refresh_local_package_path():
    if not LOCAL_PACKAGE_DIR.exists():
        return

    local_package_path = str(LOCAL_PACKAGE_DIR.resolve())
    sys.path = [path for path in sys.path if path != local_package_path]
    sys.path.insert(0, local_package_path)

    for module_name in list(sys.modules):
        if module_name == "selenium" or module_name.startswith("selenium."):
            del sys.modules[module_name]

    importlib.invalidate_caches()


class ProgressDisplay:
    def __init__(self, keyword, add_count, existing_count):
        self.keyword = keyword
        self.add_count = add_count
        self.existing_count = existing_count
        self.last_line_len = 0
        self.root = None
        self.status_var = None
        self.count_var = None
        self.total_var = None
        self.progress = None

        try:
            import tkinter as tk
            from tkinter import ttk

            self.root = tk.Tk()
            self.root.title("네이버 카페 크롤링 진행률")
            self.root.geometry("460x180")
            self.root.resizable(False, False)

            frame = ttk.Frame(self.root, padding=18)
            frame.pack(fill="both", expand=True)

            ttk.Label(frame, text=f"검색 키워드: {keyword}", font=("Malgun Gothic", 11, "bold")).pack(anchor="w")
            self.count_var = tk.StringVar(value=f"이번 실행 추가 수집: 0 / {add_count}")
            self.total_var = tk.StringVar(value=f"전체 저장 데이터: {existing_count}")
            self.status_var = tk.StringVar(value="검색 준비 중...")

            ttk.Label(frame, textvariable=self.count_var).pack(anchor="w", pady=(12, 0))
            ttk.Label(frame, textvariable=self.total_var).pack(anchor="w", pady=(4, 0))
            self.progress = ttk.Progressbar(frame, maximum=max(1, add_count), length=410)
            self.progress.pack(anchor="w", pady=(12, 0))
            ttk.Label(frame, textvariable=self.status_var).pack(anchor="w", pady=(12, 0))

            self.root.update()
        except Exception:
            self.root = None

    def update(self, added_count, status="크롤링 중..."):
        total = self.existing_count + added_count
        percent = int((added_count / max(1, self.add_count)) * 100)
        line = f"진행률: {added_count}/{self.add_count} ({percent}%) / 전체 {total}건 / {status}"
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
    "오늘", "정도", "진짜", "너무", "그냥", "이제", "하루", "이번", "저는", "제가",
    "우리", "때문", "때문에", "생각", "느낌", "블로그", "포스팅", "사진", "댓글",
    "공감", "네이버", "입니다", "합니다", "있는", "없는", "해서", "하고", "하면",
    "부터", "까지", "같아요", "그리고", "하지만", "그래서", "다시", "많이", "조금",
    "완전", "정말", "하나", "요즘", "계속", "처음", "마지막", "관련", "사람",
    "부분", "보기", "본문", "카테고리", "이웃", "로그인", "검색", "기능", "기타",
    "바로가기", "열기", "크게", "전체", "있어요", "있다", "있었다", "있다고",
    "했다", "했다가", "되는", "위해", "같은", "이렇게", "벌써", "가장", "바로",
    "함께", "내가", "나는", "나의", "좋은", "좋다", "사실", "하는", "없어",
    "없이", "안녕하세요", "이번에", "전에", "내돈내산", "광고", "협찬", "문의",
    "예약", "주소", "전화", "클릭", "확인", "추천", "후기", "정보", "준비",
    "먹고", "다른", "있어서", "시간", "그래도", "근데", "같이", "엄청", "특히",
    "있습니다", "했는데", "이런", "같다", "거의", "한다", "보고", "대한", "동안",
    "위한", "통해", "또는", "에서", "에게", "보다", "아래", "위에", "여기",
    "저기", "관련된", "가능", "사용", "경우", "방법", "체크인", "블로그의",
    "장소의", "오늘은", "시간이", "것도", "지금", "아주", "있고", "해요",
    "많은", "가서", "먹는", "아직", "자주", "열심히", "생각보다", "갑자기",
    "것이", "일차", "매일", "해서는", "같아서", "있는데", "싶은",
}


def safe_print(text):
    print(str(text).encode("cp949", errors="ignore").decode("cp949"), flush=True)


def sanitize_folder_name(keyword):
    name = re.sub(r'[\\/:*?"<>|]+', " ", keyword).strip()
    name = re.sub(r"\s+", "_", name)
    return f"{name}_navercafe"


def get_paths(keyword):
    out_dir = DATA_DIR / sanitize_folder_name(keyword)
    out_dir.mkdir(parents=True, exist_ok=True)
    return {
        "dir": out_dir,
        "raw_txt": out_dir / "navercafe_raw_pipe.txt",
        "filtered_txt": out_dir / "navercafe_filtered_pipe.txt",
        "frequency_csv": out_dir / "navercafe_word_frequency.csv",
        "wordcloud_png": out_dir / "navercafe_wordcloud.png",
        "removed_csv": out_dir / "removed_duplicates_ads.csv",
        "summary_csv": out_dir / "summary.csv",
    }


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


def dedupe_raw_file(raw_txt):
    rows = read_pipe_rows(raw_txt)
    seen_urls = set()
    seen_fingerprints = set()
    deduped = []
    removed_url = 0
    removed_content = 0

    for keyword, url, content in rows:
        if url in seen_urls:
            removed_url += 1
            continue
        seen_urls.add(url)

        fingerprint = content_fingerprint(content)
        if fingerprint in seen_fingerprints:
            removed_content += 1
            continue
        seen_fingerprints.add(fingerprint)
        deduped.append((keyword, url, content))

    if removed_url or removed_content:
        with raw_txt.open("w", encoding="utf-8") as f:
            for keyword, url, content in deduped:
                f.write(f"{keyword}||{url}||{content}\n")

    return {
        "rows": deduped,
        "seen_urls": seen_urls,
        "seen_fingerprints": seen_fingerprints,
        "removed_url": removed_url,
        "removed_content": removed_content,
    }


def get_html(url):
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=12) as res:
        return res.read().decode("utf-8", errors="ignore")


def get_api_json(url, client_id, client_secret):
    headers = {
        **HEADERS,
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    req = Request(url, headers=headers)
    with urlopen(req, timeout=12) as res:
        return json.loads(res.read().decode("utf-8", errors="ignore"))


def clean_text(text):
    text = html.unescape(text or "")
    text = text.replace("\\/", "/").replace('\\"', '"')
    text = re.sub(r"<script[\s\S]*?</script>", " ", text)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text)
    text = re.sub(r"</?mark>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&[a-zA-Z]+;", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_pipe_field(value):
    value = (value or "").replace("||", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", value).strip()


def normalize_cafe_url(url):
    url = html.unescape(url or "").replace("\\/", "/")
    match = re.search(r"https?://cafe\.naver\.com/([^/?#]+)/([0-9]+)", url)
    if match:
        return f"https://cafe.naver.com/{match.group(1)}/{match.group(2)}"

    match = re.search(r"https?://cafe\.naver\.com/ArticleRead\.nhn\?[^\"']*clubid=([0-9]+)[^\"']*articleid=([0-9]+)", url)
    if match:
        return f"https://cafe.naver.com/ArticleRead.nhn?clubid={match.group(1)}&articleid={match.group(2)}"

    match = re.search(r"https?://(?:m\.)?cafe\.naver\.com/ca-fe/(?:web/)?cafes/([0-9]+)/articles/([0-9]+)", url)
    if match:
        return f"https://m.cafe.naver.com/ca-fe/web/cafes/{match.group(1)}/articles/{match.group(2)}"

    match = re.search(r"https?://m\.cafe\.naver\.com/([^/?#]+)/([0-9]+)", url)
    if match:
        return f"https://m.cafe.naver.com/{match.group(1)}/{match.group(2)}"

    return ""


def extract_search_items(search_html):
    items = []
    seen = set()
    json_pattern = re.compile(
        r'"content":"(?P<content>.*?)","contentEllipsis".*?'
        r'"contentHref":"(?P<href>https://(?:m\.)?cafe\.naver\.com/[^"]+)".*?'
        r'"title":"(?P<title>.*?)","titleEllipsis".*?"titleHref":"(?P=href)"',
        re.S,
    )
    for match in json_pattern.finditer(search_html):
        url = normalize_cafe_url(clean_text(match.group("href")))
        if not url or url in seen:
            continue
        seen.add(url)
        fallback = f"{clean_text(match.group('title'))} {clean_text(match.group('content'))}".strip()
        items.append({"url": url, "fallback": fallback})

    html_pattern = re.compile(
        r'<a href="(?P<href>https://cafe\.naver\.com/[^"]+)"[^>]*class="title_link"[^>]*>'
        r'(?P<title>[\s\S]*?)</a>[\s\S]*?'
        r'<a href="(?P=href)"[^>]*class="dsc_link"[^>]*>(?P<content>[\s\S]*?)</a>',
        re.S,
    )
    for match in html_pattern.finditer(search_html):
        url = normalize_cafe_url(clean_text(match.group("href")))
        if not url or url in seen:
            continue
        seen.add(url)
        fallback = f"{clean_text(match.group('title'))} {clean_text(match.group('content'))}".strip()
        items.append({"url": url, "fallback": fallback})

    patterns = [
        r'"contentHref":"(?P<href>https://cafe\.naver\.com/[^"]+)"',
        r'"titleHref":"(?P<href>https://cafe\.naver\.com/[^"]+)"',
        r'"contentHref":"(?P<href>https://m\.cafe\.naver\.com/[^"]+)"',
        r'"titleHref":"(?P<href>https://m\.cafe\.naver\.com/[^"]+)"',
        r'href="(?P<href>https://cafe\.naver\.com/[^"]+)"',
        r'href="(?P<href>https://m\.cafe\.naver\.com/[^"]+)"',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, search_html, re.S):
            url = normalize_cafe_url(clean_text(match.group("href")))
            if not url or "cafe.naver.com" not in url:
                continue
            if url in seen:
                continue
            seen.add(url)
            items.append({"url": url, "fallback": ""})
    return items


def search_items(keyword, start):
    encoded = quote(keyword)
    url = (
        "https://search.naver.com/search.naver"
        f"?ssc=tab.cafe.all&sm=tab_pge&query={encoded}&start={start}"
    )
    return extract_search_items(get_html(url))


def search_items_api(keyword, start, client_id, client_secret):
    params = urlencode({
        "query": keyword,
        "display": SEARCH_PAGE_SIZE,
        "start": start,
        "sort": "sim",
    })
    url = f"https://openapi.naver.com/v1/search/cafearticle.json?{params}"
    data = get_api_json(url, client_id, client_secret)

    items = []
    seen = set()
    for item in data.get("items", []):
        url = normalize_cafe_url(clean_text(item.get("link", "")))
        if not url or url in seen:
            continue
        seen.add(url)
        fallback = f"{clean_text(item.get('title', ''))} {clean_text(item.get('description', ''))}".strip()
        items.append({"url": url, "fallback": fallback})
    return items


def extract_cafe_body(page_html):
    start = page_html.find('class="se-main-container"')
    if start >= 0:
        div_start = page_html.rfind("<div", 0, start)
        if div_start >= 0:
            start = div_start
        depth = 0
        end = -1
        for match in re.finditer(r"</?div\b[^>]*>", page_html[start:], re.I):
            tag = match.group(0)
            if tag.startswith("</"):
                depth -= 1
                if depth == 0:
                    end = start + match.end()
                    break
            else:
                depth += 1
        block = page_html[start:end] if end > start else page_html[start:start + 90000]
        text = clean_text(block)
        if len(text) >= 100:
            return text

    patterns = [
        r'<div[^>]+class="[^"]*ArticleContentBox[^"]*"[^>]*>([\s\S]*?)</div>\s*</div>',
        r'<div[^>]+class="[^"]*article_viewer[^"]*"[^>]*>([\s\S]*?)</div>',
        r'<div[^>]+id="tbody"[^>]*>([\s\S]*?)</td>',
        r'<div[^>]+id="postContent"[^>]*>([\s\S]*?)</div>',
        r'<div[^>]+id="postViewArea"[^>]*>([\s\S]*?)</div>',
        r'<div[^>]+class="[^"]*post_ct[^"]*"[^>]*>([\s\S]*?)</div>',
        r'<div[^>]+class="[^"]*se_component_wrap[^"]*"[^>]*>([\s\S]*?)</div>',
    ]
    candidates = []
    for pattern in patterns:
        for block in re.findall(pattern, page_html):
            text = clean_text(block)
            if len(text) >= 100:
                candidates.append(text)
    if candidates:
        return max(candidates, key=len)

    fragments = re.findall(r'"text":"([^"]{20,})"', page_html)
    joined = clean_text(" ".join(fragments))
    if len(joined) >= 100:
        return joined

    meta_patterns = [
        r'<meta[^>]+property="og:description"[^>]+content="([^"]+)"',
        r'<meta[^>]+name="description"[^>]+content="([^"]+)"',
    ]
    for pattern in meta_patterns:
        match = re.search(pattern, page_html)
        if match:
            text = clean_text(match.group(1))
            if len(text) >= 60:
                return text
    return ""


def create_login_browser(profile_dir):
    refresh_local_package_path()

    try:
        webdriver = importlib.import_module("selenium.webdriver")
        from selenium.webdriver.chrome.options import Options
    except ImportError as exc:
        raise RuntimeError(
            "로그인 브라우저를 사용하려면 selenium이 필요합니다. "
            f"현재 스크립트는 {LOCAL_PACKAGE_DIR} 폴더의 패키지도 같이 확인합니다. "
            "그래도 실패하면 터미널에서 아래 명령으로 설치하세요:\n"
            f'& "{sys.executable}" -m pip install --target "{LOCAL_PACKAGE_DIR}" selenium'
        ) from exc

    options = Options()
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    return webdriver.Chrome(options=options)


def prepare_login_browser(browser_config):
    if not browser_config or not browser_config.get("use_browser_login"):
        return None

    driver = create_login_browser(browser_config["profile_dir"])
    driver.get("https://nid.naver.com/nidlogin.login")
    print("\n크롬 브라우저가 열렸습니다.")
    print("네이버에 로그인하고, 필요한 카페 가입/권한 상태를 확인한 뒤 Enter를 누르세요.")
    input("로그인 완료 후 Enter: ")
    return driver


def extract_cafe_body_browser(driver, url):
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    driver.get(url)
    wait = WebDriverWait(driver, 8)
    time.sleep(1.0)

    try:
        iframe = wait.until(EC.presence_of_element_located((By.ID, "cafe_main")))
        driver.switch_to.frame(iframe)
    except TimeoutException:
        pass

    selectors = [
        ".se-main-container",
        ".ArticleContentBox",
        ".article_viewer",
        "#tbody",
        "#postContent",
        "body",
    ]
    texts = []
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            text = clean_text(element.text)
            if len(text) >= 100:
                texts.append(text)
        except NoSuchElementException:
            continue

    driver.switch_to.default_content()
    if not texts:
        return ""

    body = max(texts, key=len)
    blocked_markers = [
        "카페 회원만",
        "멤버에게만 공개",
        "권한이 없습니다",
        "가입 후 이용",
        "로그인 후 이용",
        "접근할 수 없습니다",
        "등급 이상의 회원",
    ]
    if any(marker in body for marker in blocked_markers):
        return ""
    return body


def normalize_content(text):
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"#[가-힣A-Za-z0-9_]+", " ", text)
    text = re.sub(r"[^가-힣A-Za-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def content_fingerprint(text):
    tokens = normalize_content(text).split()
    sample = " ".join(tokens[:450])
    return hashlib.sha1(sample.encode("utf-8")).hexdigest()


def is_ad(content):
    compact = re.sub(r"\s+", " ", content)
    for pattern in AD_PATTERNS:
        if pattern in compact:
            return True, pattern

    promotional_score = 0
    promotional_score += len(re.findall(r"문의|예약|상담|링크|할인|이벤트|체험|제공", compact))
    promotional_score += len(re.findall(r"센터|업체|브랜드|제품|구매|가격|비용", compact))
    if promotional_score >= 12 and len(compact) < 5000:
        return True, f"광고성 키워드 점수 {promotional_score}"
    return False, ""


def tokenize(text, extra_stopwords=None):
    stopwords = STOPWORDS | set(extra_stopwords or [])
    words = re.findall(r"[가-힣]{2,}", text)
    return [word for word in words if word not in stopwords and len(word) >= 2]


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
    width, height = 1700, 1050
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    random.seed(2027)
    palette = [
        "#111111", "#A71930", "#204B57", "#2F6F5E", "#C47A22",
        "#6B3E75", "#D44731", "#0F766E", "#7C2D12", "#1D4ED8",
        "#86198F", "#365314", "#BE123C", "#4338CA",
    ]
    top_words = freq.most_common(110)

    if not top_words:
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
        size = int(22 + 126 * (ratio ** 0.56))
        if rank < 5:
            size += 24 - rank * 4

        font = get_font(size)
        bbox = draw.textbbox((0, 0), word, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        color = random.choice(palette)

        placed_ok = False
        for attempt in range(1000):
            if rank < 10 and attempt < 300:
                x = random.randint(max(42, width // 2 - 500), min(width - text_width - 42, width // 2 + 360))
                y = random.randint(60, min(height - text_height - 42, 600))
            else:
                x = random.randint(38, max(39, width - text_width - 38))
                y = random.randint(38, max(39, height - text_height - 38))
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
                y = random.randint(38, max(39, height - text_height - 38))
                box = (x - 8, y - 8, x + text_width + 8, y + text_height + 8)
                if not intersects(box):
                    draw.text((x, y), word, font=font, fill=random.choice(palette))
                    placed.append(box)
                    break

    image.save(path)


def crawl_raw(keyword, add_count, raw_txt, api_config=None, browser_config=None):
    dedupe_result = dedupe_raw_file(raw_txt)
    seen_urls = dedupe_result["seen_urls"]
    seen_fingerprints = dedupe_result["seen_fingerprints"]
    existing_count = len(dedupe_result["rows"])
    added_count = 0
    target_total = existing_count + add_count

    if existing_count:
        safe_print(f"기존 저장 데이터: {existing_count}건")
    if dedupe_result["removed_url"] or dedupe_result["removed_content"]:
        safe_print(
            "기존 raw 중복 제거: "
            f"URL {dedupe_result['removed_url']}건, 본문 {dedupe_result['removed_content']}건"
        )

    driver = prepare_login_browser(browser_config)
    progress = ProgressDisplay(keyword, add_count, existing_count)
    progress.update(0, "검색 시작")
    empty_pages = 0
    try:
        with raw_txt.open("a", encoding="utf-8") as out:
            for page_idx in range(MAX_SEARCH_PAGES):
                if added_count >= add_count:
                    break
                if empty_pages >= 16:
                    safe_print("연속 빈 페이지가 많아 크롤링을 중단합니다.")
                    break

                start = page_idx * SEARCH_PAGE_SIZE + 1
                progress.update(added_count, f"검색 결과 확인 중 start={start}")
                try:
                    if api_config and api_config.get("use_api"):
                        items = search_items_api(
                            keyword,
                            start,
                            api_config["client_id"],
                            api_config["client_secret"],
                        )
                    else:
                        items = search_items(keyword, start)
                except Exception as exc:
                    safe_print(f"\n검색 실패 start={start}: {exc}")
                    empty_pages += 1
                    progress.update(added_count, f"검색 실패 start={start}")
                    time.sleep(max(2.0, SLEEP_SEARCH_SEC))
                    continue

                added = 0
                for item in items:
                    if added_count >= add_count:
                        break
                    url = item["url"]
                    if url in seen_urls:
                        continue

                    try:
                        progress.update(added_count, "본문 수집 중")
                        if driver:
                            body = extract_cafe_body_browser(driver, url)
                        else:
                            body = extract_cafe_body(get_html(url))
                        if len(body) < 100:
                            raise ValueError("본문 추출 길이 부족")
                        fingerprint = content_fingerprint(body)
                        if fingerprint in seen_fingerprints:
                            continue
                        seen_urls.add(url)
                        seen_fingerprints.add(fingerprint)
                        out.write(f"{clean_pipe_field(keyword)}||{clean_pipe_field(url)}||{clean_pipe_field(body)}\n")
                        out.flush()
                        added_count += 1
                        added += 1
                        progress.update(added_count, "본문 저장 완료")
                    except Exception as exc:
                        safe_print(f"\n본문 실패: {url} / {exc}")
                        progress.update(added_count, "본문 실패 후 계속 진행")
                    time.sleep(SLEEP_BODY_SEC)

                empty_pages = empty_pages + 1 if added == 0 else 0
                time.sleep(SLEEP_SEARCH_SEC)
    finally:
        progress.close()
        if driver:
            driver.quit()

    return {
        "existing_count": existing_count,
        "added_count": added_count,
        "total_count": existing_count + added_count,
        "target_total": target_total,
        "removed_existing_url": dedupe_result["removed_url"],
        "removed_existing_content": dedupe_result["removed_content"],
    }


def filter_and_analyze(keyword, paths):
    seen_urls = set()
    seen_fingerprints = set()
    freq = Counter()
    kept = 0
    removed_duplicate_url = 0
    removed_duplicate_content = 0
    removed_ad = 0
    extra_stopwords = set(re.findall(r"[가-힣]{2,}", keyword))

    with (
        paths["raw_txt"].open(encoding="utf-8") as src,
        paths["filtered_txt"].open("w", encoding="utf-8") as out,
        paths["removed_csv"].open("w", encoding="utf-8-sig", newline="") as removed_file,
    ):
        writer = csv.writer(removed_file)
        writer.writerow(["reason", "keyword", "url", "detail"])

        for line in src:
            parts = line.rstrip("\n").split("||", 2)
            if len(parts) != 3:
                continue
            crawling_word, url, content = parts

            if url in seen_urls:
                removed_duplicate_url += 1
                writer.writerow(["duplicate_url", crawling_word, url, ""])
                continue
            seen_urls.add(url)

            fingerprint = content_fingerprint(content)
            if fingerprint in seen_fingerprints:
                removed_duplicate_content += 1
                writer.writerow(["duplicate_content", crawling_word, url, ""])
                continue
            seen_fingerprints.add(fingerprint)

            ad, reason = is_ad(content)
            if ad:
                removed_ad += 1
                writer.writerow(["ad", crawling_word, url, reason])
                continue

            out.write(f"{crawling_word}||{url}||{content}\n")
            freq.update(tokenize(content, extra_stopwords))
            kept += 1

    with paths["frequency_csv"].open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "count"])
        writer.writerows(freq.most_common(500))

    make_wordcloud(freq, paths["wordcloud_png"], f"{keyword} 네이버카페 워드클라우드")

    raw_rows = sum(1 for _ in paths["raw_txt"].open(encoding="utf-8"))
    with paths["summary_csv"].open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["item", "value"])
        writer.writerow(["keyword", keyword])
        writer.writerow(["raw_count", raw_rows])
        writer.writerow(["filtered_count", kept])
        writer.writerow(["removed_duplicate_url", removed_duplicate_url])
        writer.writerow(["removed_duplicate_content", removed_duplicate_content])
        writer.writerow(["removed_ad", removed_ad])

    return {
        "raw_count": raw_rows,
        "filtered_count": kept,
        "removed_duplicate_url": removed_duplicate_url,
        "removed_duplicate_content": removed_duplicate_content,
        "removed_ad": removed_ad,
        "top_words": freq.most_common(30),
    }


def parse_args():
    parser = argparse.ArgumentParser(description="네이버 카페 검색 키워드 크롤링 + 빈도 분석 + 워드클라우드")
    parser.add_argument("--keyword", help="검색 키워드 예: 임산부 다이어리")
    parser.add_argument("--count", type=int, help="크롤링할 본문 수 예: 3000")
    parser.add_argument("--use-api", action="store_true", help="네이버 검색 Open API를 사용합니다.")
    parser.add_argument("--naver-client-id", help="네이버 개발자 센터 Client ID")
    parser.add_argument("--naver-client-secret", help="네이버 개발자 센터 Client Secret")
    parser.add_argument("--use-browser-login", action="store_true", help="로그인된 크롬 브라우저로 카페 본문을 수집합니다.")
    parser.add_argument(
        "--browser-profile-dir",
        default=str(DATA_DIR / "_naver_cafe_chrome_profile"),
        help="로그인 세션을 저장할 크롬 프로필 폴더",
    )
    return parser.parse_args()


def get_api_config(args):
    use_api = args.use_api
    if not use_api and not args.naver_client_id and not args.naver_client_secret:
        answer = input("네이버 검색 API 키를 사용할까요? (y/n): ").strip().lower()
        use_api = answer in {"y", "yes", "ㅛ", "예", "ㅇ"}

    if not use_api:
        return {"use_api": False}

    client_id = args.naver_client_id or input("Naver Client ID: ").strip()
    client_secret = args.naver_client_secret or input("Naver Client Secret: ").strip()
    if not client_id or not client_secret:
        raise ValueError("API 사용을 선택했으면 Client ID와 Client Secret이 필요합니다.")

    return {
        "use_api": True,
        "client_id": client_id,
        "client_secret": client_secret,
    }


def get_browser_config(args):
    use_browser_login = args.use_browser_login
    if not use_browser_login:
        answer = input("로그인 브라우저로 카페 본문을 가져올까요? (y/n): ").strip().lower()
        use_browser_login = answer in {"y", "yes", "ㅛ", "예", "ㅇ"}

    if not use_browser_login:
        return {"use_browser_login": False}

    profile_dir = Path(args.browser_profile_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)
    return {
        "use_browser_login": True,
        "profile_dir": str(profile_dir),
    }


def main():
    args = parse_args()
    keyword = args.keyword or input("검색 키워드를 입력하세요: ").strip()
    count = args.count or int(input("크롤링 수를 입력하세요: ").strip())
    if not keyword:
        raise ValueError("검색 키워드가 비어 있습니다.")
    if count <= 0:
        raise ValueError("크롤링 수는 1 이상이어야 합니다.")
    api_config = get_api_config(args)
    browser_config = get_browser_config(args)

    paths = get_paths(keyword)
    safe_print(f"\n네이버 카페 전용 크롤링 시작")
    safe_print(f"- 검색 키워드: {keyword}")
    safe_print(f"- 이번 실행 추가 크롤링 수: {count}")
    safe_print(f"- 검색 방식: {'네이버 검색 Open API' if api_config.get('use_api') else '네이버 검색 페이지'}")
    safe_print(f"- 본문 방식: {'로그인 브라우저' if browser_config.get('use_browser_login') else '직접 HTML 요청'}")
    safe_print(f"- 저장 폴더: {paths['dir']}")

    crawl_result = crawl_raw(keyword, count, paths["raw_txt"], api_config, browser_config)
    result = filter_and_analyze(keyword, paths)

    print("\n완료")
    print(f"- 기존 본문 수: {crawl_result['existing_count']}")
    print(f"- 이번 실행 추가 수집 수: {crawl_result['added_count']}")
    print(f"- 원본 본문 총수: {crawl_result['total_count']}")
    print(f"- 정제 후 분석 문서 수: {result['filtered_count']}")
    print(f"- 중복 URL 제거: {result['removed_duplicate_url']}")
    print(f"- 중복 본문 제거: {result['removed_duplicate_content']}")
    print(f"- 광고성 글 제거: {result['removed_ad']}")
    print(f"- 원본 TXT: {paths['raw_txt']}")
    print(f"- 정제 TXT: {paths['filtered_txt']}")
    print(f"- 빈도 CSV: {paths['frequency_csv']}")
    print(f"- 워드클라우드: {paths['wordcloud_png']}")

    print("\n상위 단어")
    for word, word_count in result["top_words"]:
        print(f"{word}: {word_count}")


if __name__ == "__main__":
    main()
