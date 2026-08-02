const timeLabel = document.getElementById("current-time");
const statusLabel = document.getElementById("dashboard-status");
const modeLabel = document.getElementById("dashboard-mode");
const activityLabel = document.getElementById("dashboard-activity");
const commandLabel = document.getElementById("dashboard-command");
const responseLabel = document.getElementById("dashboard-response");
const voiceWave = document.getElementById("voice-wave");
const voiceStateLabel = document.getElementById("voice-state-label");
const orbCard = document.querySelector(".voice-orb-card");
const orbLabel = document.getElementById("orb-label");
const orbSubtext = document.getElementById("orb-subtext");
const rightColumn = document.querySelector(".right-column");
const panelType = document.getElementById("panel-type");
const panelTitle = document.getElementById("panel-title");
const networkSummary = document.getElementById("network-summary");
const networkReportText = document.getElementById("network-report-text");
const closeNetworkPanel = document.getElementById("close-network-panel");
let networkPanelDismissed = false;

function updateTime() {
  const now = new Date();
  timeLabel.textContent = now.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function renderState(state) {
  if (!state) return;

  const statusText = state.status ? state.status.toUpperCase() : "SYSTEM ONLINE";
  const modeText = state.mode ? state.mode.replace(/\b\w/g, (char) => char.toUpperCase()) : "Sleep";
  const normalizedStatus = (state.status || "idle").toLowerCase();
  const voiceStrength = Number(state.details?.voice_strength ?? state.voice_strength ?? 0);
  const waveStrength = Math.min(1, Math.max(0.15, voiceStrength));

  statusLabel.textContent = statusText;
  modeLabel.textContent = `${modeText} mode`;
  if (activityLabel) {
    activityLabel.textContent = state.activity || "Awaiting voice interaction";
  }
  if (commandLabel) {
    commandLabel.textContent = `Last command: ${state.last_command || "—"}`;
  }
  if (responseLabel) {
    responseLabel.textContent = `Last response: ${state.last_response || "—"}`;
  }

  orbCard?.style.setProperty("--voice-wave-strength", waveStrength.toFixed(2));
  voiceWave?.classList.remove("is-idle", "is-listening", "is-speaking", "is-processing");
  orbCard?.classList.remove("is-speaking", "is-listening", "is-processing");

  if (normalizedStatus === "listening") {
    voiceWave?.classList.add("is-listening");
    if (voiceStateLabel) voiceStateLabel.textContent = "Listening";
    orbCard?.classList.add("is-active");
    orbLabel.textContent = "Listening";
    orbSubtext.textContent = "Your command is being captured";
  } else if (normalizedStatus === "processing") {
    voiceWave?.classList.add("is-processing");
    orbCard?.classList.add("is-processing");
    if (voiceStateLabel) voiceStateLabel.textContent = "Processing";
    orbCard?.classList.add("is-active");
    orbLabel.textContent = "Processing";
    orbSubtext.textContent = "Analyzing your request";
  } else if (normalizedStatus === "responding" || normalizedStatus === "speaking" || normalizedStatus === "active") {
    voiceWave?.classList.add("is-speaking");
    orbCard?.classList.add("is-speaking");
    if (voiceStateLabel) voiceStateLabel.textContent = normalizedStatus === "active" ? "Active" : "Speaking";
    orbCard?.classList.add("is-active");
    orbLabel.textContent = normalizedStatus === "active" ? "Active" : "Speaking";
    orbSubtext.textContent = "Voice response in progress";
  } else {
    voiceWave?.classList.add("is-idle");
    if (voiceStateLabel) voiceStateLabel.textContent = "Standby";
    orbCard?.classList.remove("is-active");
    orbLabel.textContent = "Ready";
    orbSubtext.textContent = "Ready for your command";
  }

  const networkEnabled = Boolean(state.details?.network_panel);
  const securityEnabled = Boolean(state.details?.security_panel);

  if (networkEnabled && !networkPanelDismissed) {
    rightColumn.classList.add("visible");
    panelType.textContent = "Network";
    panelTitle.textContent = "Connected Devices";
    networkSummary.textContent = state.last_response?.split("\n")[0] || "Network devices";
    if (networkReportText) {
      networkReportText.textContent = state.last_response || "No network report available.";
    }
  } else if (securityEnabled && !networkPanelDismissed) {
    rightColumn.classList.add("visible");
    panelType.textContent = "Security";
    panelTitle.textContent = "Security Report";
    networkSummary.textContent = state.last_response?.split("\n")[0] || "Security overview";
    if (networkReportText) {
      networkReportText.textContent = state.last_response || "No security report available.";
    }
  } else {
    rightColumn.classList.remove("visible");
    if (networkReportText) {
      networkReportText.textContent = "";
    }
  }
}

closeNetworkPanel?.addEventListener("click", () => {
  networkPanelDismissed = true;
  rightColumn.classList.remove("visible");
});

async function refreshState() {
  try {
    const response = await fetch(`state.json?ts=${Date.now()}`);
    if (!response.ok) throw new Error("state unavailable");
    const state = await response.json();
    renderState(state);
  } catch (error) {
    console.warn("Dashboard state unavailable", error);
  }
}

updateTime();
refreshState();
setInterval(updateTime, 1000);
setInterval(refreshState, 1200);

const commandButtons = document.querySelectorAll(".cmd-btn");
commandButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const originalText = button.textContent;
    button.textContent = "Queued";
    button.disabled = true;
    setTimeout(() => {
      button.textContent = originalText;
      button.disabled = false;
    }, 1400);
  });
});
