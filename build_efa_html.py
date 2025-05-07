from pathlib import Path
import re

# パス設定
sections_dir = Path("sections")
header_path = Path("sections/_common_header.html")
footer_path = Path("sections/_common_footer.html")
output_path = Path("efa_lite_full.html")

# ヘッダー・フッター読み込み
header = header_path.read_text(encoding="utf-8")
footer = footer_path.read_text(encoding="utf-8")

# 章ファイル一覧（昇順）
section_files = sorted(f for f in sections_dir.glob("*.html") if not f.name.startswith("_"))

# 本文抽出（境界タグ間のみ）
def extract_body(path: Path) -> str:
    html = path.read_text(encoding="utf-8")
    body_start = html.find("<!--#HEADER_END-->")
    body_end   = html.find("<!--#FOOTER_START-->")
    return html[body_start + len("<!--#HEADER_END-->"):body_end].strip()

# ファイル名付きリンク除去
def strip_filenames_from_links(text: str) -> str:
    return re.sub(r'href="[^"]+?\.html(#.*?)"', r'href="\1"', text)

# 相対パス復元（sections/からの ../css/ → ルート基準へ）
def restore_paths(text: str) -> str:
    text = re.sub(r'href="\.\./css/', r'href="css/', text)
    text = re.sub(r'src="\.\./images/', r'src="images/', text)
    return text

# 本文結合と後処理
full_body = "\n\n".join(extract_body(f) for f in section_files)
full_html = header + "\n" + full_body + "\n" + footer
full_html = strip_filenames_from_links(full_html)
full_html = restore_paths(full_html)

# 出力
output_path.write_text(full_html, encoding="utf-8")
print("✅ 結合完了：efa_lite_full.html に出力されました（リンク・パス復元済）")
