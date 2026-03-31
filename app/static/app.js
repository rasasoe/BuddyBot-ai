const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const voiceBtn = document.getElementById("voice-btn");
const mapCanvas = document.getElementById("map-canvas");
const mapCtx = mapCanvas.getContext("2d");
const waypointSelect = document.getElementById("waypoint-select");
const waypointList = document.getElementById("waypoint-list");
const mapAnalysis = document.getElementById("map-analysis");
const mapSummaryText = document.getElementById("map-summary-text");
const waypointCountChip = document.getElementById("waypoint-count-chip");

let waypointState = [];

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

async function sendChat(message) {
  addMessage("user", message);
  const response = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  const data = await response.json();
  addMessage("bot", data.response);
  speak(data.response);
  await Promise.all([refreshStatus(), refreshWaypoints()]);
}

async function sendRobotCommand(command, params = {}) {
  const response = await fetch("/robot/command", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command, params }),
  });
  const data = await response.json();
  addMessage("bot", data.message);
  await refreshStatus();
}

async function refreshHealth() {
  const response = await fetch("/health");
  const data = await response.json();
  document.getElementById("health-ollama").textContent = data.ollama;
  document.getElementById("health-robot").textContent = data.robot_bridge;
  document.getElementById("health-sqlite").textContent = data.sqlite;
}

async function refreshStatus() {
  const response = await fetch("/robot/status");
  const status = await response.json();
  document.getElementById("status-battery").textContent = `${status.battery}%`;
  document.getElementById("status-mode").textContent = status.mode;
  document.getElementById("status-follow").textContent = status.follow_enabled ? "켜짐" : "꺼짐";
  document.getElementById("status-source").textContent = status.active_source;
  document.getElementById("status-ros2").textContent = status.ros2_connected ? "연결됨" : "mock";
  document.getElementById("status-workspace").textContent = status.buddybot_workspace || "-";
}

async function refreshWaypoints() {
  const [waypointRes, summaryRes] = await Promise.all([
    fetch("/nav/waypoints"),
    fetch("/nav/map-summary"),
  ]);
  const waypointData = await waypointRes.json();
  const summary = await summaryRes.json();
  waypointState = waypointData.items || [];
  renderWaypointSelect();
  renderWaypointList();
  renderMapAnalysis(summary);
  drawMap(waypointState, summary.bounds || null);
}

function renderWaypointSelect() {
  waypointSelect.innerHTML = "";
  waypointState.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.name;
    option.textContent = `${item.name} (${item.x}, ${item.y})`;
    waypointSelect.appendChild(option);
  });
}

function renderWaypointList() {
  waypointList.innerHTML = "";
  waypointState.forEach((item) => {
    const el = document.createElement("div");
    el.className = "waypoint-item";
    el.innerHTML = `<strong>${item.name}</strong><span>${item.description || "설명 없음"}</span><span>x=${item.x}, y=${item.y}, θ=${item.theta}</span>`;
    waypointList.appendChild(el);
  });
  waypointCountChip.textContent = `체크포인트 ${waypointState.length}개`;
}

function renderMapAnalysis(summary) {
  mapSummaryText.textContent = summary.summary || "체크포인트 분석 정보가 없습니다.";
  mapAnalysis.innerHTML = "";
  (summary.zones || []).forEach((zone) => {
    const el = document.createElement("div");
    el.className = "analysis-item";
    el.innerHTML = `<strong>${zone.name}</strong><span>${zone.points.join(", ")}</span>`;
    mapAnalysis.appendChild(el);
  });
}

