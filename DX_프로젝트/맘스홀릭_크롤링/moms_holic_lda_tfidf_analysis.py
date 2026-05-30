import argparse
import csv
import importlib
import re
import site
import subprocess
import sys
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
LOCAL_PACKAGE_DIR = BASE_DIR.parents[1] / ".python_packages"
INPUT_PRIORITY = [
    "moms_holic_filtered.csv",
    "moms_holic_raw.csv",
    "moms_holic_filtered_pipe.txt",
    "moms_holic_raw_pipe.txt",
]

if LOCAL_PACKAGE_DIR.exists():
    local_package_path = str(LOCAL_PACKAGE_DIR.resolve())
    sys.path = [path for path in sys.path if path != local_package_path]
    sys.path.insert(0, local_package_path)
    site.addsitedir(local_package_path)
    importlib.invalidate_caches()


DEFAULT_STOPWORDS = {
    "그리고", "그러나", "그래서", "하지만", "또는", "혹은", "저는", "제가", "우리",
    "너무", "정말", "진짜", "그냥", "조금", "많이", "완전", "계속", "이번", "요즘",
    "오늘", "내일", "어제", "지금", "이제", "때문", "관련", "경우", "정도", "부분",
    "생각", "느낌", "사람", "분들", "여러분", "이거", "저거", "그거", "여기", "저기",
    "카페", "네이버", "맘스홀릭", "맘스홀릭베이비", "본문", "댓글", "작성", "게시글",
    "보기", "로그인", "검색", "이웃", "공유", "스크랩", "출처", "링크", "http", "https",
    "것", "것은", "것이", "것을", "것도", "것만", "것과", "것의", "것으로", "것이다",
    "거", "거는", "거를", "거라", "거라고", "거예요", "거에요", "겁니다", "건가요",
    "수", "있는", "있다", "있고", "있어", "있어서", "있으면", "있는데", "있습니다",
    "없는", "없다", "없고", "없어", "없어서", "없으면", "없는데", "없습니다",
    "아니다", "아닌", "아니고", "아니라", "아니면", "아니어서", "아니지만",
    "하다", "하는", "하고", "해서", "하면", "하면서", "합니다", "하세요", "했어요",
    "되다", "되는", "되고", "돼서", "되면", "됩니다", "됐다", "된다고",
    "같다", "같은", "같고", "같아서", "같으면", "같아요", "같습니다",
    "이다", "이며", "이고", "이라", "이라서", "입니다", "였어요", "예요", "에요",
    "저희", "제가", "저도", "저만", "저희가", "저희는", "저희도",
    "나도", "나는", "내가", "내게", "제게", "저한테", "저에게",
    "하면", "해서", "해도", "해요", "하고", "하고요", "하니", "하니까",
}

NOISE_TOKEN_PATTERNS = [
    re.compile(r"^것(이다|은|는|을|를|이|가|도|만|과|의|으로|처럼|같다|같은)?$"),
    re.compile(r"^거(다|는|를|라|라고|예요|에요|같다|같은)?$"),
    re.compile(r"^아니(다|고|라|면|어서|지만|에요|예요)?$"),
    re.compile(r"^있(다|는|고|어|어서|으면|는데|습니다)?$"),
    re.compile(r"^없(다|는|고|어|어서|으면|는데|습니다)?$"),
    re.compile(r"^하(다|는|고|면|면서|니까|세요|지만|려고|더라)?$"),
    re.compile(r"^되(다|는|고|면|어서|니까|었다|더라)?$"),
    re.compile(r"^같(다|은|고|아서|으면|아요|습니다)?$"),
]


def install_packages(packages):
    LOCAL_PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--target",
        str(LOCAL_PACKAGE_DIR),
        *packages,
    ]
    subprocess.check_call(command)

    local_package_path = str(LOCAL_PACKAGE_DIR.resolve())
    if local_package_path not in sys.path:
        sys.path.insert(0, local_package_path)
    site.addsitedir(local_package_path)
    importlib.invalidate_caches()


