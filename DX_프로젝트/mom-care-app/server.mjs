import { createServer } from "node:http";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = fileURLToPath(new URL("./public", import.meta.url));
const dataRoot = fileURLToPath(new URL("./backend-data", import.meta.url));
const storePath = join(dataRoot, "store.json");
const port = Number(process.env.PORT || 5173);

const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml"
};

const routines = {
  sleep: {
    label: "수면 불편",
    title: "수면 안정 루틴",
    food: "저녁에는 카페인을 피하고, 단백질 간식이나 따뜻한 우유처럼 부담 적은 음식을 추천합니다.",
    action: "잠들기 1시간 전 조명을 낮추고 휴대폰 사용을 줄입니다.",
    mind: "복식호흡 5분과 걱정 메모 분리하기를 추천합니다.",
    appliances: ["에어컨 수면모드", "공기청정기 저소음", "무드등 밝기 30%"]
  },
  heat: {
    label: "더위와 답답함",
    title: "체온 쾌적 루틴",
    food: "수분이 많은 과일과 물 섭취를 늘리고 짠 음식은 줄입니다.",
    action: "통풍이 잘 되는 옷을 입고 외출 전 기온과 폭염 알림을 확인합니다.",
    mind: "답답함을 느끼면 즉시 앉아서 3분간 느린 호흡을 합니다.",
    appliances: ["에어컨 제습 24도", "서큘레이터 약풍", "세탁기 산모복 코스"]
  },
  swelling: {
    label: "손발 붓기",
    title: "붓기 완화 루틴",
    food: "단백질 식사와 충분한 수분을 챙기고 과한 염분 섭취를 줄입니다.",
    action: "다리를 올리고 15분 쉬며 오래 서 있는 시간을 줄입니다.",
    mind: "몸의 변화는 기록하되 과도한 자기비난으로 연결하지 않도록 돕습니다.",
    appliances: ["안마의자 약한 강도", "공기청정기 자동", "건조기 저온 코스"]
  },
  nausea: {
    label: "입덧과 속 불편",
    title: "속 편안 루틴",
    food: "소량씩 자주 먹고 기름지거나 냄새가 강한 음식은 피합니다.",
    action: "주방 환기를 먼저 하고 갑작스러운 움직임을 줄입니다.",
    mind: "불편감이 심하거나 탈수 느낌이 있으면 의료진 상담을 권합니다.",
    appliances: ["후드 환기", "공기청정기 강풍 10분", "냉장고 신선 식품 알림"]
  },
  anxiety: {
    label: "불안과 예민함",
    title: "정신 케어 루틴",
    food: "식사 간격을 너무 길게 두지 않고 따뜻한 차나 물을 곁들입니다.",
    action: "보호자에게 감정을 공유하고 커뮤니티 정보 노출 시간을 줄입니다.",
    mind: "감정 이름 붙이기, 4초 들이마시고 6초 내쉬기, 필요 시 전문 상담 연결을 추천합니다.",
    appliances: ["무드등 따뜻한 색", "스피커 명상 재생", "공기청정기 취침모드"]
  }
};

const trustedSources = [
  {
    name: "질병관리청",
    type: "공공기관",
    useCase: "감염병, 예방접종, 건강 수칙 검증"
  },
  {
    name: "보건복지부",
    type: "공공기관",
    useCase: "임신·출산 지원 정책과 보건 서비스 확인"
  },
  {
    name: "대한산부인과학회",
    type: "전문 학회",
    useCase: "산부인과 진료 기준과 위험 증상 판단 근거"
  },
  {
    name: "WHO",
    type: "국제기구",
    useCase: "임산부 건강, 정신건강, 영양 가이드 확인"
  }
];

const guardianTasks = [
  "산모가 말한 불편사항을 먼저 듣고 해결책은 함께 선택하기",
  "병원 예약, 영양제, 식사 시간을 체크하기",
  "가사와 무거운 짐처럼 몸에 부담되는 일을 대신하기",
  "커뮤니티 정보는 출처를 함께 확인하고 불안감을 키우지 않기"
];

