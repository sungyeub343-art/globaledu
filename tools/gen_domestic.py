"""Regenerate the 17 domestic region pages (seoul.html ...) with school-specific content.

Usage: python tools/gen_domestic.py
District names are kept from the current page files. Run tools/add_footer_links.py afterwards.
"""
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

SITE = Path(__file__).resolve().parent.parent
BASE = "https://globaledu.kr/"
NOTE = "학교 정보는 2026년 10월 공개 자료를 바탕으로 정리한 요약입니다. 개설 과정과 입학 조건은 학교 공식 안내에서 다시 확인해 주세요."

SERVICES = [
    ("IB Diploma·MYP", "IB Math AA·AI, English A, Physics·Chemistry와 IA·EE·TOK 마감 일정을 학교 진도에 맞춰 관리합니다."),
    ("AP·Digital SAT", "미국식 학교 학생의 AP Calculus·Physics·Chemistry·English와 Digital SAT를 목표 점수와 시험일에 맞춰 준비합니다."),
    ("IGCSE·A-Level", "영국식 학교의 IGCSE 수학·영어와 A-Level 수학·과학을 Cambridge·Edexcel 시험 보드 기출 위주로 준비합니다."),
    ("입학·귀국 학생 관리", "국제학교·외국인학교 입학 영어·수학 평가와 해외에서 귀국한 학생의 학교 적응을 함께 관리합니다."),
]

