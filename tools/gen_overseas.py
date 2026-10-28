"""Generate overseas region pages (2nd batch) and register them in the hub, homepage and sitemap.

Usage: python tools/gen_overseas.py
Page markup matches the first batch (us-irvine.html etc.). Re-running overwrites the page files;
hub/index/sitemap edits are skipped when the slug is already registered.
"""
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

SITE = Path(__file__).resolve().parent.parent
BASE = "https://globaledu.kr/"
TODAY = "2026-10-28"
NOTE = "학교 정보는 2026년 10월 공개 자료를 바탕으로 정리한 요약입니다. 개설 과목(AP·IB·A-Level 등)과 입학 조건은 학교 공식 안내에서 다시 확인해 주세요."

TZ_PACIFIC = ("한국보다 16시간 늦음 (서머타임 해제 시 17시간)",
              "현지 평일 저녁 7~10시는 한국 다음 날 오전 11시~오후 2시(서머타임 기준)입니다. 방과 후 저녁 시간에 맞춰 Zoom 수업을 배정합니다.")
TZ_EASTERN = ("한국보다 13시간 늦음 (서머타임 해제 시 14시간)",
              "현지 평일 저녁 7~10시는 한국 다음 날 오전 8~11시(서머타임 기준)입니다. 방과 후 저녁 시간에 맞춰 Zoom 수업을 배정합니다.")
TZ_CENTRAL = ("한국보다 14시간 늦음 (서머타임 해제 시 15시간)",
              "현지 평일 저녁 7~10시는 한국 다음 날 오전 9시~정오(서머타임 기준)입니다. 방과 후 저녁 시간에 맞춰 Zoom 수업을 배정합니다.")
TZ_PLUS8 = ("한국보다 1시간 늦음", "현지 오후 4~9시는 한국 오후 5~10시입니다. 평일 방과 후 바로 수업할 수 있습니다.")
TZ_PLUS7 = ("한국보다 2시간 늦음", "현지 오후 4~8시는 한국 오후 6~10시입니다. 평일 방과 후 바로 수업할 수 있습니다.")

US_SERVICES = [
    ("AP 과목 내신·시험", "AP Calculus AB·BC, AP Physics, AP Chemistry, AP English Language 등 학교 수업 진도와 5월 AP 시험을 함께 관리합니다."),
    ("Digital SAT", "Reading and Writing과 Math를 진단해 목표 점수와 시험일에 맞춘 주간 계획을 세웁니다."),
    ("Honors·정규 수업 내신", "Algebra, Geometry, Precalculus와 English 과제·에세이를 학교 일정에 맞춰 준비합니다."),
    ("전학·적응기 관리", "한국에서 막 이주한 학생은 수업 용어와 과제 방식부터 정리해 첫 학기 성적을 안정시킵니다."),
]
SEA_SERVICES = [
    ("IB Diploma·MYP", "IB Math AA·AI, English, Physics·Chemistry와 IA·EE·TOK 일정을 함께 관리합니다."),
    ("IGCSE·A-Level", "영국식 학교의 IGCSE 수학·영어와 A-Level 수학·과학을 시험 보드에 맞춰 준비합니다."),
    ("AP·SAT", "미국식 학교 학생의 AP 과목과 Digital SAT를 목표 점수에 맞춰 준비합니다."),
    ("입학·전학 준비", "국제학교 입학 영어·수학 평가와 한국에서 전학 온 학생의 적응기를 관리합니다."),
]
US_POINTS_TAIL = ["학부모에게 한국어로 주간 리포트 제공", "SAT 목표 점수별 단계 학습"]
SEA_POINTS_TAIL = ["학부모에게 한국어로 주간 리포트 제공", "한국 귀국·편입 일정을 고려한 학습 계획", "방학 중 한국 체류 시 대면 수업 상담 가능"]
STD = ["AP", "SAT", "내신"]

