const urlParams = new URLSearchParams(window.location.search);
const selectedRegion = urlParams.get('region');
const selectedDistrict = urlParams.get('district');
const selectedLocality = urlParams.get('locality');
const regionField = document.getElementById('region');

if (regionField) {
  if (selectedRegion) {
    regionField.value = [selectedRegion, selectedDistrict, selectedLocality].filter(Boolean).join(' ');
  }
}

const districtData = {
  서울특별시: '종로구 중구 용산구 성동구 광진구 동대문구 중랑구 성북구 강북구 도봉구 노원구 은평구 서대문구 마포구 양천구 강서구 구로구 금천구 영등포구 동작구 관악구 서초구 강남구 송파구 강동구',
  경기도: '수원시 성남시 의정부시 안양시 부천시 광명시 평택시 동두천시 안산시 고양시 과천시 구리시 남양주시 오산시 시흥시 군포시 의왕시 하남시 용인시 파주시 이천시 안성시 김포시 화성시 광주시 양주시 포천시 여주시 연천군 가평군 양평군',
  인천광역시: '중구 동구 미추홀구 연수구 남동구 부평구 계양구 서구 강화군 옹진군',
  부산광역시: '중구 서구 동구 영도구 부산진구 동래구 남구 북구 해운대구 사하구 금정구 강서구 연제구 수영구 사상구 기장군',
  대구광역시: '중구 동구 서구 남구 북구 수성구 달서구 달성군 군위군',
  광주광역시: '동구 서구 남구 북구 광산구',
  대전광역시: '동구 중구 서구 유성구 대덕구',
  울산광역시: '중구 남구 동구 북구 울주군',
  세종특별자치시: '세종시',
  강원특별자치도: '춘천시 원주시 강릉시 동해시 태백시 속초시 삼척시 홍천군 횡성군 영월군 평창군 정선군 철원군 화천군 양구군 인제군 고성군 양양군',
  충청북도: '청주시 충주시 제천시 보은군 옥천군 영동군 증평군 진천군 괴산군 음성군 단양군',
  충청남도: '천안시 공주시 보령시 아산시 서산시 논산시 계룡시 당진시 금산군 부여군 서천군 청양군 홍성군 예산군 태안군',
  전북특별자치도: '전주시 군산시 익산시 정읍시 남원시 김제시 완주군 진안군 무주군 장수군 임실군 순창군 고창군 부안군',
  전라남도: '목포시 여수시 순천시 나주시 광양시 담양군 곡성군 구례군 고흥군 보성군 화순군 장흥군 강진군 해남군 영암군 무안군 함평군 영광군 장성군 완도군 진도군 신안군',
  경상북도: '포항시 경주시 김천시 안동시 구미시 영주시 영천시 상주시 문경시 경산시 의성군 청송군 영양군 영덕군 청도군 고령군 성주군 칠곡군 예천군 봉화군 울진군 울릉군',
  경상남도: '창원시 진주시 통영시 사천시 김해시 밀양시 거제시 양산시 의령군 함안군 창녕군 고성군 남해군 하동군 산청군 함양군 거창군 합천군',
  제주특별자치도: '제주시 서귀포시'
};

Object.keys(districtData).forEach((region) => {
  districtData[region] = districtData[region].split(' ');
});