def ensure_packages(auto_install=True):
    missing = []
    for module_name, package_name in [
        ("pandas", "pandas"),
        ("sklearn", "scikit-learn"),
    ]:
        if importlib.util.find_spec(module_name) is None:
            missing.append(package_name)

    if not missing:
        return

    if not auto_install:
        names = " ".join(missing)
        raise SystemExit(
            f"필수 패키지가 없습니다: {names}\n"
            f"설치: {sys.executable} -m pip install --target \"{LOCAL_PACKAGE_DIR}\" {names}"
        )

    print(f"필수 패키지 자동 설치 중: {', '.join(missing)}")
    install_packages(missing)


def find_input_file():
    input_files = find_all_input_files()
    if not input_files:
        raise FileNotFoundError("분석할 크롤링 결과 파일을 찾지 못했습니다.")
    return max(input_files, key=lambda path: path.stat().st_mtime)


def find_all_input_files():
    input_files = []
    for folder in sorted(BASE_DIR.iterdir()):
        if not folder.is_dir() or folder.name.startswith("_"):
            continue
        for file_name in INPUT_PRIORITY:
            path = folder / file_name
            if path.exists() and path.stat().st_size > 0:
                input_files.append(path)
                break
    return input_files


def read_pipe_file(path):
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("||", 2)
            if len(parts) == 3:
                rows.append({"keyword": parts[0], "url": parts[1], "content": parts[2]})
    return rows


def load_data(path):
    import pandas as pd

    if path.suffix.lower() == ".txt":
        df = pd.DataFrame(read_pipe_file(path))
    else:
        df = pd.read_csv(path, encoding="utf-8-sig")

    if "content" not in df.columns:
        raise ValueError(f"content 컬럼이 없습니다. 현재 컬럼: {list(df.columns)}")

    for column in ["keyword", "url"]:
        if column not in df.columns:
            df[column] = ""

    df["content"] = df["content"].fillna("").astype(str)
    df = df[df["content"].str.strip().ne("")].copy()
    df = df.drop_duplicates(subset=["content"]).reset_index(drop=True)
    return df[["keyword", "url", "content"]]


