/**
 * Email MCP Server — Silver Tier Feature 2
 * Gmail send / draft / search via Model Context Protocol
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import nodemailer from "nodemailer";
import { google } from "googleapis";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import * as dotenv from "dotenv";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.join(__dirname, ".env") });

// ── Config ────────────────────────────────────────────────────────────────────
const GMAIL_USER       = process.env.GMAIL_USER;
const GMAIL_APP_PASS   = process.env.GMAIL_APP_PASSWORD;
const VAULT_PATH       = process.env.VAULT_PATH || "E:/HC/AI_Employee_Vault";
const DRY_RUN          = process.env.DRY_RUN === "true";

const APPROVED_DIR     = path.join(VAULT_PATH, "Approved");
const PLANS_DIR        = path.join(VAULT_PATH, "Plans");
const DONE_DIR         = path.join(VAULT_PATH, "Done");
const LOGS_DIR         = path.join(VAULT_PATH, "Logs");

// ── Audit Log ─────────────────────────────────────────────────────────────────
function auditLog(entry) {
  const date = new Date().toISOString().split("T")[0];
  const logFile = path.join(LOGS_DIR, `email_mcp_${date}.json`);
  const record = {
    timestamp:   new Date().toISOString(),
    dry_run:     DRY_RUN,
    ...entry,
  };
  let logs = [];
  if (fs.existsSync(logFile)) {
    try { logs = JSON.parse(fs.readFileSync(logFile, "utf-8")); } catch {}
  }
  logs.push(record);
  fs.mkdirSync(LOGS_DIR, { recursive: true });
  fs.writeFileSync(logFile, JSON.stringify(logs, null, 2), "utf-8");
}

// ── Nodemailer Transport ──────────────────────────────────────────────────────
function getTransport() {
  return nodemailer.createTransport({
    service: "gmail",
    auth: {
      user: GMAIL_USER,
      pass: GMAIL_APP_PASS,
    },
  });
}

// ── Gmail API (OAuth) for search ──────────────────────────────────────────────
function getGmailClient() {
  const credPath  = path.join(VAULT_PATH, "Skills", "gmail-watcher", "assets", "credentials.json");
  const tokenPath = path.join(VAULT_PATH, "Skills", "gmail-watcher", "assets", "token.json");

  if (!fs.existsSync(credPath) || !fs.existsSync(tokenPath)) {
    throw new Error("Gmail OAuth credentials not found. Run generate_token.py first.");
  }

  const credentials = JSON.parse(fs.readFileSync(credPath, "utf-8"));
  const token       = JSON.parse(fs.readFileSync(tokenPath, "utf-8"));
  const { client_secret, client_id, redirect_uris } = credentials.installed || credentials.web;

  const oAuth2Client = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);
  oAuth2Client.setCredentials(token);
  return google.gmail({ version: "v1", auth: oAuth2Client });
}

// ── Tool: send_email ──────────────────────────────────────────────────────────
async function sendEmail({ to, subject, body, attachment }) {
  // Check if Approved file exists for this recipient+subject
  const approvedFiles = fs.existsSync(APPROVED_DIR)
    ? fs.readdirSync(APPROVED_DIR).filter(f => f.endsWith(".md"))
    : [];

  if (approvedFiles.length === 0 && !DRY_RUN) {
    return {
      success: false,
      message: "No approved files found in /Approved/. Move a draft to /Approved/ first.",
    };
  }

  if (DRY_RUN) {
    auditLog({ action_type: "send_email", actor: "claude", target: to, subject, result: "dry_run" });
    return { success: true, message: `[DRY_RUN] Would send email to ${to}: "${subject}"` };
  }

  const mailOptions = {
    from: GMAIL_USER,
    to,
    subject,
    text: body,
  };

  if (attachment) {
    mailOptions.attachments = [{ path: attachment }];
  }

  const transport = getTransport();
  await transport.sendMail(mailOptions);

  auditLog({ action_type: "send_email", actor: "claude", target: to, subject, result: "sent" });

  // Archive approved file to Done
  if (approvedFiles.length > 0) {
    const src = path.join(APPROVED_DIR, approvedFiles[0]);
    const dst = path.join(DONE_DIR, `SENT_${approvedFiles[0]}`);
    fs.mkdirSync(DONE_DIR, { recursive: true });
    fs.renameSync(src, dst);
  }

  return { success: true, message: `Email sent to ${to}` };
}

// ── Tool: draft_email ─────────────────────────────────────────────────────────
function draftEmail({ to, subject, body }) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const filename  = `DRAFT_${timestamp}_email.md`;
  const content   = `---
type: email_draft
to: ${to}
subject: ${subject}
created: ${new Date().toISOString()}
status: pending_approval
---

## To
${to}

## Subject
${subject}

## Body
${body}

## To APPROVE
Move this file to /Approved/ folder

## To REJECT
Move this file to /Rejected/ folder
`;

  fs.mkdirSync(PLANS_DIR, { recursive: true });
  const filePath = path.join(PLANS_DIR, filename);

  if (DRY_RUN) {
    auditLog({ action_type: "draft_email", actor: "claude", target: to, subject, result: "dry_run" });
    return { success: true, message: `[DRY_RUN] Would create draft: ${filename}`, file: filePath };
  }

  fs.writeFileSync(filePath, content, "utf-8");
  auditLog({ action_type: "draft_email", actor: "claude", target: to, subject, result: "created", file: filename });

  return { success: true, message: `Draft saved: ${filename}`, file: filePath };
}

// ── Tool: search_emails ───────────────────────────────────────────────────────
async function searchEmails({ query, max_results = 10 }) {
  const gmail = getGmailClient();

  const res = await gmail.users.messages.list({
    userId:   "me",
    q:        query,
    maxResults: max_results,
  });

  const messages = res.data.messages || [];
  if (messages.length === 0) {
    return { success: true, results: [], message: "No emails found." };
  }

  const results = [];
  for (const msg of messages.slice(0, max_results)) {
    const detail = await gmail.users.messages.get({
      userId: "me",
      id:     msg.id,
      format: "metadata",
      metadataHeaders: ["From", "Subject", "Date"],
    });

    const headers = detail.data.payload.headers || [];
    const get = (name) => headers.find(h => h.name === name)?.value || "";

    results.push({
      id:      msg.id,
      from:    get("From"),
      subject: get("Subject"),
      date:    get("Date"),
      snippet: detail.data.snippet || "",
    });
  }

  auditLog({ action_type: "search_emails", actor: "claude", target: query, result: `${results.length} results` });
  return { success: true, results, message: `Found ${results.length} emails.` };
}

// ── MCP Server ────────────────────────────────────────────────────────────────
const server = new McpServer({
  name:    "email-mcp",
  version: "1.0.0",
});

server.tool(
  "send_email",
  "Send an email via Gmail. Requires an approved file in /Approved/ folder. Never sends without approval.",
  {
    to:         z.string().email().describe("Recipient email address"),
    subject:    z.string().describe("Email subject line"),
    body:       z.string().describe("Email body text"),
    attachment: z.string().optional().describe("Optional file path to attach"),
  },
  async ({ to, subject, body, attachment }) => {
    const result = await sendEmail({ to, subject, body, attachment });
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

server.tool(
  "draft_email",
  "Save an email draft to /Plans/ folder for human review. No approval needed for drafts.",
  {
    to:      z.string().describe("Recipient email address"),
    subject: z.string().describe("Email subject line"),
    body:    z.string().describe("Email body text"),
  },
  async ({ to, subject, body }) => {
    const result = draftEmail({ to, subject, body });
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

server.tool(
  "search_emails",
  "Search Gmail inbox and return matching emails. No approval needed.",
  {
    query:       z.string().describe("Gmail search query (e.g. 'from:boss@company.com')"),
    max_results: z.number().optional().default(10).describe("Maximum number of results"),
  },
  async ({ query, max_results }) => {
    const result = await searchEmails({ query, max_results });
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// ── Start ─────────────────────────────────────────────────────────────────────
const transport = new StdioServerTransport();
await server.connect(transport);
console.error("Email MCP Server running...");