const seoulLocalityData = {
  종로구: '청운동 효자동 사직동 삼청동 부암동 평창동 무악동 교남동 가회동 종로1·2·3·4가동 종로5·6가동 이화동 혜화동 창신1동 창신2동 창신3동 숭인1동 숭인2동',
  중구: '소공동 회현동 명동 필동 장충동 광희동 을지로동 신당동 다산동 약수동 청구동 신당5동 동화동 황학동 중림동',
  용산구: '후암동 용산2가동 남영동 청파동 원효로1동 원효로2동 효창동 용문동 한강로동 이촌1동 이촌2동 이태원1동 이태원2동 한남동 서빙고동 보광동',
  성동구: '왕십리2동 왕십리도선동 마장동 사근동 행당1동 행당2동 응봉동 금호1가동 금호2·3가동 금호4가동 옥수동 성수1가1동 성수1가2동 성수2가1동 성수2가3동 송정동 용답동',
  광진구: '화양동 군자동 중곡1동 중곡2동 중곡3동 중곡4동 능동 광장동 자양1동 자양2동 자양3동 자양4동 구의1동 구의2동 구의3동',
  동대문구: '용신동 제기동 전농1동 전농2동 답십리1동 답십리2동 장안1동 장안2동 청량리동 회기동 휘경1동 휘경2동 이문1동 이문2동',
  중랑구: '면목2동 면목4동 면목5동 면목7동 면목본동 면목3·8동 상봉1동 상봉2동 중화1동 중화2동 묵1동 묵2동 망우3동 망우본동 신내1동 신내2동',
  성북구: '성북동 삼선동 동선동 돈암1동 돈암2동 안암동 보문동 정릉1동 정릉2동 정릉3동 정릉4동 길음1동 길음2동 종암동 월곡1동 월곡2동 장위1동 장위2동 장위3동 석관동',
  강북구: '삼양동 미아동 송중동 송천동 삼각산동 번1동 번2동 번3동 수유1동 수유2동 수유3동 우이동 인수동',
  도봉구: '쌍문1동 쌍문2동 쌍문3동 쌍문4동 방학1동 방학2동 방학3동 창1동 창2동 창3동 창4동 창5동 도봉1동 도봉2동',
  노원구: '월계1동 월계2동 월계3동 공릉1동 공릉2동 하계1동 하계2동 중계본동 중계1동 중계2·3동 중계4동 상계1동 상계2동 상계3·4동 상계5동 상계6·7동 상계8동 상계9동 상계10동',
  은평구: '녹번동 불광1동 불광2동 갈현1동 갈현2동 구산동 대조동 응암1동 응암2동 응암3동 역촌동 신사1동 신사2동 증산동 수색동 진관동',
  서대문구: '충현동 천연동 북아현동 신촌동 연희동 홍제1동 홍제2동 홍제3동 홍은1동 홍은2동 남가좌1동 남가좌2동 북가좌1동 북가좌2동',
  마포구: '공덕동 아현동 도화동 용강동 대흥동 염리동 신수동 서강동 서교동 합정동 망원1동 망원2동 연남동 성산1동 성산2동 상암동',
  양천구: '목1동 목2동 목3동 목4동 목5동 신월1동 신월2동 신월3동 신월4동 신월5동 신월6동 신월7동 신정1동 신정2동 신정3동 신정4동 신정6동 신정7동',
  강서구: '염창동 등촌1동 등촌2동 등촌3동 화곡본동 화곡1동 화곡2동 화곡3동 화곡4동 화곡6동 화곡8동 가양1동 가양2동 가양3동 발산1동 우장산동 공항동 방화1동 방화2동 방화3동',
  구로구: '신도림동 구로1동 구로2동 구로3동 구로4동 구로5동 가리봉동 고척1동 고척2동 개봉1동 개봉2동 개봉3동 오류1동 오류2동 수궁동 항동',
  금천구: '가산동 독산1동 독산2동 독산3동 독산4동 시흥1동 시흥2동 시흥3동 시흥4동 시흥5동',
  영등포구: '영등포본동 영등포동 여의동 당산1동 당산2동 도림동 문래동 양평1동 양평2동 신길1동 신길3동 신길4동 신길5동 신길6동 신길7동 대림1동 대림2동 대림3동',
  동작구: '노량진1동 노량진2동 상도1동 상도2동 상도3동 상도4동 흑석동 사당1동 사당2동 사당3동 사당4동 사당5동 대방동 신대방1동 신대방2동',
  관악구: '보라매동 청림동 성현동 행운동 낙성대동 청룡동 은천동 중앙동 인헌동 남현동 서원동 신원동 서림동 신사동 신림동 난향동 조원동 대학동 삼성동 미성동 난곡동',
  서초구: '서초1동 서초2동 서초3동 서초4동 잠원동 반포본동 반포1동 반포2동 반포3동 반포4동 방배본동 방배1동 방배2동 방배3동 방배4동 양재1동 양재2동 내곡동',
  강남구: '신사동 논현1동 논현2동 압구정동 청담동 삼성1동 삼성2동 대치1동 대치2동 대치4동 역삼1동 역삼2동 도곡1동 도곡2동 개포1동 개포2동 개포3동 개포4동 세곡동 일원본동 일원1동 일원2동 수서동',
  송파구: '풍납1동 풍납2동 거여1동 거여2동 마천1동 마천2동 방이1동 방이2동 오륜동 오금동 송파1동 송파2동 석촌동 삼전동 가락본동 가락1동 가락2동 문정1동 문정2동 장지동 위례동 잠실본동 잠실2동 잠실3동 잠실4동 잠실6동 잠실7동',
  강동구: '강일동 상일1동 상일2동 명일1동 명일2동 고덕1동 고덕2동 암사1동 암사2동 암사3동 천호1동 천호2동 천호3동 성내1동 성내2동 성내3동 길동 둔촌1동 둔촌2동'
};