PAGES = [
    {
        "slug": "us-austin", "consult": "오스틴", "eyebrow": "Austin · Round Rock", "hub": "미국",
        "name": "텍사스 오스틴 (라운드록·리앤더)",
        "title": "오스틴·라운드록·리앤더 고등학교 AP·SAT 온라인 과외 | 텍사스",
        "h1": "텍사스 오스틴·라운드록<br />AP·SAT 온라인 과외",
        "desc": "라운드록 ISD 웨스트우드·라운드록, 리앤더 ISD 밴더그리프트·시더파크, 이인스 ISD 웨스트레이크 고등학교 학생을 위한 AP·SAT·내신 Zoom 1:1 과외.",
        "lead": "오스틴 북부 라운드록·리앤더 지역은 삼성 오스틴 공장과 테일러 신공장 영향으로 한국 주재원 가정이 늘고 있습니다. 학교별 AP 수업과 SAT 준비를 미국 중부 시간에 맞춰 관리합니다.",
        "groups": [
            ("라운드록 ISD", [
                ("Westwood High School", "웨스트우드 고등학교", STD),
                ("Round Rock High School", "라운드록 고등학교", STD),
            ]),
            ("리앤더 ISD·이인스 ISD", [
                ("Vandegrift High School", "밴더그리프트 고등학교 · 리앤더 ISD", STD),
                ("Cedar Park High School", "시더파크 고등학교 · 리앤더 ISD", STD),
                ("Westlake High School", "웨스트레이크 고등학교 · 이인스(Eanes) ISD", STD),
            ]),
        ],
        "tz": TZ_CENTRAL, "services": US_SERVICES,
        "points": ["학교별 AP 과목 진도와 5월 시험 일정 관리", "한국에서 막 이주한 주재원 자녀의 첫 학기 적응 코칭", "테일러·조지타운 등 오스틴 주변 지역 학생도 같은 방식으로 지원", "미국 중부 저녁 시간대 Zoom 수업"] + US_POINTS_TAIL,
        "faq": [("테일러(Taylor) 지역에 사는데 수업이 가능한가요?", "가능합니다. Zoom 수업이라 테일러·허토·조지타운 등 오스틴 주변 어느 지역이든 같은 방식으로 진행합니다."),
                ("텍사스 주 시험(STAAR)도 준비하나요?", "학교 수업과 함께 STAAR End-of-Course 시험 범위(Algebra I, English I·II 등)를 점검할 수 있습니다. 상담 시 학년을 알려주세요.")],
    },
    {
        "slug": "us-seattle", "consult": "시애틀 벨뷰", "eyebrow": "Seattle · Bellevue", "hub": "미국",
        "name": "시애틀 벨뷰·이사콰·레드먼드",
        "title": "벨뷰·이사콰·레드먼드 고등학교 AP·IB·SAT 온라인 과외 | 시애틀",
        "h1": "시애틀 벨뷰·이사콰·레드먼드<br />AP·IB·SAT 온라인 과외",
        "desc": "벨뷰 뉴포트·인터레이크·벨뷰·새머미시, 이사콰·스카이라인, 레드먼드·레이크워싱턴, 머서아일랜드 고등학교 학생 AP·IB·SAT Zoom 과외.",
        "lead": "시애틀 동쪽 벨뷰·이사콰·레드먼드는 IT 기업 주재원과 한인 가정이 많이 사는 학군입니다. 학교별 AP·IB 수업과 SAT 준비를 미국 서부 시간에 맞춰 관리합니다.",
        "groups": [
            ("벨뷰 교육구 (Bellevue SD)", [
                ("Newport High School", "뉴포트 고등학교", STD),
                ("Interlake High School", "인터레이크 고등학교 · IB 과정", ["IB", "AP", "SAT"]),
                ("Bellevue High School", "벨뷰 고등학교", STD),
                ("Sammamish High School", "새머미시 고등학교", STD),
            ]),
            ("이사콰·레이크워싱턴·머서아일랜드", [
                ("Issaquah High School", "이사콰 고등학교 · 이사콰 SD", STD),
                ("Skyline High School", "스카이라인 고등학교 · 이사콰 SD", STD),
                ("Redmond High School", "레드먼드 고등학교 · 레이크워싱턴 SD", STD),
                ("Lake Washington High School", "레이크워싱턴 고등학교 · 레이크워싱턴 SD", STD),
                ("Mercer Island High School", "머서아일랜드 고등학교", STD),
            ]),
        ],
        "tz": TZ_PACIFIC,
        "services": US_SERVICES[:1] + [("IB Diploma", "인터레이크 등 IB 과정 학생의 IB Math AA·AI, English, IA·EE·TOK 일정을 함께 관리합니다.")] + US_SERVICES[1:3],
        "points": ["학교별 AP·IB 과목 진도와 시험 일정 관리", "학업 경쟁이 치열한 학군의 시험 전 주간 점검", "린우드·에드먼즈 등 시애틀 북부 학생도 같은 방식으로 지원", "미국 서부 저녁 시간대 Zoom 수업"] + US_POINTS_TAIL,
        "faq": [("인터레이크 IB 과정 학생도 수업하나요?", "네. IB Math·English 수업과 IA·EE 마감 일정, 5월 IB 시험 대비를 함께 관리합니다."),
                ("린우드·에드먼즈나 페더럴웨이도 가능한가요?", "가능합니다. 시애틀 북부·남부 어느 지역이든 Zoom으로 같은 시간대에 수업합니다.")],
    },
    {
        "slug": "us-chicago", "consult": "시카고 북부", "eyebrow": "Chicago North Shore · Naperville", "hub": "미국",
        "name": "시카고 노스브룩·글렌뷰·네이퍼빌",
        "title": "노스브룩·글렌뷰·네이퍼빌 고등학교 AP·SAT 온라인 과외 | 시카고",
        "h1": "시카고 노스브룩·글렌뷰·네이퍼빌<br />AP·SAT 온라인 과외",
        "desc": "글렌브룩 노스·사우스, 뉴트리어, 스티븐슨, 네이퍼빌 노스·센트럴, 뉴쿠아밸리, 힌즈데일 센트럴, 버넌힐스 고등학교 학생 AP·SAT Zoom 과외.",
        "lead": "시카고 북부 노스브룩·글렌뷰와 서부 교외 네이퍼빌·힌즈데일은 한국 주재원과 한인 가정이 많이 사는 학군입니다. 학교별 AP 수업과 SAT 준비를 미국 중부 시간에 맞춰 관리합니다.",
        "groups": [
            ("노스브룩·글렌뷰·위네카·링컨셔 (북부)", [
                ("Glenbrook North High School", "글렌브룩 노스 고등학교 · 노스브룩", STD),
                ("Glenbrook South High School", "글렌브룩 사우스 고등학교 · 글렌뷰", STD),
                ("New Trier High School", "뉴트리어 고등학교 · 위네카", STD),
                ("Adlai E. Stevenson High School", "스티븐슨 고등학교 · 링컨셔", STD),
                ("Vernon Hills High School", "버넌힐스 고등학교", STD),
            ]),
            ("네이퍼빌·힌즈데일 (서부 교외)", [
                ("Naperville North High School", "네이퍼빌 노스 고등학교", STD),
                ("Naperville Central High School", "네이퍼빌 센트럴 고등학교", STD),
                ("Neuqua Valley High School", "뉴쿠아밸리 고등학교", STD),
                ("Hinsdale Central High School", "힌즈데일 센트럴 고등학교", STD),
            ]),
        ],
        "tz": TZ_CENTRAL, "services": US_SERVICES,
        "points": ["학교별 AP 과목 진도와 5월 시험 일정 관리", "일리노이 11학년 SAT(주 시험) 일정에 맞춘 준비", "스코키·나일스 등 시카고 북부 다른 지역 학생도 같은 방식으로 지원", "미국 중부 저녁 시간대 Zoom 수업"] + US_POINTS_TAIL,
        "faq": [("일리노이는 학교에서 SAT를 보나요?", "일리노이 공립고는 11학년 봄에 주 시험으로 SAT를 실시합니다. 학교 시험일에 맞춰 영역별 준비 일정을 세웁니다."),
                ("스코키·나일스 지역도 가능한가요?", "가능합니다. 나일스 노스·웨스트 등 시카고 북부 다른 학교 학생도 상담 가능합니다.")],
    },
    {
        "slug": "us-detroit", "consult": "디트로이트", "eyebrow": "Novi · Troy · Ann Arbor", "hub": "미국",
        "name": "미시간 노바이·트로이·앤아버",
        "title": "노바이·노스빌·트로이·앤아버 고등학교 AP·IB·SAT 온라인 과외 | 미시간",
        "h1": "미시간 노바이·트로이·앤아버<br />AP·IB·SAT 온라인 과외",
        "desc": "노바이·노스빌·트로이·트로이 애선스·블룸필드힐스 고등학교, 인터내셔널 아카데미(IB), 앤아버 파이오니어·휴런·스카이라인 고등학교 학생 AP·SAT Zoom 과외.",
        "lead": "디트로이트 교외 노바이·트로이와 앤아버는 자동차·부품 기업 주재원 가정이 많이 사는 지역입니다. 학교별 AP·IB 수업과 SAT 준비를 미국 동부 시간에 맞춰 관리합니다.",
        "groups": [
            ("노바이·노스빌·트로이·블룸필드힐스", [
                ("Novi High School", "노바이 고등학교", STD),
                ("Northville High School", "노스빌 고등학교", STD),
                ("Troy High School (Michigan)", "트로이 고등학교 · 미시간", STD),
                ("Troy Athens High School", "트로이 애선스 고등학교", STD),
                ("Bloomfield Hills High School", "블룸필드힐스 고등학교", STD),
                ("International Academy", "인터내셔널 아카데미 · IB 공립", ["IB", "선발형"]),
            ]),
            ("앤아버 (Ann Arbor Public Schools)", [
                ("Pioneer High School", "파이오니어 고등학교", STD),
                ("Huron High School", "휴런 고등학교", STD),
                ("Skyline High School (Ann Arbor)", "스카이라인 고등학교 · 앤아버", STD),
            ]),
        ],
        "tz": TZ_EASTERN,
        "services": US_SERVICES[:1] + [("IB Diploma", "인터내셔널 아카데미 학생의 IB Math AA·AI, English, IA·EE·TOK 일정을 함께 관리합니다.")] + US_SERVICES[1:3],
        "points": ["학교별 AP·IB 과목 진도와 시험 일정 관리", "미시간 11학년 SAT(주 시험) 일정에 맞춘 준비", "앤아버 등 디트로이트 외곽 학생도 같은 방식으로 지원", "미국 동부 저녁 시간대 Zoom 수업"] + US_POINTS_TAIL,
        "faq": [("캘리포니아 풀러턴 트로이 고등학교와 같은 학교인가요?", "아닙니다. 이 페이지의 Troy High School은 미시간주 트로이에 있는 학교입니다. 풀러턴 트로이 고등학교는 LA 풀러턴·토랜스 페이지에서 안내합니다."),
                ("미시간은 학교에서 SAT를 보나요?", "미시간 공립고는 11학년 봄에 주 시험(MME)의 일부로 SAT를 실시합니다. 학교 시험일에 맞춰 준비 일정을 세웁니다.")],
    },
    {
        "slug": "malaysia", "consult": "말레이시아", "eyebrow": "Kuala Lumpur · Johor · Penang", "hub": "동남아시아",
        "name": "말레이시아 국제학교",
        "title": "말레이시아 국제학교 IB·IGCSE·AP 과외 | 쿠알라룸푸르·조호바루·페낭",
        "h1": "말레이시아 국제학교<br />IB·IGCSE·AP 온라인 과외",
        "desc": "쿠알라룸푸르 ISKL·가든·알리스 스미스·몬키아라(MKIS)·넥서스, 조호바루 말보로·래플스 아메리칸, 페낭 달랏·업랜즈 학생을 위한 IB·IGCSE·AP Zoom 과외.",
        "lead": "말레이시아는 학비 대비 교육 환경이 좋아 주재원 가정과 조기유학 학생이 많이 찾는 곳입니다. 한국과 시차가 1시간뿐이라 평일 방과 후 수업이 편합니다. 학교 커리큘럼(IB·IGCSE·A-Level·AP)에 맞춰 수학·영어를 관리합니다.",
        "groups": [
            ("쿠알라룸푸르", [
                ("International School of Kuala Lumpur (ISKL)", "ISKL · 미국식", ["IB", "미국식"]),
                ("Garden International School", "가든 인터내셔널 스쿨 · 영국식", ["IGCSE", "A-Level"]),
                ("The Alice Smith School", "알리스 스미스 스쿨 · 영국식", ["IGCSE", "A-Level"]),
                ("Mont'Kiara International School (MKIS)", "몬키아라 인터내셔널 스쿨 · 몬키아라 한인 밀집", ["IB", "미국식"]),
                ("Nexus International School", "넥서스 인터내셔널 · 푸트라자야", ["IGCSE", "IB"]),
                ("Fairview International School", "페어뷰 인터내셔널 스쿨", ["IB"]),
            ]),
            ("조호바루·페낭", [
                ("Marlborough College Malaysia", "말보로 칼리지 말레이시아 · 조호, 보딩", ["영국식", "보딩"]),
                ("Raffles American School", "래플스 아메리칸 스쿨 · 조호", ["미국식", "AP"]),
                ("Dalat International School", "달랏 인터내셔널 · 페낭", ["미국식", "AP"]),
                ("Uplands International School", "업랜즈 · 페낭", ["IB"]),
            ]),
        ],
        "tz": TZ_PLUS8, "services": SEA_SERVICES,
        "points": ["한국과 1시간 시차로 평일 방과 후 수업", "학교별 커리큘럼(IB·IGCSE·AP) 맞춤 진도", "조기유학생의 영어 과제·에세이 관리"] + SEA_POINTS_TAIL,
        "faq": [("조기유학으로 혼자 지내는 학생도 관리해 주나요?", "네. 수업과 함께 과제 마감과 시험 일정을 주 단위로 점검하고, 한국에 계신 학부모께 한국어 리포트를 보내 드립니다."),
                ("조호바루에서 싱가포르로 통학하는 학생도 가능한가요?", "가능합니다. 다니는 학교의 커리큘럼에 맞춰 수업하며, 싱가포르 국제학교 안내 페이지도 참고해 주세요.")],
    },
    {
        "slug": "thailand", "consult": "태국", "eyebrow": "Bangkok", "hub": "동남아시아",
        "name": "태국 방콕 국제학교",
        "title": "방콕 국제학교 IB·IGCSE·A-Level 과외 | ISB·NIST·방콕 파타나",
        "h1": "태국 방콕 국제학교<br />IB·IGCSE·A-Level 온라인 과외",
        "desc": "방콕 ISB·NIST·방콕 파타나·해로·슈루즈베리·KIS·루암루디·브롬스그로브·웰링턴·콘코디안 학생을 위한 IB·IGCSE·A-Level·AP Zoom 1:1 과외.",
        "lead": "방콕은 영국식·미국식·IB 국제학교가 고루 있어 학교 선택지가 넓은 곳입니다. 한국과 시차가 2시간이라 평일 방과 후 수업이 편합니다. 학교 커리큘럼에 맞춰 수학·영어를 관리합니다.",
        "groups": [("방콕 주요 국제학교", [
            ("International School Bangkok (ISB)", "ISB · 논타부리, 미국식", ["IB", "미국식"]),
            ("NIST International School", "NIST", ["IB"]),
            ("Bangkok Patana School", "방콕 파타나 · 영국식", ["IGCSE", "IB"]),
            ("Harrow International School Bangkok", "해로 인터내셔널 방콕 · 영국식", ["IGCSE", "A-Level"]),
            ("Shrewsbury International School Bangkok", "슈루즈베리 방콕 · 영국식", ["IGCSE", "A-Level"]),
            ("KIS International School", "KIS 인터내셔널", ["IB"]),
            ("Ruamrudee International School (RIS)", "루암루디 · 미국식", ["IB", "미국식"]),
            ("Bromsgrove International School Thailand", "브롬스그로브 · 영국식", ["영국식"]),
            ("Wellington College International School Bangkok", "웰링턴 칼리지 방콕 · 영국식", ["영국식"]),
            ("Concordian International School", "콘코디안", ["IB"]),
        ])],
        "tz": TZ_PLUS7, "services": SEA_SERVICES,
        "points": ["한국과 2시간 시차로 평일 방과 후 수업", "학교별 커리큘럼(IB·IGCSE·A-Level) 맞춤 진도", "치앙마이·푸켓 지역 학생도 같은 방식으로 지원"] + SEA_POINTS_TAIL,
        "faq": [("치앙마이나 푸켓에 사는데 수업이 가능한가요?", "가능합니다. Zoom 수업이라 태국 어느 지역이든 같은 시간대로 진행합니다."),
                ("영국식 학교와 IB 학교 수업이 다른가요?", "네. IGCSE·A-Level은 시험 보드별 기출 중심으로, IB는 내부평가(IA)와 최종 시험을 함께 관리하도록 수업을 구성합니다.")],
    },
    {
        "slug": "philippines", "consult": "필리핀", "eyebrow": "Manila · Cebu · Clark", "hub": "동남아시아",
        "name": "필리핀 마닐라 국제학교",
        "title": "마닐라 국제학교 IB·IGCSE·AP 과외 | ISM·브리티시 스쿨·브렌트",
        "h1": "필리핀 마닐라·세부 국제학교<br />IB·IGCSE·AP 온라인 과외",
        "desc": "마닐라 ISM·브리티시 스쿨 마닐라·브렌트·리들리·페이스 아카데미, 세부 인터내셔널 스쿨, 클락 세인트 폴 아메리칸 스쿨 학생 IB·IGCSE·AP·SAT Zoom 과외.",
        "lead": "필리핀은 주재원 가정과 조기유학·어학연수 학생이 함께 많은 곳입니다. 한국과 시차가 1시간뿐이라 평일 방과 후 수업이 편합니다. 학교 커리큘럼에 맞춰 수학·영어를 관리합니다.",
        "groups": [
            ("마닐라 (BGC·마카티·알라방)", [
                ("International School Manila (ISM)", "인터내셔널 스쿨 마닐라 · BGC", ["IB"]),
                ("British School Manila", "브리티시 스쿨 마닐라 · BGC", ["IGCSE", "IB"]),
                ("Brent International School Manila", "브렌트 인터내셔널 마닐라 · 라구나", ["IB", "미국식"]),
                ("Reedley International School", "리들리 인터내셔널 스쿨 · 미국식", ["미국식"]),
                ("Faith Academy", "페이스 아카데미 · 미국식, 기독교", ["미국식", "AP"]),
                ("Singapore School Manila", "싱가포르 스쿨 마닐라 · 싱가포르식", ["싱가포르식"]),
            ]),
            ("세부·클락·수빅", [
                ("Cebu International School", "세부 인터내셔널 스쿨", ["IB"]),
                ("St. Paul American School Clark", "세인트 폴 아메리칸 스쿨 · 클락", ["미국식"]),
                ("Brent International School Subic", "브렌트 인터내셔널 수빅", ["미국식"]),
            ]),
        ],
        "tz": TZ_PLUS8, "services": SEA_SERVICES,
        "points": ["한국과 1시간 시차로 평일 방과 후 수업", "학교별 커리큘럼(IB·IGCSE·AP) 맞춤 진도", "조기유학생의 영어 과제·에세이 관리"] + SEA_POINTS_TAIL,
        "faq": [("세부나 클락에 사는데 수업이 가능한가요?", "가능합니다. Zoom 수업이라 필리핀 어느 지역이든 같은 시간대로 진행합니다."),
                ("어학연수 중인데 국제학교 진학 준비도 하나요?", "네. 국제학교 입학 영어·수학 평가와 첫 학기 수업 적응을 함께 준비합니다.")],
    },
    {
        "slug": "indonesia", "consult": "인도네시아", "eyebrow": "Jakarta", "hub": "동남아시아",
        "name": "인도네시아 자카르타 국제학교",
        "title": "자카르타 국제학교 IB·IGCSE·AP 과외 | JIS·브리티시 스쿨 자카르타",
        "h1": "인도네시아 자카르타 국제학교<br />IB·IGCSE·AP 온라인 과외",
        "desc": "자카르타 JIS·브리티시 스쿨 자카르타(BSJ)·AIS 인도네시아·SIS·비누스 심프룩·멘타리 학생을 위한 IB·IGCSE·AP·SAT Zoom 1:1 과외.",
        "lead": "자카르타는 오래전부터 한국 기업 주재원이 많은 도시입니다. 한국과 시차가 2시간이라 평일 방과 후 수업이 편합니다. 국제학교 커리큘럼(IB·IGCSE·AP)에 맞춰 수학·영어를 관리합니다.",
        "groups": [("자카르타 주요 국제학교", [
            ("Jakarta Intercultural School (JIS)", "자카르타 인터컬처럴 스쿨 · 미국식", ["IB", "AP", "미국식"]),
            ("British School Jakarta (BSJ)", "브리티시 스쿨 자카르타 · 빈타로", ["IGCSE", "IB"]),
            ("Australian Independent School Indonesia", "AIS 인도네시아 · 호주식", ["호주식"]),
            ("Singapore Intercultural School (SIS)", "싱가포르 인터컬처럴 스쿨", ["싱가포르식"]),
            ("Binus School Simprug", "비누스 스쿨 심프룩", ["IB"]),
            ("Mentari Intercultural School", "멘타리 인터컬처럴 스쿨", ["IB"]),
        ])],
        "tz": TZ_PLUS7, "services": SEA_SERVICES,
        "points": ["한국과 2시간 시차로 평일 방과 후 수업", "학교별 커리큘럼(IB·IGCSE·AP) 맞춤 진도", "발리 등 자카르타 외 지역 학생도 같은 방식으로 지원"] + SEA_POINTS_TAIL,
        "faq": [("자카르타한국국제학교(JIKS) 학생도 가능한가요?", "가능합니다. 다만 한국 교육과정 학교라 수업 내용은 영어 실력 향상, 국제학교 전학이나 SAT·TOEFL 준비 위주로 상담합니다."),
                ("자카르타 교통 체증 때문에 수업 시간이 걱정돼요.", "통학 시간을 고려해 귀가 후 시간으로 수업을 정하고, 일정이 바뀌면 같은 주 안에서 보강을 조율합니다.")],
    },
    # --- 3rd batch (2026-10-28) ---
    {
        "slug": "us-nyc", "consult": "뉴욕 퀸스", "eyebrow": "Queens · NYC Specialized High Schools", "hub": "미국",
        "name": "뉴욕 퀸스·뉴욕시 특목고",
        "title": "뉴욕 퀸스·스타이브센트·브롱스 과학고 AP·SAT 온라인 과외 | 뉴욕시",
        "h1": "뉴욕 퀸스·뉴욕시 특목고<br />AP·SAT 온라인 과외",
        "desc": "베이사이드·프랜시스 루이스·카도조·타운센드 해리스, 스타이브센트·브롱스 과학고·브루클린 테크, 스카스데일·에지몬트 고등학교 학생 AP·SAT·Regents Zoom 과외.",
        "lead": "퀸스 베이사이드·플러싱·리틀넥은 뉴욕시에서 한인 가정이 가장 많이 사는 지역입니다. 동네 학교와 시험으로 들어가는 뉴욕시 특목고, 웨스트체스터 학군의 AP·Regents·SAT를 미국 동부 시간에 맞춰 관리합니다.",
        "groups": [
            ("퀸스 (베이사이드·플러싱·리틀넥)", [
                ("Bayside High School", "베이사이드 고등학교", STD),
                ("Francis Lewis High School", "프랜시스 루이스 고등학교", STD),
                ("Benjamin N. Cardozo High School", "벤저민 카도조 고등학교", STD),
                ("Townsend Harris High School", "타운센드 해리스 고등학교 · 선발형", ["선발형", "AP", "SAT"]),
            ]),
            ("뉴욕시 특목고 (SHSAT 선발)", [
                ("Stuyvesant High School", "스타이브센트 고등학교 · 맨해튼", ["선발형", "AP", "STEM"]),
                ("The Bronx High School of Science", "브롱스 과학고", ["선발형", "AP", "STEM"]),
                ("Brooklyn Technical High School", "브루클린 테크니컬 고등학교", ["선발형", "AP", "STEM"]),
            ]),
            ("웨스트체스터", [
                ("Scarsdale High School", "스카스데일 고등학교", STD),
                ("Edgemont High School", "에지몬트 고등학교", STD),
            ]),
        ],
        "tz": TZ_EASTERN,
        "services": US_SERVICES[:3] + [("Regents 시험 대비", "뉴욕주 Regents 수학(Algebra I·Geometry·Algebra II) 시험을 학교 진도와 함께 준비합니다.")],
        "points": ["특목고 재학생의 빠른 수학·과학 진도 대응", "학교별 AP 과목 진도와 5월 시험 일정 관리", "뉴욕주 Regents 수학 시험 대비", "미국 동부 저녁 시간대 Zoom 수업"] + US_POINTS_TAIL,
        "faq": [("SHSAT(특목고 입학시험)도 준비하나요?", "특목고 재학생의 수학·영어 수업과 AP·SAT 준비를 중심으로 지원합니다. SHSAT 준비가 필요하면 상담 시 학년과 시험 일정을 알려주세요."),
                ("롱아일랜드 그레이트넥 지역은 어디서 보나요?", "그레이트넥·맨해셋·제리코 등 나소카운티 학교는 '뉴욕 롱아일랜드 그레이트넥' 페이지에서 안내합니다.")],
    },
    {
        "slug": "us-boston", "consult": "보스턴", "eyebrow": "Boston · Massachusetts", "hub": "미국",
        "name": "보스턴 근교·매사추세츠 보딩스쿨",
        "title": "보스턴 렉싱턴·뉴턴 고등학교와 매사추세츠 보딩스쿨 AP·SAT 온라인 과외",
        "h1": "보스턴 근교·매사추세츠 보딩스쿨<br />AP·SAT 온라인 과외",
        "desc": "렉싱턴·뉴턴 노스·사우스·브루클라인·액턴-박스버러·웰즐리 고등학교와 앤도버·디어필드·밀턴·그로턴·미들섹스 보딩스쿨 학생을 위한 AP·SAT Zoom 과외.",
        "lead": "보스턴 근교 렉싱턴·뉴턴은 대학·병원·연구소에서 일하는 한인 가정이 많이 사는 학군이고, 매사추세츠에는 한국 유학생이 많이 다니는 보딩스쿨이 모여 있습니다. 학교 수업과 SAT를 미국 동부 시간에 맞춰 관리합니다.",
        "groups": [
            ("보스턴 근교 공립", [
                ("Lexington High School", "렉싱턴 고등학교", STD),
                ("Newton North High School", "뉴턴 노스 고등학교", STD),
                ("Newton South High School", "뉴턴 사우스 고등학교", STD),
                ("Brookline High School", "브루클라인 고등학교", STD),
                ("Acton-Boxborough Regional High School", "액턴-박스버러 리저널 고등학교", STD),
                ("Wellesley High School", "웰즐리 고등학교", STD),
            ]),
            ("매사추세츠 보딩스쿨", [
                ("Phillips Academy Andover", "필립스 아카데미 앤도버", ["보딩", "SAT"]),
                ("Deerfield Academy", "디어필드 아카데미", ["보딩", "SAT"]),
                ("Milton Academy", "밀턴 아카데미", ["보딩", "SAT"]),
                ("Groton School", "그로턴 스쿨", ["보딩", "SAT"]),
                ("Middlesex School", "미들섹스 스쿨", ["보딩", "SAT"]),
            ]),
        ],
        "tz": TZ_EASTERN,
        "services": US_SERVICES[:3] + [("보딩스쿨 학업 관리", "기숙사 일과(스터디 홀) 밖의 시간에 맞춰 수학 진도, 영어 에세이와 과제 마감을 주 단위로 점검합니다.")],
        "points": ["보딩스쿨 기숙사 일정에 맞춘 수업 시간 배정", "학교별 고급 수학·과학 과목 진도 대응", "영어 에세이·리서치 과제 코칭", "미국 동부 저녁·주말 시간대 Zoom 수업"] + US_POINTS_TAIL,
        "faq": [("보딩스쿨은 AP 과목이 없다던데 어떻게 수업하나요?", "일부 보딩스쿨은 AP 대신 자체 고급 과목을 운영합니다. 학교 과목명과 교재를 확인해 그 수업 진도에 맞춰 지도하고, 필요하면 AP 시험이나 SAT를 따로 준비합니다."),
                ("기숙사 생활 중에도 수업 시간을 낼 수 있나요?", "스터디 홀과 소등 시간을 피해 주말이나 저녁 자유 시간으로 정합니다. 학교 일정표를 보고 함께 조율합니다.")],
    },
    {
        "slug": "us-houston", "consult": "휴스턴", "eyebrow": "Houston · Katy · Sugar Land", "hub": "미국",
        "name": "텍사스 휴스턴 (케이티·슈거랜드)",
        "title": "휴스턴 케이티·슈거랜드 고등학교 AP·SAT 온라인 과외 | 텍사스",
        "h1": "텍사스 휴스턴 케이티·슈거랜드<br />AP·SAT 온라인 과외",
        "desc": "케이티 ISD 세븐레이크스·톰킨스·싱코랜치, 포트벤드 ISD 클레멘츠·덜레스, 스프링브랜치 ISD 메모리얼 고등학교 학생을 위한 AP·SAT·내신 Zoom 1:1 과외.",
        "lead": "휴스턴 서쪽 케이티와 남서쪽 슈거랜드는 에너지·석유화학 기업 주재원 가정이 많이 사는 지역입니다. 학교별 AP 수업과 SAT 준비를 미국 중부 시간에 맞춰 관리합니다.",
        "groups": [
            ("케이티 ISD", [
                ("Seven Lakes High School", "세븐레이크스 고등학교", STD),
                ("Tompkins High School", "톰킨스 고등학교", STD),
                ("Cinco Ranch High School", "싱코랜치 고등학교", STD),
            ]),
            ("포트벤드 ISD·스프링브랜치 ISD", [
                ("Clements High School", "클레멘츠 고등학교 · 슈거랜드", STD),
                ("Dulles High School", "덜레스 고등학교 · 슈거랜드", STD),
                ("Memorial High School", "메모리얼 고등학교 · 스프링브랜치 ISD", STD),
            ]),
        ],
        "tz": TZ_CENTRAL, "services": US_SERVICES,
        "points": ["학교별 AP 과목 진도와 5월 시험 일정 관리", "한국에서 막 이주한 주재원 자녀의 첫 학기 적응 코칭", "텍사스 STAAR 시험 범위 점검", "미국 중부 저녁 시간대 Zoom 수업"] + US_POINTS_TAIL,
        "faq": [("텍사스 주 시험(STAAR)도 준비하나요?", "학교 수업과 함께 STAAR End-of-Course 시험 범위(Algebra I, English I·II 등)를 점검할 수 있습니다. 상담 시 학년을 알려주세요."),
                ("댈러스·오스틴 지역도 따로 안내하나요?", "네. 댈러스(플레이노·프리스코)와 오스틴(라운드록·리앤더)은 각각 별도 페이지에서 안내합니다.")],
    },
    {
        "slug": "us-central-nj", "consult": "중부 뉴저지", "eyebrow": "Edison · Princeton · West Windsor", "hub": "미국",
        "name": "중부 뉴저지 (에디슨·프린스턴·웨스트윈저)",
        "title": "에디슨·프린스턴·웨스트윈저 고등학교 AP·SAT 온라인 과외 | 뉴저지",
        "h1": "중부 뉴저지 에디슨·프린스턴<br />AP·SAT 온라인 과외",
        "desc": "J.P. 스티븐스(에디슨), 프린스턴, 웨스트윈저-플레인스보로 노스·사우스, 체리힐 이스트 고등학교 학생을 위한 AP·SAT·내신 Zoom 1:1 과외.",
        "lead": "에디슨·프린스턴·웨스트윈저는 제약·연구소·대학에서 일하는 한인 가정이 많이 사는 중부 뉴저지 학군입니다. 학업 경쟁이 치열한 학교의 AP 수학·과학과 SAT를 미국 동부 시간에 맞춰 관리합니다.",
        "groups": [
            ("에디슨·프린스턴·웨스트윈저", [
                ("J.P. Stevens High School", "J.P. 스티븐스 고등학교 · 에디슨", STD),
                ("Princeton High School", "프린스턴 고등학교", STD),
                ("West Windsor-Plainsboro HS North", "웨스트윈저-플레인스보로 노스", STD),
                ("West Windsor-Plainsboro HS South", "웨스트윈저-플레인스보로 사우스", STD),
            ]),
            ("체리힐 (필라델피아 근교)", [
                ("Cherry Hill High School East", "체리힐 이스트 고등학교", STD),
            ]),
        ],
        "tz": TZ_EASTERN, "services": US_SERVICES,
        "points": ["AP Calculus BC·Physics C 등 상위 과목 집중 수업", "학교별 AP 과목 진도와 5월 시험 일정 관리", "필라델피아 근교(로어메리언·래드너) 학생도 같은 방식으로 지원", "미국 동부 저녁 시간대 Zoom 수업"] + US_POINTS_TAIL,
        "faq": [("버겐카운티(포트리·테너플라이)는 어디서 보나요?", "북부 뉴저지 버겐카운티 학교는 '뉴저지 버겐카운티' 페이지에서 안내합니다."),
                ("필라델피아 근교도 가능한가요?", "가능합니다. 로어메리언·코네스토가·래드너 등 펜실베이니아 쪽 학교 학생도 상담 가능합니다.")],
    },
    {
        "slug": "shanghai", "consult": "상하이", "eyebrow": "Shanghai", "hub": "동아시아",
        "name": "중국 상하이 국제학교",
        "title": "상하이 국제학교 IB·IGCSE·AP 과외 | SAS·덜위치·웰링턴·YCIS",
        "h1": "중국 상하이 국제학교<br />IB·IGCSE·AP 온라인 과외",
        "desc": "상하이 아메리칸 스쿨(SAS), 덜위치 칼리지 상하이, 웰링턴 칼리지 상하이, YCIS, 컨커디아, WISS, 브리티시 인터내셔널 스쿨 상하이 학생 IB·IGCSE·AP·SAT Zoom 과외.",
        "lead": "상하이는 중국에서 한국 주재원 가정이 가장 많은 도시 중 하나로, 민항구 홍췐루 일대에 한인 생활권이 있습니다. 한국과 시차가 1시간이라 평일 방과 후 수업이 편합니다. 학교 커리큘럼(IB·IGCSE·AP)에 맞춰 수학·영어를 관리합니다.",
        "groups": [("상하이 주요 국제학교", [
            ("Shanghai American School (SAS)", "상하이 아메리칸 스쿨 · 푸시·푸둥", ["AP", "IB", "미국식"]),
            ("Dulwich College Shanghai Pudong", "덜위치 칼리지 상하이 푸둥 · 영국식", ["IGCSE", "IB"]),
            ("Wellington College International Shanghai", "웰링턴 칼리지 상하이 · 영국식", ["IGCSE", "IB"]),
            ("Yew Chung International School of Shanghai (YCIS)", "YCIS 상하이", ["IGCSE", "IB"]),
            ("Concordia International School Shanghai", "컨커디아 상하이 · 미국식", ["AP", "미국식"]),
            ("Western International School of Shanghai (WISS)", "WISS", ["IB"]),
            ("British International School Shanghai", "브리티시 인터내셔널 스쿨 상하이", ["IGCSE", "IB"]),
        ])],
        "tz": TZ_PLUS8, "services": SEA_SERVICES,
        "points": ["한국과 1시간 시차로 평일 방과 후 수업", "학교별 커리큘럼(IB·IGCSE·AP) 맞춤 진도", "국제학교 입학·전학 영어·수학 평가 준비"] + SEA_POINTS_TAIL,
        "faq": [("상하이한국학교 학생도 가능한가요?", "가능합니다. 다만 한국 교육과정 학교라 수업 내용은 영어 실력 향상, 국제학교 전학이나 SAT·TOEFL 준비 위주로 상담합니다."),
                ("중국에서 Zoom 수업이 원활한가요?", "학생 쪽 인터넷 환경을 첫 수업 전에 함께 점검하고, 연결이 불안정하면 다른 화상 도구로 바꿔 진행합니다.")],
    },
    {
        "slug": "beijing", "consult": "베이징", "eyebrow": "Beijing", "hub": "동아시아",
        "name": "중국 베이징 국제학교",
        "title": "베이징 국제학교 IB·IGCSE·A-Level 과외 | ISB·WAB·덜위치",
        "h1": "중국 베이징 국제학교<br />IB·IGCSE·A-Level 온라인 과외",
        "desc": "베이징 ISB, WAB(웨스턴 아카데미), 덜위치 칼리지 베이징, BISS, 해로 베이징, YCIS 베이징, BCIS 학생을 위한 IB·IGCSE·A-Level·SAT Zoom 1:1 과외.",
        "lead": "베이징은 왕징 일대를 중심으로 한인 생활권이 형성된 도시입니다. 한국과 시차가 1시간이라 평일 방과 후 수업이 편합니다. 국제학교 커리큘럼(IB·IGCSE·A-Level)에 맞춰 수학·영어를 관리합니다.",
        "groups": [("베이징 주요 국제학교", [
            ("International School of Beijing (ISB)", "ISB · 순이, 미국식", ["IB", "미국식"]),
            ("Western Academy of Beijing (WAB)", "웨스턴 아카데미 오브 베이징", ["IB"]),
            ("Dulwich College Beijing", "덜위치 칼리지 베이징 · 영국식", ["IGCSE", "IB"]),
            ("Beijing BISS International School", "BISS", ["IB"]),
            ("Harrow International School Beijing", "해로 베이징 · 영국식", ["IGCSE", "A-Level"]),
            ("Yew Chung International School of Beijing", "YCIS 베이징", ["IGCSE", "IB"]),
            ("Beijing City International School (BCIS)", "BCIS", ["IB"]),
        ])],
        "tz": TZ_PLUS8, "services": SEA_SERVICES,
        "points": ["한국과 1시간 시차로 평일 방과 후 수업", "학교별 커리큘럼(IB·IGCSE·A-Level) 맞춤 진도", "국제학교 입학·전학 영어·수학 평가 준비"] + SEA_POINTS_TAIL,
        "faq": [("북경한국국제학교 학생도 가능한가요?", "가능합니다. 다만 한국 교육과정 학교라 수업 내용은 영어 실력 향상, 국제학교 전학이나 SAT·TOEFL 준비 위주로 상담합니다."),
                ("중국에서 Zoom 수업이 원활한가요?", "학생 쪽 인터넷 환경을 첫 수업 전에 함께 점검하고, 연결이 불안정하면 다른 화상 도구로 바꿔 진행합니다.")],
    },
    {
        "slug": "hong-kong", "consult": "홍콩", "eyebrow": "Hong Kong", "hub": "동아시아",
        "name": "홍콩 국제학교",
        "title": "홍콩 국제학교 IB·IGCSE·AP 과외 | HKIS·CDNIS·ESF·해로 홍콩",
        "h1": "홍콩 국제학교<br />IB·IGCSE·AP 온라인 과외",
        "desc": "홍콩 HKIS, 캐나디안 인터내셔널 스쿨(CDNIS), GSIS, ESF 아일랜드 스쿨·KGV, 해로 홍콩, 차이니즈 인터내셔널 스쿨, 홍콩한국국제학교 학생 IB·IGCSE·AP Zoom 과외.",
        "lead": "홍콩은 금융·무역 주재원 가정이 많고 영국식·미국식·IB 학교가 고루 있는 곳입니다. 한국과 시차가 1시간이라 평일 방과 후 수업이 편합니다. 학교 커리큘럼에 맞춰 수학·영어를 관리합니다.",
        "groups": [("홍콩 주요 국제학교", [
            ("Hong Kong International School (HKIS)", "HKIS · 미국식", ["AP", "미국식"]),
            ("Canadian International School of Hong Kong (CDNIS)", "캐나디안 인터내셔널 스쿨", ["IB"]),
            ("German Swiss International School (GSIS)", "GSIS · 영어·독일어 과정", ["IGCSE", "IB"]),
            ("Island School (ESF)", "아일랜드 스쿨 · ESF", ["IB"]),
            ("King George V School (ESF)", "킹 조지 5세 스쿨 · ESF", ["IGCSE", "IB"]),
            ("Harrow International School Hong Kong", "해로 홍콩 · 영국식", ["IGCSE", "A-Level"]),
            ("Chinese International School", "차이니즈 인터내셔널 스쿨", ["IB"]),
            ("Korean International School Hong Kong", "홍콩한국국제학교 · 한국·영어 과정", ["한국·영어 과정"]),
        ])],
        "tz": TZ_PLUS8, "services": SEA_SERVICES,
        "points": ["한국과 1시간 시차로 평일 방과 후 수업", "학교별 커리큘럼(IB·IGCSE·A-Level·AP) 맞춤 진도", "ESF 등 영국계 학교의 IGCSE 시험 보드별 대비"] + SEA_POINTS_TAIL,
        "faq": [("홍콩한국국제학교 학생도 가능한가요?", "가능합니다. 다니는 과정(한국 과정·영어 과정)에 맞춰 영어·수학 수업 내용을 정합니다."),
                ("홍콩은 학교마다 커리큘럼이 다른데 모두 가능한가요?", "네. IB, IGCSE·A-Level, AP 과정별로 학교 진도표와 과제를 확인해 수업을 구성합니다.")],
    },
    {
        "slug": "tokyo", "consult": "도쿄", "eyebrow": "Tokyo", "hub": "동아시아",
        "name": "일본 도쿄 국제학교",
        "title": "도쿄 국제학교 IB·AP·IGCSE 과외 | ASIJ·BST·세이센·세인트메리즈",
        "h1": "일본 도쿄 국제학교<br />IB·AP·IGCSE 온라인 과외",
        "desc": "도쿄 아메리칸 스쿨 인 재팬(ASIJ), 브리티시 스쿨 인 도쿄(BST), 세이센, 세인트 메리즈, 니시마치, K. 인터내셔널 스쿨 학생을 위한 IB·AP·IGCSE·SAT Zoom 1:1 과외.",
        "lead": "도쿄는 한국과 시차가 없어 수업 시간을 잡기 가장 쉬운 해외 지역입니다. 주재원 가정이 많이 보내는 미국식·영국식·IB 국제학교의 커리큘럼에 맞춰 수학·영어를 관리합니다.",
        "groups": [("도쿄 주요 국제학교", [
            ("The American School in Japan (ASIJ)", "아메리칸 스쿨 인 재팬 · 미국식", ["AP", "미국식"]),
            ("The British School in Tokyo (BST)", "브리티시 스쿨 인 도쿄 · 영국식", ["IGCSE", "A-Level"]),
            ("Seisen International School", "세이센 인터내셔널 스쿨 · 여학교", ["IB"]),
            ("St. Mary's International School", "세인트 메리즈 인터내셔널 스쿨 · 남학교", ["IB"]),
            ("Nishimachi International School", "니시마치 인터내셔널 스쿨 · 유치~9학년", ["초·중등"]),
            ("K. International School Tokyo", "K. 인터내셔널 스쿨 도쿄", ["IB"]),
        ])],
        "tz": ("한국과 시차 없음", "일본 오후 4~9시가 한국 시간과 같습니다. 평일 방과 후 바로 수업할 수 있습니다."),
        "services": SEA_SERVICES,
        "points": ["한국과 시차가 없어 평일 방과 후 바로 수업", "학교별 커리큘럼(IB·AP·IGCSE) 맞춤 진도", "요코하마·오사카 등 다른 지역 학생도 같은 방식으로 지원"] + SEA_POINTS_TAIL,
        "faq": [("오사카나 요코하마도 가능한가요?", "가능합니다. Zoom 수업이라 일본 어느 지역이든 한국과 같은 시간대로 진행합니다."),
                ("도쿄한국학교 학생도 가능한가요?", "가능합니다. 다니는 과정에 맞춰 영어 실력 향상, 국제학교 전학이나 SAT·TOEFL 준비 위주로 상담합니다.")],
    },
]

