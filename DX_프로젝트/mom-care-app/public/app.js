const pages = {
  mom: "임산부 모드",
  guardian: "보호자 모드",
  diary: "다이어리",
  trust: "신뢰 정보",
  plan: "기능 기획"
};

const routines = {
  sleep: {
    title: "수면 안정 루틴",
    food: "카페인을 피하고 따뜻한 우유, 견과류처럼 부담 적은 간식",
    action: "잠들기 1시간 전 조명 낮추기, 실내 온도 24도 전후 유지",
    mind: "복식호흡 5분, 걱정 메모를 내일 할 일로 분리",
    appliances: ["에어컨 수면모드", "공기청정기 저소음", "무드등 밝기 30%"]
  },
  heat: {
    title: "체온 쾌적 루틴",
    food: "수분이 많은 과일과 물, 짠 음식은 줄이기",
    action: "통풍 잘 되는 옷, 외출 전 폭염 알림 확인",
    mind: "답답함을 느끼면 3분 휴식과 느린 호흡",
    appliances: ["에어컨 제습 24도", "서큘레이터 약풍", "세탁기 산모복 코스"]
  },
  swelling: {
    title: "붓기 완화 루틴",
    food: "단백질 식사와 충분한 수분, 과한 염분 줄이기",
    action: "다리 올리기 15분, 오래 서 있기 피하기",
    mind: "몸 변화 기록 후 과도한 자기비난 멈추기",
    appliances: ["안마의자 약한 강도", "공기청정기 자동", "건조기 저온 코스"]
  },
  nausea: {
    title: "속 편안 루틴",
    food: "소량씩 자주 먹기, 자극적인 냄새와 기름진 음식 피하기",
    action: "주방 환기, 갑작스러운 움직임 줄이기",
    mind: "불편감이 심하면 참지 말고 의료진 상담",
    appliances: ["후드 환기", "공기청정기 강풍 10분", "냉장고 신선 식품 알림"]
  },
  anxiety: {
    title: "정신 케어 루틴",
    food: "규칙적인 식사와 따뜻한 차, 과도한 당 섭취 줄이기",
    action: "보호자에게 감정 공유, 뉴스와 커뮤니티 정보 노출 줄이기",
    mind: "감정 이름 붙이기, 4-6 호흡 5회, 필요 시 전문 상담 연결",
    appliances: ["무드등 따뜻한 색", "스피커 명상 재생", "공기청정기 취침모드"]
  }
};

const guardianTasks = [
  "산모가 말한 불편사항을 해결하려고 하기보다 먼저 듣기",
  "병원 예약, 영양제, 식사 시간을 함께 확인하기",
  "가사와 무거운 짐처럼 몸에 부담되는 일을 대신하기",
  "허위 정보가 의심되는 글은 출처를 같이 확인하기"
];

const diarySamples = [
  { mood: "편안함", text: "오늘은 산책을 짧게 했고 밤에는 조명을 낮췄더니 잠이 조금 편했다." },
  { mood: "피곤함", text: "오후에 붓기가 있어 다리를 올리고 쉬었다. 보호자가 저녁 준비를 도와줬다." }
];

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

function switchPage(pageId) {
  $$(".page").forEach((page) => page.classList.toggle("active", page.id === pageId));
  $$(".nav-item, .mode-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.page === pageId);
  });
  $("#pageTitle").textContent = pages[pageId] || "ThinQ Mom Care";
}

function assessRisk(stress) {
  const badge = $("#riskBadge");
  if (stress >= 8) {
    badge.textContent = "주의";
    badge.className = "badge risk";
  } else if (stress >= 6) {
    badge.textContent = "관찰";
    badge.className = "badge watch";
  } else {
    badge.textContent = "안정";
    badge.className = "badge calm";
  }
}

function renderCare() {
  const week = Number($("#weekInput").value || 24);
  const stress = Number($("#stressInput").value);
  const symptom = $("#symptomInput").value;
  const routine = routines[symptom];
  const trimester = week < 14 ? "초기" : week < 28 ? "중기" : "후기";

  assessRisk(stress);
  $("#careTitle").textContent = `${week}주차 ${routine.title}`;
  $("#foodTip").textContent = routine.food;
  $("#actionTip").textContent = routine.action;
  $("#mindTip").textContent = routine.mind;

  $("#careResult").innerHTML = `
    <div class="routine-card">
      <strong>임신 ${trimester} 맞춤 케어</strong>
      <span>현재 입력한 주차와 증상 기준으로 생활 루틴을 제안합니다. 통증, 출혈, 고열, 호흡곤란 같은 위험 증상은 즉시 의료진 상담이 필요합니다.</span>
    </div>
    <div class="routine-card">
      <strong>가전 제어 추천</strong>
      <span>${routine.appliances.join(" · ")}</span>
    </div>
    <div class="routine-card">
      <strong>허위 정보 방지</strong>
      <span>앱 답변에는 출처 태그를 붙이고, 커뮤니티 글은 신고/검증 대기 상태를 둡니다.</span>
    </div>
  `;
}

function renderGuardianTasks() {
  $("#guardianTasks").innerHTML = guardianTasks.map((task) => `<li>${task}</li>`).join("");
}

function renderDiary() {
  const saved = JSON.parse(localStorage.getItem("mom-care-diary") || "[]");
  const entries = [...saved, ...diarySamples];
  $("#diaryList").innerHTML = entries
    .map((entry) => `<div class="diary-entry"><strong>${entry.mood}</strong><p>${entry.text}</p></div>`)
    .join("");
}

$$("[data-page]").forEach((button) => {
  button.addEventListener("click", () => switchPage(button.dataset.page));
});

$("#stressInput").addEventListener("input", (event) => {
  $("#stressValue").textContent = event.target.value;
  assessRisk(Number(event.target.value));
});

$("#careButton").addEventListener("click", renderCare);

$("#saveDiaryButton").addEventListener("click", () => {
  const text = $("#diaryInput").value.trim();
  if (!text) return;

  const saved = JSON.parse(localStorage.getItem("mom-care-diary") || "[]");
  saved.unshift({ mood: $("#moodInput").value, text });
  localStorage.setItem("mom-care-diary", JSON.stringify(saved));
  $("#diaryInput").value = "";
  renderDiary();
});

$("#subscribeButton").addEventListener("click", () => {
  localStorage.setItem("mom-care-subscribed", "true");
  $("#adBanner").style.display = "none";
});

$("#hideAdButton").addEventListener("click", () => {
  $("#adBanner").style.display = "none";
});

if (localStorage.getItem("mom-care-subscribed") === "true") {
  $("#adBanner").style.display = "none";
}

renderCare();
renderGuardianTasks();
renderDiary();