Object.keys(seoulLocalityData).forEach((district) => {
  seoulLocalityData[district] = seoulLocalityData[district].split(' ');
});

const gyeonggiLocalityData = {
  수원시: '파장동 율천동 정자1동 정자2동 영화동 송죽동 조원1동 연무동 정자3동 조원2동 세류1동 세류2동 세류3동 평동 서둔동 구운동 호매실동 곡선동 입북동 금곡동 권선2동 지동 우만1동 우만2동 인계동 매교동 매산동 고등동 화서1동 화서2동 행궁동 매탄1동 매탄2동 매탄3동 매탄4동 영통1동 영통2동 망포1동 원천동 광교1동 광교2동 권선1동 영통3동 망포2동',
  성남시: '신흥1동 신흥2동 신흥3동 태평1동 태평2동 태평3동 태평4동 수진1동 수진2동 단대동 산성동 양지동 복정동 신촌동 고등동 시흥동 성남동 금광1동 금광2동 은행1동 은행2동 상대원1동 상대원2동 상대원3동 하대원동 도촌동 중앙동 분당동 수내3동 수내1동 수내2동 정자2동 정자3동 서현1동 서현2동 이매1동 이매2동 야탑1동 야탑3동 야탑2동 구미동 운중동 금곡동 구미1동 삼평동 판교동 백현동 정자1동 정자동 위례동',
  의정부시: '의정부2동 호원1동 장암동 신곡1동 신곡2동 송산1동 자금동 가능동 흥선동 녹양동 호원2동 송산2동 송산3동 의정부1동 고산동',
  안양시: '안양1동 안양2동 안양3동 안양4동 안양5동 안양6동 안양7동 명학동 병목안동 석수1동 석수2동 충훈동 박달동 호현동 비산1동 비산2동 비산3동 부흥동 달안동 관양동 인덕원동 부림동 평촌동 평안동 귀인동 호계1동 호계2동 호계3동 범계동 신촌동 갈산동',
  부천시: '심곡3동 원미1동 상동 중4동 상1동 송내1동 소사본동 괴안동 고강1동 신흥동 심곡1동 심곡2동 소사동 원미2동 도당동 역곡2동 춘의동 역곡1동 중동 약대동 중1동 중3동 중2동 상3동 상2동 송내2동 심곡본1동 심곡본동 소사본1동 범박동 역곡3동 옥길동 고강본동 성곡동 오정동 원종2동 원종1동',
  광명시: '광명1동 광명2동 광명3동 광명4동 광명5동 광명6동 광명7동 철산1동 철산2동 철산3동 철산4동 하안1동 하안2동 하안3동 하안4동 소하1동 소하2동 일직동 학온동',
  평택시: '팽성읍 안중읍 포승읍 진위면 서탄면 고덕면 오성면 청북읍 현덕면 서정동 송탄동 지산동 송북동 신장1동 신장2동 신평동 동삭동 비전2동 용이동 비전1동 중앙동 고덕동 세교동 원평동 통복동',
  동두천시: '생연1동 생연2동 중앙동 보산동 불현동 송내동 소요동 상패동',
  안산시: '일동 이동 사동 사이동 해양동 본오1동 본오2동 본오3동 반월동 안산동 부곡동 월피동 성포동 와동 고잔동 중앙동 호수동 원곡동 백운동 신길동 초지동 선부1동 선부2동 선부3동 대부동',
  고양시: '주교동 원신동 흥도동 성사1동 성사2동 효자동 창릉동 고양동 관산동 능곡동 화정1동 화정2동 행주동 행신1동 행신2동 화전동 대덕동 행신3동 식사동 중산2동 정발산동 풍산동 백석1동 마두1동 마두2동 장항1동 장항2동 고봉동 백석2동 일산1동 일산2동 일산3동 탄현1동 주엽1동 주엽2동 대화동 송포동 가좌동 삼송1동 삼송2동 행신4동 중산1동 탄현2동 덕이동',
  과천시: '중앙동 갈현동 원문동 별양동 부림동 과천동 문원동',
  구리시: '갈매동 동구동 인창동 교문1동 교문2동 수택1동 수택2동 수택3동',
  남양주시: '와부읍 진접읍 화도읍 진건읍 오남읍 퇴계원읍 별내면 수동면 조안면 평내동 금곡동 양정동 다산1동 다산2동 별내동 호평동',
  오산시: '중앙동 대원1동 남촌동 신장1동 세마동 초평동 신장2동 대원2동',
  시흥시: '대야동 신천동 신현동 은행동 매화동 목감동 과림동 거북섬동 정왕3동 정왕4동 정왕본동 정왕1동 능곡동 군자동 월곶동 연성동 장곡동 배곧2동 배곧1동 정왕2동',
  군포시: '군포1동 산본1동 산본2동 금정동 재궁동 오금동 수리동 궁내동 광정동 대야동 군포2동 송부동',
  의왕시: '고천동 부곡동 오전동 내손1동 내손2동 청계동',
  하남시: '천현동 신장1동 신장2동 덕풍1동 덕풍2동 감북동 춘궁동 초이동 미사3동 미사1동 미사2동 덕풍3동 위례동 감일동',
  용인시: '포곡읍 모현읍 남사읍 이동읍 원삼면 백암면 양지읍 중앙동 삼가동 유림1동 동부동 구갈동 보라동 기흥동 서농동 구성동 마북동 동백3동 보정동 상하동 신갈동 영덕2동 풍덕천1동 풍덕천2동 신봉동 죽전3동 죽전2동 동천동 상현3동 상현2동 성복동 영덕1동 상갈동 동백2동 동백1동 역북동 죽전1동 상현1동 유림2동',
  파주시: '문산읍 파주읍 법원읍 조리읍 월롱면 탄현면 광탄면 파평면 적성면 금촌2동 금촌1동 금촌3동 운정5동 운정1동 운정2동 운정3동 장단면 운정4동 운정6동 교하동',
  이천시: '장호원읍 부발읍 신둔면 백사면 호법면 마장면 대월면 모가면 설성면 율면 창전동 중리동 증포동 관고동',
  안성시: '공도읍 보개면 금광면 서운면 미양면 대덕면 양성면 원곡면 일죽면 죽산면 삼죽면 고삼면 안성1동 안성2동 안성3동',
  김포시: '통진읍 고촌읍 양촌읍 대곶면 월곶면 하성면 김포본동 장기본동 사우동 풍무동 장기동 구래동 마산동 운양동',
  화성시: '봉담읍 우정읍 향남읍 남양읍 매송면 비봉면 마도면 송산면 서신면 팔탄면 장안면 양감면 정남면 새솔동 진안동 병점1동 병점2동 반월동 기배동 화산동 동탄1동 동탄2동 동탄3동 동탄4동 동탄5동 동탄6동 동탄7동 동탄8동 동탄9동',
  광주시: '능평동 초월읍 곤지암읍 도척면 퇴촌면 남종면 경안동 탄벌동 광남2동 남한산성면 쌍령동 송정동 광남1동 오포2동 오포1동 신현동',
  양주시: '백석읍 은현면 남면 광적면 장흥면 양주1동 양주2동 회천1동 회천2동 회천3동 옥정2동 옥정1동',
  포천시: '소흘읍 군내면 내촌면 가산면 신북면 창수면 영중면 일동면 이동면 영북면 관인면 화현면 포천동 선단동',
  여주시: '가남읍 점동면 세종대왕면 흥천면 금사면 산북면 대신면 북내면 강천면 여흥동 중앙동 오학동',
  연천군: '연천읍 전곡읍 군남면 청산면 백학면 미산면 왕징면 신서면 중면 장남면',
  가평군: '가평읍 설악면 청평면 상면 조종면 북면',
  양평군: '양평읍 강상면 강하면 양서면 옥천면 서종면 단월면 청운면 양동면 지평면 용문면 개군면'
};