INDEX_TAGS = [("태국", "thailand"), ("방콕", "thailand"), ("말레이시아", "malaysia"), ("쿠알라룸푸르", "malaysia"),
              ("필리핀", "philippines"), ("마닐라", "philippines"), ("인도네시아", "indonesia"),
              ("시애틀", "us-seattle"), ("시카고", "us-chicago"),
              ("뉴욕", "us-nyc"), ("보스턴", "us-boston"), ("매사추세츠주", "us-boston"),
              ("상하이", "shanghai"), ("베이징", "beijing"), ("홍콩", "hong-kong"), ("일본", "tokyo"), ("도쿄", "tokyo")]
HUB_SECTION_ORDER = ["미국", "영국", "동남아시아", "동아시아"]
INDEX_SUMMARY = ("어바인 · 실리콘밸리 · 뉴저지 · 롱아일랜드 · 워싱턴DC 근교 · 댈러스 · 애틀랜타 · 런던·서리 · 싱가포르 · 베트남 · "
                 "오스틴 · 시애틀 · 시카고 · 미시간 · 말레이시아 · 태국 · 필리핀 · 인도네시아 · "
                 "뉴욕 퀸스 · 보스턴 · 휴스턴 · 중부 뉴저지 · 상하이 · 베이징 · 홍콩 · 도쿄")

