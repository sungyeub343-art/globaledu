const urlParams = new URLSearchParams(window.location.search);
const selectedRegion = urlParams.get('region');
const selectedDistrict = urlParams.get('district');
const regionField = document.getElementById('region');

if (regionField) {
  if (selectedRegion) {
    regionField.value = selectedDistrict ? `${selectedRegion} ${selectedDistrict}` : selectedRegion;
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
  const fullName = `${selectedRegion} ${selectedDistrict}`;
  document.title = `${fullName} 국제학교 과외 안내 | Global Edu`;
  document.querySelector('meta[name="description"]')?.setAttribute('content', `${fullName} 국제학교 학생을 위한 IB·AP·IGCSE 수학과 Academic English 맞춤 과외 안내입니다. 방문·화상 수업과 무료 상담을 제공합니다.`);
  document.getElementById('district-region').textContent = selectedRegion;
  document.getElementById('district-title').textContent = `${fullName} 국제학교 과외 안내`;
  document.getElementById('district-intro').textContent = `${fullName} 국제학교 학생의 커리큘럼과 학교 일정을 확인해 수학·영어 과외, 과제 관리, 시험 대비를 맞춤으로 설계합니다.`;
  document.getElementById('breadcrumb-district').textContent = selectedDistrict;
  document.getElementById('plan-title').textContent = `${selectedDistrict} 맞춤 국제학교 학습 플랜`;
  document.getElementById('stat-copy').textContent = `${selectedDistrict} 학생의 커리큘럼, 학년, 목표에 맞춘 1:1 상담을 진행합니다.`;
  document.querySelectorAll('#consult-link, #district-consult, #bottom-consult').forEach((link) => {
    link.href = `consult.html?region=${encodeURIComponent(selectedRegion)}&district=${encodeURIComponent(selectedDistrict)}`;
  });
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
