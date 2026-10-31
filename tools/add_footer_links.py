"""Site-wide SEO pass: footer internal links, sitemap lastmod and rss.xml.

Usage: python tools/add_footer_links.py   (run after gen_domestic.py / gen_overseas.py)
Idempotent: the footer block between the FOOTER markers is replaced on every run.
"""
import html
import re
import subprocess
from datetime import date
from email.utils import format_datetime
from datetime import datetime, timezone, timedelta
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
BASE = "https://globaledu.kr/"
START, END = "<!-- FOOTER-LINKS:START -->", "<!-- FOOTER-LINKS:END -->"
SKIP = {"navereb1c925a3490209acc3ac9c469f5673f.html"}

SUBJECTS = [("IGCSE 과외", "igcse-tutoring.html"), ("IB 과외", "ib-tutoring.html"), ("AP 과외", "ap-tutoring.html"),
            ("SAT 과외", "sat-tutoring.html"), ("영어과외 지역 안내", "regions.html"), ("수학과외 지역 안내", "math-regions.html")]
DOMESTIC = [("서울", "seoul"), ("경기", "gyeonggi"), ("인천·송도", "incheon"), ("제주", "jeju"), ("부산", "busan"),
            ("대구", "daegu"), ("대전", "daejeon"), ("광주", "gwangju"), ("울산", "ulsan"), ("세종", "sejong"),
            ("강원", "gangwon"), ("충북", "chungcheongbukdo"), ("충남", "chungcheongnamdo"), ("전북", "jeonbuk"),
            ("전남", "jeonnam"), ("경북", "gyeongsangbukdo"), ("경남", "gyeongsangnamdo")]


def overseas_links():
    s = (SITE / "overseas.html").read_text(encoding="utf-8")
    links = [("해외 지역 전체", "overseas.html")]
    for href, name in re.findall(r'<a class="city-card" href="([^"]+)"><strong>([^<]+)</strong>', s):
        links.append((html.unescape(name).split(" (")[0].replace(" 국제학교", ""), href))
    return links


def block():
    def row(title, items):
        return (f'        <div><strong>{title}</strong>'
                + "".join(f'<a href="{h}">{html.escape(n)}</a>' for n, h in items) + "</div>\n")
    return (f"{START}\n      <nav class=\"footer-links\" aria-label=\"사이트 바로가기\">\n"
            + row("과목별 과외", SUBJECTS)
            + row("국내 지역", [(n, s + ".html") for n, s in DOMESTIC])
            + row("해외 지역", overseas_links())
            + f"        <div><strong>상담</strong><a href=\"tel:01029283614\">전화상담 010-2928-3614</a></div>\n"
            + f"      </nav>\n      {END}")


def add_footer(path, fb):
    s = path.read_text(encoding="utf-8")
    if START in s:
        s = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda _: fb, s, flags=re.S)
    else:
        s, n = re.subn(r'(<footer class="site-footer">)', lambda m: m.group(1) + "\n      " + fb, s, count=1)
        if not n:
            return False
    path.write_text(s, encoding="utf-8", newline="\n")
    return True


def git_changed_today():
    out = subprocess.run(["git", "status", "--porcelain"], cwd=SITE, capture_output=True, text=True, encoding="utf-8").stdout
    return {line[3:].strip().strip('"') for line in out.splitlines()}


def update_sitemap(changed, today):
    path = SITE / "sitemap.xml"
    s = path.read_text(encoding="utf-8")

    def bump(m):
        loc = m.group(1)
        file = loc[len(BASE):] or "index.html"
        return f"<loc>{loc}</loc><lastmod>{today if file in changed else m.group(2)}</lastmod>"
    s = re.sub(r"<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>", bump, s)
    path.write_text(s, encoding="utf-8", newline="\n")
    return re.findall(r"<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>", s)


def write_rss(entries):
    kst = timezone(timedelta(hours=9))
    items = []
    for loc, lastmod in sorted(entries, key=lambda e: e[1], reverse=True):
        file = loc[len(BASE):] or "index.html"
        page = (SITE / file).read_text(encoding="utf-8")
        title = html.unescape(re.search(r"<title>([^<]*)</title>", page).group(1))
        desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', page)
        desc = html.unescape(desc_m.group(1)) if desc_m else title
        pub = format_datetime(datetime.fromisoformat(lastmod).replace(hour=9, tzinfo=kst))
        items.append(f"""    <item>
      <title>{html.escape(title)}</title>
      <link>{loc}</link>
      <guid>{loc}</guid>
      <description>{html.escape(desc)}</description>
      <pubDate>{pub}</pubDate>
    </item>
""")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>IB아이비 | 국제학교 IGCSE·IB·AP·SAT 과외</title>
    <link>{BASE}</link>
    <description>국제학교 학생을 위한 IGCSE·IB·AP·Digital SAT 수학·영어 1:1 과외 안내</description>
    <language>ko</language>
{''.join(items)}  </channel>
</rss>
"""
    (SITE / "rss.xml").write_text(rss, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    fb = block()
    done = [p.name for p in sorted(SITE.glob("*.html")) if p.name not in SKIP and add_footer(p, fb)]
    print("footer links:", len(done), "pages")
    today = date.today().isoformat()
    entries = update_sitemap(git_changed_today(), today)
    write_rss(entries)
    print("sitemap entries:", len(entries), "| rss.xml written")