HUB_TZ = [
    ("미국 서부 (LA·실리콘밸리·시애틀)", "−16시간", "현지 저녁 7~10시 = 한국 다음 날 오전 11시~오후 2시"),
    ("미국 중부 (댈러스·오스틴·시카고)", "−14시간", "현지 저녁 7~10시 = 한국 다음 날 오전 9시~정오"),
    ("미국 동부 (뉴욕·뉴저지·DC·애틀랜타·미시간)", "−13시간", "현지 저녁 7~10시 = 한국 다음 날 오전 8~11시"),
    ("영국 (런던·서리)", "−8시간", "현지 주말 오전 9시~정오 = 한국 오후 5~8시"),
    ("일본 (도쿄)", "시차 없음", "현지 오후 4~9시 = 한국 오후 4~9시"),
    ("중국·홍콩·싱가포르·말레이시아·필리핀", "−1시간", "현지 오후 4~9시 = 한국 오후 5~10시"),
    ("베트남·태국·인도네시아", "−2시간", "현지 오후 4~8시 = 한국 오후 6~10시"),
]


def esc(s):
    return html.escape(s, quote=True)


def consult_url(region):
    return "consult.html?region=" + quote(region)


def head(title, desc, slug, ld):
    url = BASE + slug + ".html"
    return f"""<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{esc(title)} | IB아이비</title>
    <meta name="description" content="{esc(desc)}" />
    <link rel="canonical" href="{url}" />
    <meta property="og:type" content="website" />
    <meta property="og:locale" content="ko_KR" />
    <meta property="og:site_name" content="IB아이비" />
    <meta property="og:title" content="{esc(title)}" />
    <meta property="og:description" content="{esc(desc)}" />
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
      <nav class="top-nav"><a href="igcse-tutoring.html">IGCSE</a><a href="ib-tutoring.html">IB</a><a href="ap-tutoring.html">AP</a><a href="sat-tutoring.html">SAT</a><a href="overseas.html">해외 지역</a><a class="nav-cta" href="consult.html">상담 신청</a></nav>
    </header>
"""


