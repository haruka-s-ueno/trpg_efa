import re
from pathlib import Path

# 入出力設定
efa_path = Path("efa_lite.html")
output_dir = Path("sections")
header_path = Path("sections/_common_header.html")
footer_path = Path("sections/_common_footer.html")

output_dir.mkdir(exist_ok=True)
html = efa_path.read_text(encoding="utf-8")

# STEP 1: 階層対応：画像・CSSのパスを ../ に補正、目次のヘッダー変換
def adjust_paths(text: str) -> str:
    text = re.sub(r'href="css/', r'href="../css/', text)
    text = re.sub(r'src="images/', r'src="../images/', text)
    text = re.sub(r'href="#00_toc"', r'href="00_toc.html#00_toc"', text)
    return text
html = adjust_paths(html)

# STEP 2: 既存章コメント削除
comment_block_pattern = re.compile(
    r'\n?\s*<![-=]{10,}[\s\S]{0,500}?-{10,}>\s*\n?',  # 前後の改行・空白も含めて削除
    re.MULTILINE
)
html = re.sub(comment_block_pattern, '', html)

# STEP 3: <h1 id="..."> 検出
h1_matches = list(re.finditer(r'<h1 id="([^"]+)">(.*?)</h1>', html))
if not h1_matches:
    raise RuntimeError("章の <h1 id=...> が見つかりません")

first_h1_pos = h1_matches[0].start()
last_body_pos = html.rfind("</body>")
header = html[:first_h1_pos]
footer = html[last_body_pos:]

header_path.write_text(header, encoding="utf-8")
footer_path.write_text(footer, encoding="utf-8")

# STEP 4: id→ファイル名辞書作成
id_to_file = {}
chapter_ranges = []
for i, match in enumerate(h1_matches):
    chapter_id = match.group(1)
    chapter_title = match.group(2)
    start = match.start()
    end = h1_matches[i + 1].start() if i + 1 < len(h1_matches) else last_body_pos
    filename = f"{chapter_id}.html"
    chapter_ranges.append((chapter_id, chapter_title, start, end, filename))

    body = html[start:end]
    for m in re.finditer(r'id="([^"]+)"', body):
        anchor_id = m.group(1)
        id_to_file[anchor_id] = filename

# STEP 5: 補正処理
def patch_links(text: str) -> str:
    def repl(m):
        anchor = m.group(1)
        file = id_to_file.get(anchor)
        return f'href="{file}#{anchor}"' if file else m.group(0)
    return re.sub(r'href="#([^"]+)"', repl, text)

def make_comment(title: str) -> str:
    return (
        "\n"
        "<!--------------------------------------------------------------------------------------------------\n"
        f"-   {title}\n"
        "--------------------------------------------------------------------------------------------------->"
    )

def insert_heading_comments(text: str) -> str:
    def repl(match):
        tag, _id, title = match.group(1), match.group(2), match.group(3)
        comment = make_comment(title)
        # コメントとタグの間に改行を入れず、文脈上の改行は元のテキスト構造に依存
        return comment + f"\n<{tag} id=\"{_id}\">{title}</{tag}>"
    return re.sub(r'<(h[23]) id="([^"]+)">(.*?)</\1>', repl, text)


# STEP 6: 章ファイル出力
for chapter_id, chapter_title, start, end, filename in chapter_ranges:
    body = html[start:end]
    body = patch_links(adjust_paths(body))
    body = insert_heading_comments(body)
    comment = make_comment(chapter_title)
    full_html = (
        header.strip() + "\n" +
        "<!--#HEADER_END-->" +
        comment + "\n" +
        body.strip() + "\n" +
        "<!--#FOOTER_START-->\n" +
        footer.strip()
    )
    (output_dir / filename).write_text(full_html, encoding="utf-8")

print("✅ 境界タグ・見出しコメント付きで sections/*.html に出力しました。")