const defaultStore = {
  diaries: [
    {
      id: "sample-1",
      mood: "편안함",
      text: "오늘은 산책을 짧게 했고 밤에는 조명을 낮췄더니 잠이 조금 편했다.",
      shared: true,
      createdAt: "2026-05-20T00:00:00.000Z"
    }
  ],
  communityPosts: [
    {
      id: "post-1",
      title: "밤에 더울 때 도움이 된 루틴",
      body: "에어컨 수면모드와 무드등을 같이 쓰니 잠드는 시간이 줄었다.",
      reports: 0,
      status: "published"
    }
  ],
  subscriptions: [],
  applianceLogs: [],
  assessments: []
};

function sendJson(res, status, body) {
  res.writeHead(status, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(body, null, 2));
}

async function readBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString("utf8");
  return raw ? JSON.parse(raw) : {};
}

async function readStore() {
  await mkdir(dataRoot, { recursive: true });
  if (!existsSync(storePath)) {
    await writeFile(storePath, JSON.stringify(defaultStore, null, 2), "utf8");
  }
  return JSON.parse(await readFile(storePath, "utf8"));
}

async function writeStore(store) {
  await mkdir(dataRoot, { recursive: true });
  await writeFile(storePath, JSON.stringify(store, null, 2), "utf8");
}

function getTrimester(week) {
  if (week < 14) return "초기";
  if (week < 28) return "중기";
  return "후기";
}

function getRisk(stress, context = "") {
  const redFlags = ["출혈", "고열", "호흡곤란", "극심한 통증", "태동 감소"];
  const matched = redFlags.filter((word) => context.includes(word));

  if (matched.length > 0 || stress >= 8) {
    return {
      level: "risk",
      label: "주의",
      message: "위험 신호가 있거나 스트레스가 높습니다. 앱 추천만 따르지 말고 의료진 상담을 권장합니다.",
      redFlags: matched
    };
  }

  if (stress >= 6) {
    return {
      level: "watch",
      label: "관찰",
      message: "오늘은 컨디션 변화를 관찰하고 보호자와 상태를 공유하는 편이 좋습니다.",
      redFlags: []
    };
  }

  return {
    level: "calm",
    label: "안정",
    message: "생활 루틴으로 관리 가능한 상태로 보입니다.",
    redFlags: []
  };
}

function buildAssessment(body) {
  const week = Math.min(42, Math.max(1, Number(body.week || 24)));
  const stress = Math.min(10, Math.max(1, Number(body.stress || 5)));
  const symptom = routines[body.symptom] ? body.symptom : "sleep";
  const routine = routines[symptom];
  const risk = getRisk(stress, body.context || "");

  return {
    id: `assessment-${Date.now()}`,
    week,
    trimester: getTrimester(week),
    symptom,
    symptomLabel: routine.label,
    stress,
    context: body.context || "",
    risk,
    recommendation: {
      title: `${week}주차 ${routine.title}`,
      food: routine.food,
      action: routine.action,
      mind: routine.mind,
      appliances: routine.appliances,
      evidencePolicy: "진단 대신 생활 관리 제안을 제공하고, 위험 증상은 의료진 상담으로 연결합니다."
    },
    createdAt: new Date().toISOString()
  };
}