def breadcrumb_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}


def render_page(p):
    faq_all = p["faq"] + [("수업은 어떻게 진행되나요?", "Zoom 1:1 화상 수업으로 진행합니다. 첫 상담에서 학교·학년·수강 과목과 최근 성적을 확인하고 주간 수업 계획을 안내합니다.")]
    ld = {"@context": "https://schema.org", "@graph": [
        breadcrumb_ld([("홈", ""), ("해외 지역별 과외", "overseas.html"), (p["name"], p["slug"] + ".html")]),
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_all]},
    ]}
    cu = consult_url(p["consult"])
    out = [head(p["title"], p["desc"], p["slug"], ld)]
    out.append(f"""    <main class="page-shell">
      <div class="breadcrumbs" aria-label="breadcrumb"><a href="index.html">홈</a><span>›</span><a href="overseas.html">해외 지역별 과외</a><span>›</span><span>{esc(p['name'])}</span></div>
      <section class="page-hero reveal">
        <p class="eyebrow">{esc(p['eyebrow'])}</p>
        <h1>{p['h1']}</h1>
        <p>{esc(p['lead'])}</p>
        <div class="hero-actions"><a class="btn btn-primary" href="{cu}">무료 상담 신청</a><a class="btn btn-ghost" href="overseas.html">다른 해외 지역 보기</a></div>
      </section>
      <section class="detail-layout reveal">
        <div>
""")
    for gi, (gname, schools) in enumerate(p["groups"]):
        out.append(f"""          <div class="section-title-wrap">{'<p class="eyebrow">Schools</p>' if gi == 0 else ''}<h2>{esc(gname)}</h2></div>
          <div class="city-grid">
""")
        for en, ko, tags in schools:
            meta = "".join(f"<span>{esc(t)}</span>" for t in tags)
            out.append(f"""            <article class="city-card"><strong>{esc(en)}</strong><small>{esc(ko)}</small><div class="city-meta">{meta}</div></article>
""")
        out.append("          </div>\n")
    tz_short, tz_long = p["tz"]
    out.append(f"""          <p class="section-lead">{esc(NOTE)}</p>
        </div>
        <aside>
          <div class="stat-box"><h3>시차</h3><strong>{esc(tz_short.split(' (')[0])}</strong><p>{esc(tz_long)}</p></div>
          <div class="stat-box"><h3>수업 방식</h3><strong>Zoom 1:1</strong><p>{esc(tz_short)}. 거주 지역 시간에 맞춰 수업 시간을 정합니다.</p></div>
          <div class="stat-box"><h3>지원 과목</h3><strong>수학·영어</strong><p>학교 내신, 과제, 공인 시험 대비까지 지원합니다.</p></div>
        </aside>
      </section>
      <section class="reveal">
        <div class="section-title-wrap"><p class="eyebrow">Programs</p><h2>{esc(p['name'])} 학생이 많이 찾는 수업</h2></div>
        <div class="info-grid">
""")
    for h, d in p["services"]:
        out.append(f"""          <article class="info-card"><h3>{esc(h)}</h3><p>{esc(d)}</p></article>
""")
    out.append(f"""        </div>
      </section>
      <section class="reveal">
        <div class="section-title-wrap"><p class="eyebrow">Benefits</p><h2>{esc(p['name'])} 수업 특징</h2></div>
        <ul class="feature-list">{''.join(f'<li>{esc(x)}</li>' for x in p['points'])}</ul>
      </section>
      <section class="reveal">
        <div class="section-title-wrap"><p class="eyebrow">FAQ</p><h2>자주 묻는 질문</h2></div>
        <div class="faq-list">
""")
    for q, a in faq_all:
        out.append(f"""          <article class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></article>
""")
    out.append(f"""        </div>
      </section>
      <section class="banner reveal"><p>학교·학년과 수강 과목을 알려주시면 {esc(p['name'])} 시간대에 맞춘 수업 계획을 안내합니다.</p><a class="btn btn-primary" href="{cu}">무료 상담 신청</a></section>
    </main>
    <footer class="site-footer"><p>IB아이비 | {esc(p['name'])}</p><p>Copyright © 2026 globaledu.kr All rights reserved.</p></footer>
    <script src="script.js"></script>
  </body>
</html>
""")
    return "".join(out)


