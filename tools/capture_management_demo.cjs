#!/usr/bin/env node
"use strict";

// Reproducible visual check for the PC-hosted C3 demo. This script refuses
// non-loopback URLs and never interacts with camera hardware.

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

function parseArguments(argv) {
  const result = {
    url: "http://127.0.0.1:8765/",
    output: path.resolve("docs", "images"),
  };
  for (let index = 2; index < argv.length; index += 1) {
    if (argv[index] === "--url" && argv[index + 1]) result.url = argv[++index];
    else if (argv[index] === "--output" && argv[index + 1]) result.output = path.resolve(argv[++index]);
    else throw new Error(`unsupported argument: ${argv[index]}`);
  }
  const parsed = new URL(result.url);
  if (parsed.protocol !== "http:" || !["127.0.0.1", "localhost"].includes(parsed.hostname)) {
    throw new Error("capture URL must be loopback HTTP");
  }
  return result;
}

async function main() {
  const options = parseArguments(process.argv);
  fs.mkdirSync(options.output, { recursive: true });
  const browserPath = process.env.SLOT20_BROWSER_PATH ||
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
  const browser = await chromium.launch({ headless: true, executablePath: browserPath });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1100 },
    deviceScaleFactor: 1,
    colorScheme: "dark",
  });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(`console: ${message.text()}`);
  });

  const screenshot = async (name) => {
    const destination = path.join(options.output, name);
    await page.screenshot({ path: destination, fullPage: true, animations: "disabled" });
    return destination;
  };
  const waitForState = async (state) => {
    await page.waitForFunction(
      (expected) => document.querySelector("#simulator-state")?.textContent === expected,
      state,
    );
  };
  const action = async (name, state) => {
    await page.locator(`[data-action="${name}"]`).click();
    await waitForState(state);
  };
  const reset = async () => {
    await action("reset", "idle");
  };
  const validate = async () => {
    await page.locator("#validate-demo").click();
    await page.locator(".verification-pass").waitFor();
    await waitForState("verified");
  };
  const reachFailure = async () => {
    await validate();
    await action("authorize", "verified");
    await action("stage", "staged");
    await action("begin_write", "writing_candidate");
    await action("pending_boot", "pending_boot");
    await action("boot_failure", "failed");
  };

  const files = [];
  try {
    await page.goto(options.url, { waitUntil: "networkidle" });
    await page.locator("#login-form button").click();
    await page.locator("#dashboard").waitFor({ state: "visible" });
    await action("reset", "idle");
    files.push(await screenshot("c3-offline-status.png"));

    await validate();
    files.push(await screenshot("c3-validation-success.png"));

    await action("authorize", "verified");
    await action("stage", "staged");
    await action("begin_write", "writing_candidate");
    await action("pending_boot", "pending_boot");
    await action("healthy", "healthy");
    await action("commit", "committed");
    files.push(await screenshot("c3-update-committed.png"));

    await reset();
    await page.locator("#validate-corrupt").click();
    await page.locator(".verification-fail").waitFor();
    await waitForState("idle");
    files.push(await screenshot("c3-corrupt-rejected.png"));

    await reset();
    await reachFailure();
    await action("rollback", "rolled_back");
    files.push(await screenshot("c3-logical-rollback.png"));

    await reset();
    await reachFailure();
    await action("recovery_required", "recovery_required");
    files.push(await screenshot("c3-recovery-required.png"));
  } finally {
    await context.close();
    await browser.close();
  }

  const report = {
    mode: "offline_host_simulation",
    url: options.url,
    screenshots: files.map((value) => path.basename(value)),
    browser_console_errors: errors,
  };
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
  if (errors.length) process.exitCode = 1;
}

main().catch((error) => {
  process.stderr.write(`${error.stack || error.message}\n`);
  process.exitCode = 1;
});
