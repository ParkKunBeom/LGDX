const pages = {
  mom: "임산부 모드",
  guardian: "보호자 모드",
  diary: "다이어리",
  trust: "신뢰 정보",
  plan: "백엔드 기능"
};

const fallbackRoutines = {
  sleep: {
    title: "수면 안정 루틴",
    food: "카페인을 피하고 단백질 간식이나 따뜻한 우유처럼 부담 적은 음식을 추천합니다.",
    action: "잠들기 1시간 전 조명을 낮추고 휴대폰 사용을 줄입니다.",
    mind: "복식호흡 5분과 걱정 메모 분리하기를 추천합니다.",
    appliances: ["에어컨 수면모드", "공기청정기 저소음", "무드등 밝기 30%"]
  },
  heat: {
    title: "체온 쾌적 루틴",
    food: "수분이 많은 과일과 물 섭취를 늘리고 짠 음식은 줄입니다.",
    action: "통풍이 잘 되는 옷을 입고 외출 전 기온과 폭염 알림을 확인합니다.",
    mind: "답답함을 느끼면 즉시 앉아서 3분간 느린 호흡을 합니다.",
    appliances: ["에어컨 제습 24도", "서큘레이터 약풍", "세탁기 산모복 코스"]
  },
  swelling: {
    title: "붓기 완화 루틴",
    food: "단백질 식사와 충분한 수분을 챙기고 과한 염분 섭취를 줄입니다.",
    action: "다리를 올리고 15분 쉬며 오래 서 있는 시간을 줄입니다.",
    mind: "몸의 변화는 기록하되 과도한 자기비난으로 연결하지 않도록 돕습니다.",
    appliances: ["안마의자 약한 강도", "공기청정기 자동", "건조기 저온 코스"]
  },
  nausea: {
    title: "속 편안 루틴",
    food: "소량씩 자주 먹고 기름지거나 냄새가 강한 음식은 피합니다.",
    action: "주방 환기를 먼저 하고 갑작스러운 움직임을 줄입니다.",
    mind: "불편감이 심하거나 탈수 느낌이 있으면 의료진 상담을 권합니다.",
    appliances: ["후드 환기", "공기청정기 강풍 10분", "냉장고 신선 식품 알림"]
  },
  anxiety: {
    title: "정신 케어 루틴",
    food: "식사 간격을 너무 길게 두지 않고 따뜻한 차나 물을 곁들입니다.",
    action: "보호자에게 감정을 공유하고 커뮤니티 정보 노출 시간을 줄입니다.",
    mind: "감정 이름 붙이기, 4초 들이마시고 6초 내쉬기를 추천합니다.",
    appliances: ["무드등 따뜻한 색", "스피커 명상 재생", "공기청정기 취침모드"]
  }
};

const fallbackTasks = [
  "산모가 말한 불편사항을 먼저 듣고 해결책은 함께 선택하기",
  "병원 예약, 영양제, 식사 시간을 체크하기",
  "가사와 무거운 짐처럼 몸에 부담되는 일을 대신하기",
  "커뮤니티 정보는 출처를 함께 확인하고 불안감을 키우지 않기"
];

const fallbackSources = [
  { name: "질병관리청", type: "공공기관", useCase: "감염병, 예방접종, 건강 수칙 검증" },
  { name: "보건복지부", type: "공공기관", useCase: "임신·출산 지원 정책과 보건 서비스 확인" },
  { name: "대한산부인과학회", type: "전문 학회", useCase: "산부인과 진료 기준과 위험 증상 판단 근거" },
  { name: "WHO", type: "국제기구", useCase: "임산부 건강, 정신건강, 영양 가이드 확인" }
];

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);
const apiEnabled = location.protocol.startsWith("http");

async function api(path, options = {}) {
  if (!apiEnabled) throw new Error("file mode");

  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "API error");
  return data;
}

function switchPage(pageId) {
  $$(".page").forEach((page) => page.classList.toggle("active", page.id === pageId));
  $$(".nav-item, .mode-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.page === pageId);
  });
  $("#pageTitle").textContent = pages[pageId] || "ThinQ Mom Care";
}

function setBackendStatus(ok) {
  const status = $("#backendStatus");
  status.textContent = ok ? "백엔드 연결됨" : "파일 실행 모드";
  status.className = ok ? "status online" : "status offline";
}

function assessRisk(stress, context = "") {
  const hasRedFlag = ["출혈", "고열", "호흡곤란", "극심한 통증", "태동 감소"].some((word) => context.includes(word));
  if (hasRedFlag || stress >= 8) {
    return { level: "risk", label: "주의", message: "위험 신호가 있거나 스트레스가 높습니다. 의료진 상담을 권장합니다." };
  }
  if (stress >= 6) {
    return { level: "watch", label: "관찰", message: "컨디션 변화를 관찰하고 보호자와 상태를 공유하세요." };
  }
  return { level: "calm", label: "안정", message: "생활 루틴으로 관리 가능한 상태로 보입니다." };
}

function renderRisk(risk) {
  const badge = $("#riskBadge");
  badge.textContent = risk.label;
  badge.className = `badge ${risk.level}`;
}

function buildFallbackAssessment() {
  const week = Number($("#weekInput").value || 24);
  const stress = Number($("#stressInput").value);
  const symptom = $("#symptomInput").value;
  const routine = fallbackRoutines[symptom];
  const risk = assessRisk(stress, $("#contextInput").value);

  return {
    week,
    trimester: week < 14 ? "초기" : week < 28 ? "중기" : "후기",
    stress,
    risk,
    recommendation: {
      title: `${week}주차 ${routine.title}`,
      food: routine.food,
      action: routine.action,
      mind: routine.mind,
      appliances: routine.appliances,
      evidencePolicy: "진단 대신 생활 관리 제안을 제공하고, 위험 증상은 의료진 상담으로 연결합니다."
    }
  };
}