def hub_card(p):
    order = ["AP", "SAT", "IB", "IGCSE", "GCSE", "A-Level"]
    tags = sorted({t for _, ss in p["groups"] for _, _, ts in ss for t in ts if t in order}, key=order.index)
    meta = "".join(f"<span>{esc(t)}</span>" for t in tags)
    n = sum(len(ss) for _, ss in p["groups"])
    return (f'          <a class="city-card" href="{p["slug"]}.html"><strong>{esc(p["name"])}</strong>'
            f'<small>주요 학교 {n}곳 · {esc(p["tz"][0].split(" (")[0])}</small><div class="city-meta">{meta}</div></a>\n')


def update_hub():
    path = SITE / "overseas.html"
    s = path.read_text(encoding="utf-8")
    for p in PAGES:
        if f'href="{p["slug"]}.html"' in s:
            continue
        marker = f'<div class="section-title-wrap"><h2>{p["hub"]}</h2></div>\n        <div class="city-grid">\n'
        if marker not in s:
            # New region group: add an empty section after the last existing group in HUB_SECTION_ORDER.
            new_section = f'      <section class="reveal">\n        {marker}        </div>\n      </section>\n'
            prev = [h for h in HUB_SECTION_ORDER[:HUB_SECTION_ORDER.index(p["hub"])]
                    if f'<h2>{h}</h2></div>\n        <div class="city-grid">' in s][-1]
            prev_at = s.index(f'<h2>{prev}</h2></div>\n        <div class="city-grid">')
            insert_at = s.index("      </section>\n", prev_at) + len("      </section>\n")
            s = s[:insert_at] + new_section + s[insert_at:]
        start = s.index(marker) + len(marker)
        end = s.index("        </div>\n", start)
        s = s[:end] + hub_card(p) + s[end:]
    # Rebuild the ItemList from the cards actually on the page, in display order.
    cards = re.findall(r'<a class="city-card" href="([^"]+)\.html"><strong>([^<]+)</strong>', s)
    items = [{"@type": "ListItem", "position": i + 1, "name": html.unescape(n), "url": f"{BASE}{u}.html"} for i, (u, n) in enumerate(cards)]
    m = re.search(r'(<script type="application/ld\+json">\n)(.*?)(\n    </script>)', s, re.S)
    ld = json.loads(m.group(2))
    for node in ld["@graph"]:
        if node["@type"] == "ItemList":
            node["itemListElement"] = items
    s = s[:m.start(2)] + json.dumps(ld, ensure_ascii=False, indent=2) + s[m.end(2):]
    tz_html = "".join(f'          <article class="info-card"><h3>{esc(n)} · {esc(d)}</h3><p>{esc(t)}</p></article>\n' for n, d, t in HUB_TZ)
    s = re.sub(r'(<h2>지역별 시차와 수업 가능 시간</h2>.*?<div class="info-grid">\n).*?(        </div>)', lambda mm: mm.group(1) + tz_html + mm.group(2), s, count=1, flags=re.S)
    path.write_text(s, encoding="utf-8", newline="\n")