function drawMap(items, bounds) {
  const width = mapCanvas.width;
  const height = mapCanvas.height;
  mapCtx.clearRect(0, 0, width, height);

  mapCtx.fillStyle = "#fffcf7";
  mapCtx.fillRect(0, 0, width, height);

  mapCtx.strokeStyle = "rgba(24, 19, 15, 0.12)";
  mapCtx.lineWidth = 1;
  for (let x = 40; x < width; x += 40) {
    mapCtx.beginPath();
    mapCtx.moveTo(x, 0);
    mapCtx.lineTo(x, height);
    mapCtx.stroke();
  }
  for (let y = 40; y < height; y += 40) {
    mapCtx.beginPath();
    mapCtx.moveTo(0, y);
    mapCtx.lineTo(width, y);
    mapCtx.stroke();
  }

  if (!items.length) return;

  const minX = bounds ? bounds.min_x : Math.min(...items.map((item) => item.x));
  const maxX = bounds ? bounds.max_x : Math.max(...items.map((item) => item.x));
  const minY = bounds ? bounds.min_y : Math.min(...items.map((item) => item.y));
  const maxY = bounds ? bounds.max_y : Math.max(...items.map((item) => item.y));

  const pad = 50;
  const scaleX = (value) => pad + ((value - minX) / Math.max(maxX - minX, 1)) * (width - pad * 2);
  const scaleY = (value) => height - pad - ((value - minY) / Math.max(maxY - minY, 1)) * (height - pad * 2);

  items.forEach((item, index) => {
    const x = scaleX(item.x);
    const y = scaleY(item.y);
    mapCtx.fillStyle = index === 0 ? "#c2410c" : "#0f766e";
    mapCtx.beginPath();
    mapCtx.arc(x, y, 8, 0, Math.PI * 2);
    mapCtx.fill();

    mapCtx.fillStyle = "#18130f";
    mapCtx.font = "14px 'IBM Plex Sans KR'";
    mapCtx.fillText(item.name, x + 12, y - 12);
  });
}

async function goSelectedWaypoint() {
  const name = waypointSelect.value;
  if (!name) return;
  const response = await fetch("/nav/go", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  const data = await response.json();
  addMessage("bot", data.message);
}

async function saveWaypoint(event) {
  event.preventDefault();
  const name = document.getElementById("waypoint-name").value.trim();
  const x = Number(document.getElementById("waypoint-x").value);
  const y = Number(document.getElementById("waypoint-y").value);
  const theta = Number(document.getElementById("waypoint-theta").value || 0);
  if (!name) return;

  const response = await fetch("/nav/waypoints", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, x, y, theta, description: `${name} user-defined checkpoint` }),
  });
  await response.json();
  addMessage("bot", `${name} 체크포인트를 저장했습니다.`);
  event.target.reset();
  await refreshWaypoints();
}

function speak(text) {
  if (!("speechSynthesis" in window)) return;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "ko-KR";
  utterance.rate = 1;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;
  chatInput.value = "";
  sendChat(message);
});

document.querySelectorAll("[data-command]").forEach((button) => {
  button.addEventListener("click", () => sendRobotCommand(button.dataset.command));
});

document.querySelectorAll("[data-manual]").forEach((button) => {
  button.addEventListener("click", () => {
    sendRobotCommand("manual", { direction: button.dataset.manual, speed: 0.35, duration: 1.0 });
  });
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => sendChat(button.dataset.prompt));
});

document.getElementById("refresh-status").addEventListener("click", refreshStatus);
document.getElementById("refresh-map").addEventListener("click", refreshWaypoints);
document.getElementById("go-selected").addEventListener("click", goSelectedWaypoint);
document.getElementById("waypoint-form").addEventListener("submit", saveWaypoint);

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
  const recognition = new SpeechRecognition();
  recognition.lang = "ko-KR";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  voiceBtn.addEventListener("click", () => {
    recognition.start();
    voiceBtn.textContent = "듣는 중...";
  });

  recognition.addEventListener("result", (event) => {
    const transcript = event.results[0][0].transcript;
    chatInput.value = transcript;
    sendChat(transcript);
  });

  recognition.addEventListener("end", () => {
    voiceBtn.textContent = "음성 듣기";
  });
} else {
  voiceBtn.disabled = true;
  voiceBtn.textContent = "브라우저 미지원";
}

addMessage("bot", "버디봇 커맨드 센터가 준비됐습니다. 수동 조작, 추종, 음성 대화, 체크포인트 이동을 바로 실행할 수 있습니다.");
refreshHealth();
refreshStatus();
refreshWaypoints();
setInterval(refreshStatus, 5000);