# schools: (English name, Korean label, tags). Leave empty when no international/foreign school is listed.
REGIONS = [
    {"slug": "seoul", "name": "서울특별시", "short": "서울", "eyebrow": "Seoul",
     "title": "서울 국제학교 과외 | 덜위치·드와이트·SFS·YISS IB·AP·SAT 1:1",
     "desc": "서울 덜위치 칼리지 서울, 드와이트 스쿨 서울, 서울외국인학교(SFS), 용산국제학교(YISS), 한국켄트외국인학교 학생을 위한 IB·AP·IGCSE·SAT 수학·영어 1:1 방문·화상 과외.",
     "lead": "서울에는 반포의 덜위치 칼리지, 상암의 드와이트 스쿨, 연희동의 서울외국인학교처럼 커리큘럼이 서로 다른 국제학교·외국인학교가 모여 있습니다. 학교마다 다른 IB·AP·IGCSE 과정과 시험 일정에 맞춰 수학·영어를 관리합니다.",
     "schools": [
         ("Dulwich College Seoul", "덜위치 칼리지 서울 · 서초구 반포", ["IGCSE", "IB"]),
         ("Dwight School Seoul", "드와이트 스쿨 서울 · 마포구 상암", ["IB"]),
         ("Seoul Foreign School", "서울외국인학교 (SFS) · 서대문구 연희동", ["IB"]),
         ("Yongsan International School of Seoul", "용산국제학교 (YISS) · 용산구", ["AP", "미국식"]),
         ("Korea Kent Foreign School", "한국켄트외국인학교 · 광진구", ["AP", "미국식"]),
         ("Asia Pacific International School", "아시아퍼시픽국제외국인학교 · 노원구", ["미국식"]),
     ],
     "faq": [("강남·서초에 사는데 방문 수업이 가능한가요?", "가능합니다. 서울 지역은 방문 수업과 화상 수업 중 학생 일정에 맞는 방식을 선택할 수 있습니다."),
             ("학교마다 커리큘럼이 다른데 모두 수업하나요?", "네. 덜위치(IGCSE·IB), 드와이트(IB), YISS·켄트(AP)처럼 학교 과정별로 진도표와 과제를 확인해 수업을 구성합니다.")]},
    {"slug": "gyeonggi", "name": "경기도", "short": "경기", "eyebrow": "Gyeonggi",
     "title": "판교·수원 국제학교 과외 | KIS·SIS·GSIS IB·AP·SAT 1:1 | 경기",
     "desc": "판교 한국국제학교(KIS), 성남 서울국제학교(SIS), 경기수원국제학교(GSIS), 청심국제중고 학생을 위한 IB·AP·SAT 수학·영어 1:1 방문·화상 과외.",
     "lead": "경기도에는 판교의 한국국제학교(KIS), 성남의 서울국제학교(SIS), 수원의 경기수원국제학교(GSIS)가 있어 미국식 AP 과정과 IB 과정 학생이 함께 많습니다. 학교 과정과 통학 동선에 맞춰 수학·영어 수업을 배치합니다.",
     "schools": [
         ("Korea International School (Pangyo)", "한국국제학교 KIS · 성남시 판교", ["AP", "미국식"]),
         ("Seoul International School", "서울국제학교 SIS · 성남시", ["AP", "미국식"]),
         ("Gyeonggi Suwon International School", "경기수원국제학교 GSIS · 수원시", ["IB"]),
         ("Cheongshim International Academy", "청심국제중·고 · 가평군 (국내 특목)", ["국내 특목", "영어"]),
     ],
     "faq": [("판교 KIS 학생도 방문 수업이 되나요?", "가능합니다. 판교·분당·용인 지역은 방문 수업과 화상 수업 중 선택할 수 있습니다."),
             ("GSIS IB 과정 학생도 수업하나요?", "네. IB Math·English와 IA·EE 마감 일정, 5월 IB 시험 대비를 함께 관리합니다.")]},
    {"slug": "incheon", "name": "인천광역시", "short": "인천·송도", "eyebrow": "Incheon · Songdo",
     "title": "송도 국제학교 과외 | 채드윅 송도 IB·SAT 수학·영어 1:1 | 인천",
     "desc": "인천 송도 채드윅 송도국제학교(Chadwick International) 학생을 위한 IB MYP·DP, Digital SAT 수학·영어 1:1 방문·화상 과외와 송도 국제도시 학생 관리.",
     "lead": "송도 국제도시의 채드윅 송도국제학교(Chadwick International)는 IB 과정을 운영하는 대표적인 국내 국제학교입니다. MYP부터 DP까지 학년별 과제와 평가 일정에 맞춰 수학·영어를 관리합니다.",
     "schools": [
         ("Chadwick International", "채드윅 송도국제학교 · 연수구 송도", ["IB"]),
     ],
     "faq": [("채드윅 MYP 학생도 수업하나요?", "네. MYP 수학·영어의 단원 평가(Criteria)와 과제를 학교 일정에 맞춰 준비하고, DP 진학 전 과목 선택도 함께 상담합니다."),
             ("송도 지역 방문 수업이 가능한가요?", "가능합니다. 송도·연수구는 방문 수업과 화상 수업 중 학생 일정에 맞는 방식을 선택할 수 있습니다.")]},
    {"slug": "jeju", "name": "제주특별자치도", "short": "제주", "eyebrow": "Jeju Global Education City",
     "title": "제주 국제학교 과외 | NLCS·브랭섬홀·KIS·SJA 제주 IB·AP 1:1",
     "desc": "제주영어교육도시 NLCS 제주, 브랭섬홀 아시아, KIS 제주, 세인트존스베리 아카데미 제주 학생을 위한 IB·IGCSE·AP·SAT 수학·영어 1:1 화상 과외.",
     "lead": "서귀포 대정읍 제주영어교육도시에는 NLCS 제주, 브랭섬홀 아시아, KIS 제주, 세인트존스베리 아카데미 제주가 모여 있습니다. 기숙사 생활 학생이 많아 학교 일과를 피해 화상 수업으로 수학·영어를 관리합니다.",
     "schools": [
         ("North London Collegiate School Jeju", "NLCS 제주 · 영국식", ["IGCSE", "IB"]),
         ("Branksome Hall Asia", "브랭섬홀 아시아 · 여학교", ["IB"]),
         ("Korea International School Jeju", "KIS 제주", ["국제학교"]),
         ("St. Johnsbury Academy Jeju", "세인트존스베리 아카데미 제주 · 미국식", ["AP", "미국식"]),
     ],
     "faq": [("기숙사에 있는데 수업 시간을 낼 수 있나요?", "기숙사 자습·소등 시간을 피해 주중 저녁이나 주말로 정합니다. 학교 일정표를 보고 함께 조율합니다."),
             ("서울·경기에 살면서 주말에만 집에 오는 학생도 가능한가요?", "가능합니다. 주중에는 화상 수업, 주말에는 집에서 방문 수업으로 나눠 진행할 수 있습니다.")]},
    {"slug": "busan", "name": "부산광역시", "short": "부산", "eyebrow": "Busan",
     "title": "부산 국제학교 과외 | 부산외국인학교 AP·IB·SAT 수학·영어 1:1",
     "desc": "부산외국인학교(BFS), 부산국제외국인학교(BIFS) 등 부산 외국인학교·국제학교 학생과 해외 귀국 학생을 위한 AP·IB·SAT 수학·영어 1:1 방문·화상 과외.",
     "lead": "부산에는 해운대 일대의 외국인학교와 국제학교가 있고, 해외 근무 후 귀국한 가정도 많습니다. 학교 과정(AP·IB)과 학생 영어 수준에 맞춰 수학·영어를 관리합니다.",
     "schools": [
         ("Busan Foreign School", "부산외국인학교 (BFS)", ["외국인학교", "미국식"]),
         ("Busan International Foreign School", "부산국제외국인학교 (BIFS)", ["외국인학교"]),
     ],
     "faq": [("해운대 지역 방문 수업이 가능한가요?", "가능합니다. 해운대·수영구 등은 방문 수업과 화상 수업 중 선택할 수 있습니다."),
             ("해외에서 귀국한 학생의 영어 유지 수업도 하나요?", "네. 영어 원서 읽기·에세이·토론 수업으로 영어 실력을 유지하면서 국내 학교 일정에 맞춰 진행합니다.")]},
    {"slug": "daegu", "name": "대구광역시", "short": "대구", "eyebrow": "Daegu",
     "title": "대구 국제학교 과외 | 대구국제학교 AP·SAT 수학·영어 1:1",
     "desc": "대구국제학교(DIS) 학생과 해외 귀국·국제학교 진학 준비 학생을 위한 AP·SAT·IB 수학·영어 1:1 방문·화상 과외. 수성구·달서구 수업 가능.",
     "lead": "대구에는 미국식 과정을 운영하는 대구국제학교(DIS)가 있고, 수성구를 중심으로 국제학교 진학과 해외 대학 준비 수요가 꾸준합니다. 학교 과정과 목표 시험에 맞춰 수학·영어를 관리합니다.",
     "schools": [("Daegu International School", "대구국제학교 (DIS)", ["미국식", "AP"])],
     "faq": [("수성구 방문 수업이 가능한가요?", "가능합니다. 수성구·달서구 등은 방문 수업과 화상 수업 중 선택할 수 있습니다."),
             ("국제학교 입학 시험 준비도 하나요?", "네. 영어 읽기·쓰기와 수학 진단 평가를 기준으로 입학 전 부족한 부분을 보완합니다.")]},
    {"slug": "daejeon", "name": "대전광역시", "short": "대전", "eyebrow": "Daejeon",
     "title": "대전 국제학교 과외 | TCIS 대전외국인학교 IB·SAT 수학·영어 1:1",
     "desc": "대전외국인학교(TCIS) 학생과 대덕연구단지·KAIST 연구원 가정의 국제학교·귀국 학생을 위한 IB·AP·SAT 수학·영어 1:1 방문·화상 과외.",
     "lead": "대전 유성구에는 IB 과정을 운영하는 대전외국인학교(TCIS)가 있고, 대덕연구단지·대학 연구원 가정의 해외 귀국 학생이 많습니다. 학교 과정과 귀국 일정에 맞춰 수학·영어를 관리합니다.",
     "schools": [("Taejon Christian International School", "대전외국인학교 (TCIS) · 유성구", ["IB"])],
     "faq": [("유성구 방문 수업이 가능한가요?", "가능합니다. 유성구·서구 등은 방문 수업과 화상 수업 중 선택할 수 있습니다."),
             ("연구년으로 해외에 나갔다 온 학생도 수업하나요?", "네. 해외 학교에서 배운 과정과 국내 학교 진도의 차이를 확인해 영어 유지와 수학 보완을 함께 진행합니다.")]},
    {"slug": "ulsan", "name": "울산광역시", "short": "울산", "eyebrow": "Ulsan",
     "title": "울산 국제학교 과외 | 현대외국인학교·해외 귀국 학생 수학·영어 1:1",
     "desc": "울산 현대외국인학교 학생과 조선·자동차·석유화학 기업 해외 근무 후 귀국한 학생을 위한 AP·IB·SAT 수학·영어 1:1 방문·화상 과외.",
     "lead": "울산 동구에는 현대외국인학교가 있고, 조선·자동차·석유화학 기업의 해외 법인 근무 후 귀국한 가정이 많습니다. 학교 과정과 귀국 시점에 맞춰 수학·영어를 관리합니다.",
     "schools": [("Hyundai Foreign School", "현대외국인학교 · 동구", ["외국인학교"])],
     "faq": [("해외 주재 후 귀국한 학생의 영어 유지 수업도 하나요?", "네. 영어 원서 읽기·에세이 수업으로 실력을 유지하면서 국내 학교 일정에 맞춰 진행합니다."),
             ("다시 해외로 나갈 예정인데 미리 준비할 수 있나요?", "가능합니다. 갈 나라의 학교 과정(AP·IB·IGCSE)을 확인해 수학 용어와 영어 과제 방식부터 미리 준비합니다.")]},
]