def update_index():
    path = SITE / "index.html"
    s = path.read_text(encoding="utf-8")
    for region, slug in INDEX_TAGS:
        s = s.replace(f'<a href="consult.html?region={region}">', f'<a href="{slug}.html">', 1)
    s = re.sub(r'(<a href="overseas.html"><strong>해외 지역별 안내 →</strong></a> )[^<]*(</p>)',
               lambda m: m.group(1) + INDEX_SUMMARY + m.group(2), s, count=1)
    path.write_text(s, encoding="utf-8", newline="\n")


def update_sitemap():
    path = SITE / "sitemap.xml"
    s = path.read_text(encoding="utf-8")
    for slug in [p["slug"] for p in PAGES]:
        if f"/{slug}.html<" not in s:
            s = s.replace("</urlset>", f"  <url><loc>{BASE}{slug}.html</loc><lastmod>{TODAY}</lastmod></url>\n</urlset>")
    s = re.sub(r"(<loc>https://globaledu.kr/(?:overseas\.html)?</loc><lastmod>)[^<]+", rf"\g<1>{TODAY}", s)
    path.write_text(s, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    for p in PAGES:
        (SITE / f"{p['slug']}.html").write_text(render_page(p), encoding="utf-8", newline="\n")
    update_hub()
    update_index()
    update_sitemap()
    print("generated", len(PAGES), "pages")
