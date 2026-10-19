"use strict";

let csrfToken = null;

const loginPanel = document.querySelector("#login-panel");
const dashboard = document.querySelector("#dashboard");
const loginError = document.querySelector("#login-error");

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (csrfToken && options.method && options.method !== "GET") {
    headers.set("X-CSRF-Token", csrfToken);
  }
  const response = await fetch(path, {...options, headers});
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.error || `request_failed_${response.status}`);
  }
  return body;
}

function renderStatus(status) {
  document.querySelector("#hardware-profile").textContent = status.hardware_profile;
  document.querySelector("#simulator-state").textContent = status.simulator.state;
  document.querySelector("#known-good").textContent =
    `${status.simulator.known_good.release_version} · sequence ${status.simulator.known_good.release_sequence}`;
  document.querySelector("#recovery-explanation").textContent = status.recovery_explanation;
  const allowed = new Set(status.available_actions || []);
  document.querySelectorAll("[data-action]").forEach((button) => {
    button.disabled = button.dataset.action !== "reset" && !allowed.has(button.dataset.action);
  });
}

function addEvent(message, tone = "neutral") {
  const item = document.createElement("li");
  item.textContent = message;
  item.dataset.tone = tone;
  document.querySelector("#events").prepend(item);
  while (document.querySelector("#events").children.length > 8) {
    document.querySelector("#events").lastElementChild.remove();
  }
}

function renderVerification(result) {
  const root = document.querySelector("#verification-result");
  root.classList.remove("empty");
  root.replaceChildren();
  const summary = document.createElement("p");
  summary.className = result.host_verification_passed ? "verification-pass" : "verification-fail";
  summary.textContent = result.host_verification_passed
    ? "Host verification passed · installation remains unauthorized"
    : "Bundle rejected before any simulated installation step";
  root.append(summary);
  const list = document.createElement("dl");
  for (const [name, check] of Object.entries(result.checks)) {
    const term = document.createElement("dt");
    term.textContent = name.replace("_", " ");
    const detail = document.createElement("dd");
    detail.textContent = `${check.status} · ${check.code}`;
    detail.dataset.status = check.status;
    list.append(term, detail);
  }
  root.append(list);
  if (result.manifest) {
    const identity = document.createElement("p");
    identity.className = "manifest-line";
    identity.textContent = `${result.manifest.release_version} · sequence ${result.manifest.release_sequence} · ${result.manifest.component_count} synthetic components`;
    root.append(identity);
  }
}

async function validateBytes(bytes, label) {
  const response = await fetch("/api/validate", {
    method: "POST",
    headers: {
      "Content-Type": "application/octet-stream",
      "X-CSRF-Token": csrfToken,
    },
    body: bytes,
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || `request_failed_${response.status}`);
  renderVerification(body.verification);
  renderStatus(body.status);
  addEvent(
    `${label}: ${body.verification.host_verification_passed ? "verified" : "rejected"}.`,
    body.verification.host_verification_passed ? "pass" : "fail",
  );
}

async function validateDemo(corrupt) {
  const response = await fetch(corrupt ? "/api/demo-bundle-corrupt" : "/api/demo-bundle");
  if (!response.ok) throw new Error(`demo_bundle_${response.status}`);
  await validateBytes(await response.arrayBuffer(), corrupt ? "Corrupted demo" : "Synthetic demo");
}

async function loadStatus() {
  const status = await api("/api/status");
  renderStatus(status);
  loginPanel.classList.add("hidden");
  dashboard.classList.remove("hidden");
}

document.querySelector("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  loginError.textContent = "";
  try {
    const result = await api("/api/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        username: document.querySelector("#username").value,
        password: document.querySelector("#password").value,
      }),
    });
    csrfToken = result.csrf_token;
    await loadStatus();
  } catch (error) {
    loginError.textContent = error.message === "invalid_credentials"
      ? "The demonstration credentials were not accepted."
      : `Login failed: ${error.message}`;
  }
});

document.querySelector("#logout").addEventListener("click", async () => {
  try {
    await api("/api/logout", {method: "POST"});
  } finally {
    csrfToken = null;
    dashboard.classList.add("hidden");
    loginPanel.classList.remove("hidden");
  }
});

document.querySelector("#validate-demo").addEventListener("click", async () => {
  try { await validateDemo(false); } catch (error) { addEvent(`Validation error: ${error.message}`, "fail"); }
});

document.querySelector("#validate-corrupt").addEventListener("click", async () => {
  try { await validateDemo(true); } catch (error) { addEvent(`Validation error: ${error.message}`, "fail"); }
});

document.querySelector("#validate-file").addEventListener("click", async () => {
  const file = document.querySelector("#bundle-file").files[0];
  if (!file) { addEvent("Choose a bundle before validation.", "fail"); return; }
  try { await validateBytes(file, "Selected bundle"); } catch (error) { addEvent(`Validation error: ${error.message}`, "fail"); }
});

document.querySelector("#actions").addEventListener("click", async (event) => {
  const action = event.target.dataset.action;
  if (!action) return;
  document.querySelector("#action-error").textContent = "";
  try {
    const status = await api("/api/action", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({action}),
    });
    renderStatus(status);
    if (action === "reset") {
      document.querySelector("#verification-result").className = "verification empty";
      document.querySelector("#verification-result").textContent = "No bundle has been checked in this session.";
    }
    addEvent(`${action.replaceAll("_", " ")} → ${status.simulator.state}`, action.includes("failure") || action.includes("recovery") ? "fail" : "pass");
  } catch (error) {
    document.querySelector("#action-error").textContent = `Action rejected: ${error.message}`;
    addEvent(`Rejected action: ${action}.`, "fail");
  }
});