async function renderCare() {
  const payload = {
    week: Number($("#weekInput").value || 24),
    symptom: $("#symptomInput").value,
    stress: Number($("#stressInput").value),
    context: $("#contextInput").value.trim()
  };

  let assessment;
  try {
    assessment = await api("/api/assessments", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    setBackendStatus(true);
  } catch {
    assessment = buildFallbackAssessment();
    setBackendStatus(false);
  }

  const routine = assessment.recommendation;
  renderRisk(assessment.risk);
  $("#careTitle").textContent = routine.title;
  $("#foodTip").textContent = routine.food;
  $("#actionTip").textContent = routine.action;
  $("#mindTip").textContent = routine.mind;

  $("#careResult").innerHTML = `
    <div class="routine-card">
      <strong>임신 ${assessment.trimester} 맞춤 평가</strong>
      <span>${assessment.risk.message}</span>
    </div>
    <div class="routine-card">
      <strong>가전 제어 추천</strong>
      <span>${routine.appliances.join(" · ")}</span>
      <button class="inline-button" id="simulateApplianceButton">가전 제어 시뮬레이션</button>
    </div>
    <div class="routine-card">
      <strong>정보 제공 원칙</strong>
      <span>${routine.evidencePolicy}</span>
    </div>
  `;

  $("#simulateApplianceButton").addEventListener("click", simulateAppliance);
}

async function simulateAppliance() {
  const device = $("#careTitle").textContent.includes("수면") ? "에어컨" : "ThinQ 기기";
  try {
    const result = await api("/api/appliances/control", {
      method: "POST",
      body: JSON.stringify({ device, command: "recommended-routine" })
    });
    alert(`${result.device} 제어 요청 저장됨: ${result.status}`);
  } catch {
    alert("파일 실행 모드에서는 가전 제어가 시뮬레이션 알림으로만 동작합니다.");
  }
}

async function renderGuardianTasks() {
  let tasks = fallbackTasks;
  try {
    const data = await api("/api/guardian/tasks");
    tasks = data.tasks;
    setBackendStatus(true);
  } catch {
    setBackendStatus(false);
  }
  $("#guardianTasks").innerHTML = tasks.map((task) => `<li>${task}</li>`).join("");
}

async function renderDiary() {
  let entries = JSON.parse(localStorage.getItem("mom-care-diary") || "[]");
  try {
    const data = await api("/api/diaries");
    entries = data.diaries;
    setBackendStatus(true);
  } catch {
    setBackendStatus(false);
  }

  $("#diaryList").innerHTML = entries
    .map((entry) => `<div class="diary-entry"><strong>${entry.mood}</strong><p>${entry.text}</p></div>`)
    .join("");
}

async function saveDiary() {
  const text = $("#diaryInput").value.trim();
  if (!text) return;

  const entry = { mood: $("#moodInput").value, text, shared: true };

  try {
    await api("/api/diaries", {
      method: "POST",
      body: JSON.stringify(entry)
    });
    setBackendStatus(true);
  } catch {
    const saved = JSON.parse(localStorage.getItem("mom-care-diary") || "[]");
    saved.unshift({ ...entry, id: `local-${Date.now()}` });
    localStorage.setItem("mom-care-diary", JSON.stringify(saved));
    setBackendStatus(false);
  }

  $("#diaryInput").value = "";
  await renderDiary();
}

async function renderTrustSources() {
  let sources = fallbackSources;
  let rules = [
    "출처가 약한 정보는 추천하지 않음",
    "의학적 진단이나 처방은 제공하지 않음",
    "위험 증상은 병원 상담 안내"
  ];

  try {
    const data = await api("/api/trust/sources");
    sources = data.sources;
    rules = data.answerRules;
    setBackendStatus(true);
  } catch {
    setBackendStatus(false);
  }

  $("#sourceList").innerHTML = sources
    .map((source) => `<div><strong>${source.name}</strong><p>${source.type} · ${source.useCase}</p></div>`)
    .join("");

  $("#answerRules").innerHTML = rules.map((rule) => `<li>${rule}</li>`).join("");
}

async function subscribe() {
  try {
    await api("/api/subscriptions", { method: "POST", body: "{}" });
    setBackendStatus(true);
  } catch {
    setBackendStatus(false);
  }
  localStorage.setItem("mom-care-subscribed", "true");
  $("#adBanner").style.display = "none";
}

$$("[data-page]").forEach((button) => {
  button.addEventListener("click", () => switchPage(button.dataset.page));
});

$("#stressInput").addEventListener("input", (event) => {
  $("#stressValue").textContent = event.target.value;
  renderRisk(assessRisk(Number(event.target.value), $("#contextInput").value));
});

$("#careButton").addEventListener("click", renderCare);
$("#saveDiaryButton").addEventListener("click", saveDiary);
$("#subscribeButton").addEventListener("click", subscribe);
$("#hideAdButton").addEventListener("click", () => {
  $("#adBanner").style.display = "none";
});

if (localStorage.getItem("mom-care-subscribed") === "true") {
  $("#adBanner").style.display = "none";
}

renderCare();
renderGuardianTasks();
renderDiary();
renderTrustSources();