Object.keys(gyeonggiLocalityData).forEach((district) => {
  gyeonggiLocalityData[district] = gyeonggiLocalityData[district].split(' ');
});

const localityData = {
  서울특별시: seoulLocalityData,
  경기도: gyeonggiLocalityData
};

const districtDirectory = document.getElementById('district-directory');
if (districtDirectory) {
  Object.entries(districtData).forEach(([region, districts]) => {
    const group = document.createElement('article');
    group.className = 'district-group';
    group.innerHTML = `<div class="district-group-heading"><h3>${region}</h3><span>${districts.length}개 지역</span></div><div class="district-links"></div>`;
    const links = group.querySelector('.district-links');
    districts.forEach((district) => {
      const link = document.createElement('a');
      link.className = 'district-link';
      link.href = `district.html?region=${encodeURIComponent(region)}&district=${encodeURIComponent(district)}`;
      link.innerHTML = `<strong>${district}</strong><span aria-hidden="true">↗</span>`;
      links.appendChild(link);
    });
    districtDirectory.appendChild(group);
  });
}

const districtTitle = document.getElementById('district-title');
if (districtTitle && selectedRegion && selectedDistrict) {
  const localityNames = localityData[selectedRegion]?.[selectedDistrict];
  const isKnownLocality = localityNames?.includes(selectedLocality);
  const fullName = [selectedRegion, selectedDistrict, isKnownLocality ? selectedLocality : null].filter(Boolean).join(' ');
  document.title = `${fullName} 국제학교 과외 안내 | Global Edu`;
  document.querySelector('meta[name="description"]')?.setAttribute('content', `${fullName} 국제학교 학생을 위한 IB·AP·IGCSE·A-Level 수학/영어 과외와 SAT·TOEFL·IELTS 대비 안내입니다. 방문·화상 1:1 수업과 무료 상담을 제공합니다.`);
  document.getElementById('district-region').textContent = selectedRegion;
  document.getElementById('district-title').textContent = `${fullName} 국제학교 과외 안내`;
  document.getElementById('district-intro').textContent = `${fullName} 국제학교 학생의 커리큘럼과 학교 일정을 확인해 수학·영어 과외, 내신 관리, 과제 코칭, 시험 대비를 맞춤으로 설계합니다.`;
  document.getElementById('breadcrumb-district').textContent = isKnownLocality ? `${selectedDistrict} ${selectedLocality}` : selectedDistrict;
  document.getElementById('plan-title').textContent = `${isKnownLocality ? selectedLocality : selectedDistrict} 맞춤 국제학교 학습 플랜`;
  document.getElementById('stat-copy').textContent = `${isKnownLocality ? selectedLocality : selectedDistrict} 학생의 커리큘럼, 학년, 목표에 맞춘 1:1 상담을 진행합니다.`;
  document.querySelectorAll('#consult-link, #district-consult, #bottom-consult').forEach((link) => {
    const consultParams = new URLSearchParams({ region: selectedRegion, district: selectedDistrict });
    if (isKnownLocality) consultParams.set('locality', selectedLocality);
    link.href = `consult.html?${consultParams.toString()}`;
  });

  if (localityNames) {
    const localityDirectory = document.getElementById('locality-directory');
    const localityLinks = document.getElementById('locality-links');
    localityDirectory.hidden = false;
    document.getElementById('locality-eyebrow').textContent = `${selectedDistrict} neighborhood guidance`;
    document.getElementById('locality-title').textContent = `${selectedDistrict} 동·읍·면 지역 선택`;
    document.getElementById('locality-lead').textContent = `거주 또는 수업 희망 동·읍·면을 선택하면 ${selectedDistrict} 해당 지역의 국제학교 과외 상담 페이지로 이동합니다.`;

    localityNames.forEach((locality) => {
      const link = document.createElement('a');
      const localityParams = new URLSearchParams({ region: selectedRegion, district: selectedDistrict, locality });
      link.className = 'locality-link';
      link.href = `district.html?${localityParams.toString()}`;
      link.textContent = locality;
      if (locality === selectedLocality) link.setAttribute('aria-current', 'page');
      localityLinks.appendChild(link);
    });
  }
}