# Regions without a listed international school: content focuses on returning students and boarding-school students.
OTHER = [
    ("gwangju", "광주광역시", "광주", "Gwangju", "광주 지역은 해외 근무·연구년 후 귀국한 학생과, 송도·제주 국제학교나 해외 보딩스쿨에 진학하려는 학생 수요가 있습니다."),
    ("sejong", "세종특별자치시", "세종", "Sejong", "세종은 정부부처 공무원 가정이 많아 해외 파견을 마치고 귀국한 학생이나 파견을 앞둔 학생의 영어·수학 수요가 많습니다."),
    ("gangwon", "강원특별자치도", "강원", "Gangwon", "강원 지역은 원주·춘천을 중심으로 국제학교·보딩스쿨 진학 준비 학생과 제주·송도 국제학교에 다니며 방학에 집에 오는 학생이 있습니다."),
    ("chungcheongbukdo", "충청북도", "충북", "Chungbuk", "충북은 청주·오송·진천 지역 기업과 연구기관 가정의 해외 귀국 학생, 국제학교 진학 준비 학생 수요가 있습니다."),
    ("chungcheongnamdo", "충청남도", "충남", "Chungnam", "충남 천안·아산은 디스플레이·반도체 기업의 해외 법인 근무 후 귀국한 가정과 해외 파견을 앞둔 가정이 많습니다."),
    ("jeonbuk", "전북특별자치도", "전북", "Jeonbuk", "전북은 전주·익산·군산을 중심으로 해외 귀국 학생과 국제학교·해외 보딩스쿨 진학 준비 학생 수요가 있습니다."),
    ("jeonnam", "전라남도", "전남", "Jeonnam", "전남 여수·광양·순천은 석유화학·철강 기업의 해외 근무 후 귀국한 가정과 해외 파견을 앞둔 가정의 수요가 있습니다."),
    ("gyeongsangbukdo", "경상북도", "경북", "Gyeongbuk", "경북 포항·구미는 철강·전자 기업의 해외 법인 근무 후 귀국한 가정과 해외 파견을 앞둔 가정의 영어·수학 수요가 있습니다."),
    ("gyeongsangnamdo", "경상남도", "경남", "Gyeongnam", "경남 창원·거제·김해는 기계·조선 기업의 해외 근무 후 귀국한 가정과 해외 파견을 앞둔 가정의 수요가 있습니다."),
]
for slug, name, short, eyebrow, lead in OTHER:
    REGIONS.append({
        "slug": slug, "name": name, "short": short, "eyebrow": eyebrow,
        "title": f"{short} 국제학교 과외 | 해외 귀국·국제학교 진학 IB·AP·SAT 1:1",
        "desc": f"{name} 해외 귀국 학생, 국제학교·보딩스쿨 재학생과 진학 준비 학생을 위한 IB·AP·IGCSE·SAT 수학·영어 1:1 방문·화상 과외.",
        "lead": lead + " 학생이 다녔던(또는 다닐) 학교 과정에 맞춰 수학·영어를 관리합니다.",
        "schools": [],
        "faq": [(f"{short} 지역에는 국제학교가 많지 않은데 어떤 학생이 수업하나요?", "해외에서 귀국한 학생의 영어 유지, 송도·제주 국제학교나 해외 보딩스쿨 재학생의 방학·주말 관리, 국제학교 진학 준비 학생이 주로 수업합니다."),
                ("방문 수업도 가능한가요?", "지역과 일정에 따라 방문 수업이 가능한지 상담 시 안내하며, 화상 수업은 어느 지역이든 진행할 수 있습니다.")],
    })