async function handleApi(req, res, url) {
  const store = await readStore();

  if (req.method === "GET" && url.pathname === "/api/health") {
    return sendJson(res, 200, { ok: true, service: "ThinQ Mom Care Backend" });
  }

  if (req.method === "POST" && url.pathname === "/api/assessments") {
    const assessment = buildAssessment(await readBody(req));
    store.assessments.unshift(assessment);
    await writeStore(store);
    return sendJson(res, 201, assessment);
  }

  if (req.method === "GET" && url.pathname === "/api/recommendations") {
    const symptom = url.searchParams.get("symptom") || "sleep";
    const week = Number(url.searchParams.get("week") || 24);
    return sendJson(res, 200, buildAssessment({ symptom, week, stress: 5 }));
  }

  if (req.method === "GET" && url.pathname === "/api/guardian/tasks") {
    return sendJson(res, 200, { tasks: guardianTasks });
  }

  if (req.method === "GET" && url.pathname === "/api/diaries") {
    return sendJson(res, 200, { diaries: store.diaries });
  }

  if (req.method === "POST" && url.pathname === "/api/diaries") {
    const body = await readBody(req);
    const diary = {
      id: `diary-${Date.now()}`,
      mood: body.mood || "기록",
      text: String(body.text || "").trim(),
      shared: Boolean(body.shared),
      createdAt: new Date().toISOString()
    };
    if (!diary.text) return sendJson(res, 400, { error: "일지 내용을 입력해주세요." });
    store.diaries.unshift(diary);
    await writeStore(store);
    return sendJson(res, 201, diary);
  }

  if (req.method === "GET" && url.pathname === "/api/community/posts") {
    return sendJson(res, 200, { posts: store.communityPosts });
  }

  if (req.method === "POST" && url.pathname === "/api/community/posts") {
    const body = await readBody(req);
    const post = {
      id: `post-${Date.now()}`,
      title: body.title || "공감 기록",
      body: String(body.body || "").trim(),
      reports: 0,
      status: "published",
      createdAt: new Date().toISOString()
    };
    if (!post.body) return sendJson(res, 400, { error: "게시글 내용을 입력해주세요." });
    store.communityPosts.unshift(post);
    await writeStore(store);
    return sendJson(res, 201, post);
  }

  if (req.method === "POST" && url.pathname.startsWith("/api/community/posts/") && url.pathname.endsWith("/report")) {
    const postId = url.pathname.split("/")[4];
    const post = store.communityPosts.find((item) => item.id === postId);
    if (!post) return sendJson(res, 404, { error: "게시글을 찾을 수 없습니다." });
    post.reports += 1;
    post.status = post.reports >= 3 ? "review" : post.status;
    await writeStore(store);
    return sendJson(res, 200, post);
  }

  if (req.method === "GET" && url.pathname === "/api/trust/sources") {
    return sendJson(res, 200, {
      sources: trustedSources,
      answerRules: [
        "출처가 약한 정보는 추천하지 않음",
        "의학적 진단이나 처방은 제공하지 않음",
        "위험 증상은 병원 상담 안내",
        "커뮤니티 글은 신고 누적 시 검토 상태로 전환"
      ]
    });
  }

  if (req.method === "POST" && url.pathname === "/api/appliances/control") {
    const body = await readBody(req);
    const log = {
      id: `appliance-${Date.now()}`,
      device: body.device || "ThinQ device",
      command: body.command || "simulate",
      status: "simulated",
      createdAt: new Date().toISOString()
    };
    store.applianceLogs.unshift(log);
    await writeStore(store);
    return sendJson(res, 200, log);
  }

  if (req.method === "POST" && url.pathname === "/api/subscriptions") {
    const subscription = {
      id: `subscription-${Date.now()}`,
      plan: "ad-free",
      price: 3900,
      status: "active",
      createdAt: new Date().toISOString()
    };
    store.subscriptions.unshift(subscription);
    await writeStore(store);
    return sendJson(res, 201, subscription);
  }

  return sendJson(res, 404, { error: "API route not found" });
}

async function serveStatic(res, url) {
  const safePath = normalize(decodeURIComponent(url.pathname)).replace(/^(\.\.[/\\])+/, "");
  let filePath = join(appRoot, safePath === "/" ? "index.html" : safePath);

  if (!existsSync(filePath)) {
    filePath = join(appRoot, "index.html");
  }

  const body = await readFile(filePath);
  res.writeHead(200, {
    "Content-Type": contentTypes[extname(filePath)] || "application/octet-stream"
  });
  res.end(body);
}

createServer(async (req, res) => {
  try {
    const url = new URL(req.url || "/", `http://${req.headers.host}`);
    if (url.pathname.startsWith("/api/")) {
      await handleApi(req, res, url);
      return;
    }
    await serveStatic(res, url);
  } catch (error) {
    sendJson(res, 500, { error: error.message });
  }
}).listen(port, () => {
  console.log(`ThinQ Mom Care app: http://localhost:${port}`);
  console.log(`API health check: http://localhost:${port}/api/health`);
});