const regionCards = document.querySelectorAll('.city-card');
regionCards.forEach((card) => {
  const href = card.getAttribute('href');
  if (href && href.includes('consult.html')) {
    card.addEventListener('click', (event) => {
      const regionName = card.querySelector('strong')?.textContent?.trim();
      if (regionName) {
        const targetUrl = new URL(href, window.location.href);
        targetUrl.searchParams.set('region', regionName);
        card.setAttribute('href', targetUrl.pathname + '?' + targetUrl.searchParams.toString());
      }
    });
  }
});

const revealItems = document.querySelectorAll('.reveal');

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('show');
      }
    });
  },
  { threshold: 0.2 }
);

revealItems.forEach((item, index) => {
  item.style.transitionDelay = `${index * 0.06}s`;
  observer.observe(item);
});

const counters = document.querySelectorAll('.counter');

const animateCounter = (counter) => {
  const target = Number(counter.dataset.target);
  const duration = 1200;
  const start = performance.now();
  const hasDecimal = String(target).includes('.');

  const step = (time) => {
    const progress = Math.min((time - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = target * eased;

    counter.textContent = hasDecimal ? current.toFixed(1) : Math.floor(current).toString();

    if (progress < 1) {
      requestAnimationFrame(step);
    }
  };

  requestAnimationFrame(step);
};

const counterObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting && !entry.target.dataset.done) {
        entry.target.dataset.done = 'true';
        animateCounter(entry.target);
      }
    });
  },
  { threshold: 0.8 }
);

counters.forEach((counter) => counterObserver.observe(counter));