def clean_text(text):
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[0-9]+", " ", text)
    text = re.sub(r"[^가-힣A-Za-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_useful_token(word, stopwords):
    word = word.strip().lower()
    if len(word) < 2 or word in stopwords:
        return False
    if any(pattern.match(word) for pattern in NOISE_TOKEN_PATTERNS):
        return False
    if re.fullmatch(r"[ㅋㅎㅠㅜ]+", word):
        return False
    return True


def make_tokenizer(stopwords):
    try:
        from kiwipiepy import Kiwi
    except Exception:
        try:
            print("kiwipiepy가 없어 자동 설치를 시도합니다.")
            install_packages(["kiwipiepy"])
            from kiwipiepy import Kiwi
        except Exception as exc:
            print(f"kiwipiepy 설치 또는 로딩 실패. 정규식 토큰화로 진행합니다: {exc}")
            Kiwi = None

    if Kiwi:
        kiwi = Kiwi()

        def tokenize_with_kiwi(text):
            tokens = []
            for token in kiwi.tokenize(clean_text(text)):
                if token.tag.startswith(("NN", "VA", "VV", "XR", "SL")):
                    word = token.form.strip().lower()
                    if is_useful_token(word, stopwords):
                        tokens.append(word)
            return tokens

        return tokenize_with_kiwi

    def tokenize_with_regex(text):
        words = re.findall(r"[가-힣A-Za-z]{2,}", clean_text(text).lower())
        return [word for word in words if is_useful_token(word, stopwords)]

    return tokenize_with_regex


def load_stopwords(extra_stopwords):
    stopwords = set(DEFAULT_STOPWORDS)
    for path in extra_stopwords:
        if not path.exists():
            continue
        with path.open(encoding="utf-8-sig") as f:
            for row in csv.reader(f):
                if row and row[0].strip():
                    stopwords.add(row[0].strip().lower())
    return stopwords


def sanitize_filename(name):
    name = re.sub(r'[\\/:*?"<>|]+', " ", str(name)).strip()
    name = re.sub(r"\s+", "_", name)
    return name or "맘스홀릭"


def keyword_from_input(input_path, df):
    keywords = [str(value).strip() for value in df["keyword"].dropna().unique() if str(value).strip()]
    if len(keywords) == 1:
        return sanitize_filename(keywords[0])

    folder_name = input_path.parent.name
    folder_name = re.sub(r"_?맘스홀릭.*$", "", folder_name).strip("_ ")
    return sanitize_filename(folder_name or "맘스홀릭")


def output_paths(input_path, df, output_dir):
    keyword = keyword_from_input(input_path, df)
    return {
        "overall": output_dir / f"{keyword}_전체_tfidf.csv",
        "cluster": output_dir / f"{keyword}_군집별_tfidf.csv",
        "document": output_dir / f"{keyword}_문서별_군집.csv",
    }


def outputs_exist(paths):
    return [path for path in paths.values() if path.exists()]


def save_tfidf_words(tfidf_matrix, feature_names, output_path, top_n):
    import pandas as pd

    scores = tfidf_matrix.sum(axis=0).A1
    top_indices = scores.argsort()[:-top_n - 1:-1]
    rows = [
        {"rank": rank, "word": feature_names[index], "tfidf_score": float(scores[index])}
        for rank, index in enumerate(top_indices, start=1)
    ]
    pd.DataFrame(rows).to_csv(output_path, index=False, encoding="utf-8-sig")


def save_cluster_words(tfidf_matrix, labels, feature_names, output_path, top_n):
    import pandas as pd

    rows = []
    cluster_keywords = {}
    for cluster_id in sorted(set(labels)):
        member_indices = [idx for idx, label in enumerate(labels) if label == cluster_id]
        if not member_indices:
            continue
        scores = tfidf_matrix[member_indices].sum(axis=0).A1
        top_indices = scores.argsort()[:-top_n - 1:-1]
        cluster_keywords[int(cluster_id)] = ", ".join(feature_names[index] for index in top_indices[:10])
        for rank, index in enumerate(top_indices, start=1):
            rows.append(
                {
                    "cluster": int(cluster_id),
                    "rank": rank,
                    "word": feature_names[index],
                    "tfidf_score": float(scores[index]),
                    "document_count": len(member_indices),
                }
            )

    pd.DataFrame(rows).to_csv(output_path, index=False, encoding="utf-8-sig")
    return cluster_keywords


def save_document_clusters(df, labels, cluster_keywords, output_path):
    result_df = df.copy()
    result_df["cluster"] = labels
    result_df["cluster_top_words"] = result_df["cluster"].map(cluster_keywords).fillna("")
    result_df.to_csv(output_path, index=False, encoding="utf-8-sig")


def choose_best_cluster_count(tfidf_matrix, max_clusters, random_state):
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    document_count = tfidf_matrix.shape[0]
    upper = min(max_clusters, document_count - 1)
    if upper < 2:
        return 1, []

    scores = []
    for cluster_count in range(2, upper + 1):
        model = KMeans(n_clusters=cluster_count, random_state=random_state, n_init=10)
        labels = model.fit_predict(tfidf_matrix)
        score = silhouette_score(tfidf_matrix, labels)
        scores.append({"cluster_count": cluster_count, "silhouette_score": float(score)})

    best = max(scores, key=lambda row: row["silhouette_score"])
    return best["cluster_count"], scores


def analyze_one(input_path, args, tokenizer):
    from sklearn.cluster import KMeans
    from sklearn.feature_extraction.text import TfidfVectorizer

    df = load_data(input_path)
    if len(df) < 2:
        print(f"건너뜀: 문서가 2개 미만입니다. {input_path}")
        return False

    output_dir = Path(args.output).resolve() if args.output and not args.all else input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = output_paths(input_path, df, output_dir)
    existing_outputs = outputs_exist(paths)
    if existing_outputs and not args.overwrite:
        print(f"건너뜀: 기존 결과 파일이 있어 덮어쓰지 않습니다. {input_path}")
        for path in existing_outputs:
            print(f"  - {path}")
        return False

    max_features = min(args.max_features, max(20, len(df) * 30))
    tfidf_vectorizer = TfidfVectorizer(
        tokenizer=tokenizer,
        token_pattern=None,
        max_features=max_features,
        min_df=args.min_df,
        max_df=args.max_df,
    )
    tfidf_matrix = tfidf_vectorizer.fit_transform(df["content"])
    tfidf_features = tfidf_vectorizer.get_feature_names_out()

    if args.clusters and args.clusters > 0:
        cluster_count = max(1, min(args.clusters, len(df)))
        silhouette_scores = []
    else:
        cluster_count, silhouette_scores = choose_best_cluster_count(
            tfidf_matrix=tfidf_matrix,
            max_clusters=args.max_clusters,
            random_state=args.random_state,
        )

    if cluster_count == 1:
        cluster_labels = [0] * len(df)
    else:
        kmeans = KMeans(n_clusters=cluster_count, random_state=args.random_state, n_init=10)
        cluster_labels = kmeans.fit_predict(tfidf_matrix)

    save_tfidf_words(tfidf_matrix, tfidf_features, paths["overall"], args.top_words)
    cluster_keywords = save_cluster_words(tfidf_matrix, cluster_labels, tfidf_features, paths["cluster"], args.top_words)
    save_document_clusters(df, cluster_labels, cluster_keywords, paths["document"])

    cluster_counts = Counter(cluster_labels)
    print("분석 완료")
    print(f"- 입력 파일: {input_path}")
    print(f"- 문서 수: {len(df)}")
    print(f"- 선택된 군집 수: {cluster_count}")
    if silhouette_scores:
        score_text = ", ".join(
            f"k={row['cluster_count']}:{row['silhouette_score']:.4f}"
            for row in silhouette_scores
        )
        print(f"- 실루엣 점수: {score_text}")
    print(f"- 군집별 문서 수: {dict(sorted(cluster_counts.items()))}")
    print(f"- 전체 TF-IDF: {paths['overall']}")
    print(f"- 군집별 TF-IDF: {paths['cluster']}")
    print(f"- 문서별 군집: {paths['document']}")
    return True


def analyze(args):
    ensure_packages(auto_install=not args.no_install)
    stopwords = load_stopwords([Path(path) for path in args.stopwords])
    tokenizer = make_tokenizer(stopwords)

    if args.all:
        input_files = find_all_input_files()
        if not input_files:
            raise FileNotFoundError("분석할 크롤링 결과 파일을 찾지 못했습니다.")
    else:
        input_files = [Path(args.input).resolve() if args.input else find_input_file()]

    completed = 0
    skipped = 0
    for input_path in input_files:
        try:
            if analyze_one(input_path, args, tokenizer):
                completed += 1
            else:
                skipped += 1
        except Exception as exc:
            skipped += 1
            print(f"실패: {input_path}")
            print(f"  - {exc}")

    print(f"전체 처리 결과: 완료 {completed}개, 건너뜀/실패 {skipped}개")


def parse_args():
    parser = argparse.ArgumentParser(description="Moms Holic crawled text TF-IDF and clustering analysis")
    parser.add_argument("--input", help="moms_holic_filtered.csv, moms_holic_raw.csv, or pipe txt path")
    parser.add_argument("--all", action="store_true", help="analyze every crawling result folder")
    parser.add_argument("--output", help="analysis output directory. Ignored with --all; each folder gets its own files.")
    parser.add_argument("--overwrite", action="store_true", help="overwrite existing TF-IDF result files")
    parser.add_argument("--clusters", type=int, default=0, help="KMeans cluster count. 0 means auto by silhouette score.")
    parser.add_argument("--max-clusters", type=int, default=10, help="maximum cluster count for silhouette search")
    parser.add_argument("--top-words", type=int, default=30, help="top word count per result")
    parser.add_argument("--max-features", type=int, default=3000, help="maximum vocabulary size")
    parser.add_argument("--min-df", type=int, default=2, help="minimum document frequency")
    parser.add_argument("--max-df", type=float, default=0.85, help="maximum document frequency ratio")
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--stopwords", nargs="*", default=[], help="extra stopword csv/txt files")
    parser.add_argument("--install-missing", action="store_true", help="kept for compatibility; missing packages install automatically")
    parser.add_argument("--no-install", action="store_true", help="do not install missing packages automatically")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.install_missing:
        ensure_packages(auto_install=True)
    analyze(args)


if __name__ == "__main__":
    main()