def esc(s):
    return html.escape(s, quote=True)


def districts_from(page):
    s = page.read_text(encoding="utf-8")
    # Domestic city cards only (the aside uses stat-box). Cards from a previous run carry <small>지역 수업</small>.
    return re.findall(r'<article class="city-card">\s*<strong>([^<]+)</strong>', s)


def render(r, districts):
    slug, name = r["slug"], r["name"]
    url = BASE + slug + ".html"
    cu = "consult.html?region=" + quote(name)
    faq_all = r["faq"] + [("수업은 어떻게 진행되나요?", "첫 상담에서 학교·학년·수강 과목과 최근 성적을 확인하고, 방문 또는 Zoom 화상 1:1 수업으로 주간 계획에 맞춰 진행합니다.")]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "지역별 안내", "item": BASE + "regions.html"},
            {"@type": "ListItem", "position": 3, "name": name, "item": url}]},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_all]},
    ]}
    o = [f"""<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{esc(r['title'])} | IB아이비</title>
    <meta name="description" content="{esc(r['desc'])}" />
    <link rel="canonical" href="{url}" />
    <meta property="og:type" content="website" />
    <meta property="og:locale" content="ko_KR" />
    <meta property="og:site_name" content="IB아이비" />
    <meta property="og:title" content="{esc(r['title'])}" />
    <meta property="og:description" content="{esc(r['desc'])}" />
    <meta property="og:url" content="{url}" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Noto+Serif+KR:wght@500;700&display=swap" rel="stylesheet" />
    <link rel="icon" href="favicon.svg?v=1" type="image/svg+xml" />
    <link rel="stylesheet" href="styles.css" />
    <script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
    </script>
  </head>
  <body>
    <div class="bg-orb orb-a" aria-hidden="true"></div><div class="bg-orb orb-b" aria-hidden="true"></div>
    <header class="site-header">
      <a class="brand" href="index.html"><span class="brand-mark">G</span><span>IB아이비</span></a>
      <nav class="top-nav"><a href="igcse-tutoring.html">IGCSE</a><a href="ib-tutoring.html">IB</a><a href="ap-tutoring.html">AP</a><a href="sat-tutoring.html">SAT</a><a href="regions.html">국내 지역</a><a href="overseas.html">해외 지역</a><a class="nav-cta" href="consult.html">상담 신청</a></nav>
    </header>
    <main class="page-shell">
      <div class="breadcrumbs" aria-label="breadcrumb"><a href="index.html">홈</a><span>›</span><a href="regions.html">지역별 안내</a><span>›</span><span>{esc(name)}</span></div>
      <section class="page-hero reveal">
        <p class="eyebrow">{esc(r['eyebrow'])}</p>
        <h1>{esc(r['short'])} 국제학교 과외<br />IB·AP·IGCSE·SAT 수학·영어 1:1</h1>
        <p>{esc(r['lead'])}</p>
        <div class="hero-actions"><a class="btn btn-primary" href="{cu}">상담 신청</a><a class="btn btn-ghost" href="tel:01029283614">전화상담 010-2928-3614</a></div>
      </section>
      <section class="detail-layout reveal">
        <div>
"""]
    if r["schools"]:
        o.append(f"""          <div class="section-title-wrap"><p class="eyebrow">Schools</p><h2>{esc(r['short'])} 국제학교·외국인학교</h2></div>
          <div class="city-grid">
""")
        for en, ko, tags in r["schools"]:
            o.append(f"""            <article class="school-card city-card"><strong>{esc(en)}</strong><small>{esc(ko)}</small><div class="city-meta">{''.join(f'<span>{esc(t)}</span>' for t in tags)}</div></article>
""")
        o.append(f"""          </div>
          <p class="section-lead">{esc(NOTE)}</p>
""")
    o.append(f"""          <div class="section-title-wrap"><p class="eyebrow">Districts</p><h2>{esc(name)} 수업 지역</h2></div>
          <div class="city-grid">
""")
    for d in districts:
        o.append(f"""            <article class="city-card">
              <strong>{esc(d)}</strong><small>지역 수업</small><div class="city-meta"><span>방문</span><span>화상</span></div></article>
""")
    o.append(f"""          </div>
        </div>
        <aside>
          <div class="stat-box"><h3>수업 방식</h3><strong>방문·화상</strong><p>지역과 학생 일정에 맞춰 방문 또는 Zoom 1:1 수업을 선택합니다.</p></div>
          <div class="stat-box"><h3>지원 과정</h3><strong>IB·AP·IGCSE</strong><p>학교 커리큘럼과 Digital SAT·AP·IB 시험 일정에 맞춰 수업합니다.</p></div>
          <div class="stat-box"><h3>상담</h3><strong>010-2928-3614</strong><p>학교·학년·과목을 알려주시면 맞는 수업 방식과 선생님을 안내합니다.</p></div>
        </aside>
      </section>
      <section class="reveal">
        <div class="section-title-wrap"><p class="eyebrow">Programs</p><h2>{esc(r['short'])} 학생이 많이 찾는 수업</h2></div>
        <div class="info-grid">
""")
    for h, d in SERVICES:
        o.append(f"""          <article class="info-card"><h3>{esc(h)}</h3><p>{esc(d)}</p></article>
""")
    o.append("""        </div>
      </section>
      <section class="reveal">
        <div class="section-title-wrap"><p class="eyebrow">FAQ</p><h2>자주 묻는 질문</h2></div>
        <div class="faq-list">
""")
    for q, a in faq_all:
        o.append(f"""          <article class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></article>
""")
    o.append(f"""        </div>
      </section>
      <section class="banner reveal"><p>학교·학년과 수강 과목을 알려주시면 {esc(r['short'])} 지역 수업 계획을 안내합니다.</p><a class="btn btn-primary" href="tel:01029283614">전화상담 010-2928-3614</a></section>
    </main>
    <footer class="site-footer"><p>IB아이비 | {esc(name)} 국제학교 과외</p><p>Copyright © 2026 globaledu.kr All rights reserved.</p></footer>
    <script src="script.js"></script>
  </body>
</html>
""")
    return "".join(o)


if __name__ == "__main__":
    for r in REGIONS:
        page = SITE / f"{r['slug']}.html"
        districts = districts_from(page)
        assert districts, r["slug"]
        page.write_text(render(r, districts), encoding="utf-8", newline="\n")
    print("generated", len(REGIONS), "domestic pages")
