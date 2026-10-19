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
