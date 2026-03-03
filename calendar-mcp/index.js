#!/usr/bin/env node
/**
 * Calendar MCP Server — Gold Tier Feature 4
 * Google Calendar integration for AI Employee
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { google } from "googleapis";
import fs from "fs";
import path from "path";

const VAULT = process.env.VAULT_PATH || "E:/HC/AI_Employee_Vault";
const TOKEN_PATH = path.join(VAULT, "Skills/gmail-watcher/assets/token.json");
const CREDS_PATH = path.join(VAULT, "Skills/gmail-watcher/assets/credentials.json");

// OAuth2 client setup
function getAuthClient() {
  const creds = JSON.parse(fs.readFileSync(CREDS_PATH, "utf-8"));
  const { client_id, client_secret, redirect_uris } = creds.installed;
  const auth = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);
  const token = JSON.parse(fs.readFileSync(TOKEN_PATH, "utf-8"));
  auth.setCredentials(token);
  return auth;
}

const server = new McpServer({
  name: "calendar-mcp",
  version: "1.0.0",
});

// Tool 1: List upcoming events
server.tool(
  "list_events",
  {
    maxResults: z.number().optional().describe("Kitne events chahiye (default 10)"),
    daysAhead: z.number().optional().describe("Agle kitne din ke events (default 7)"),
  },
  async ({ maxResults = 10, daysAhead = 7 }) => {
    try {
      const auth = getAuthClient();
      const calendar = google.calendar({ version: "v3", auth });

      const now = new Date();
      const future = new Date();
      future.setDate(future.getDate() + daysAhead);

      const res = await calendar.events.list({
        calendarId: "primary",
        timeMin: now.toISOString(),
        timeMax: future.toISOString(),
        maxResults,
        singleEvents: true,
        orderBy: "startTime",
      });

      const events = res.data.items || [];
      if (events.length === 0) {
        return { content: [{ type: "text", text: `Agle ${daysAhead} din mein koi event nahi.` }] };
      }

      const list = events.map((e) => {
        const start = e.start.dateTime || e.start.date;
        return `- **${e.summary || "No title"}** | ${start} | ${e.location || "No location"}`;
      }).join("\n");

      return { content: [{ type: "text", text: `**Upcoming Events (${events.length}):**\n\n${list}` }] };
    } catch (err) {
      return { content: [{ type: "text", text: `Error: ${err.message}` }] };
    }
  }
);

// Tool 2: Create event
server.tool(
  "create_event",
  {
    title: z.string().describe("Event ka title"),
    startDateTime: z.string().describe("Start time ISO format (e.g. 2026-03-10T10:00:00)"),
    endDateTime: z.string().describe("End time ISO format (e.g. 2026-03-10T11:00:00)"),
    description: z.string().optional().describe("Event description"),
    location: z.string().optional().describe("Event location"),
    attendeeEmail: z.string().optional().describe("Attendee ka email"),
  },
  async ({ title, startDateTime, endDateTime, description, location, attendeeEmail }) => {
    try {
      const auth = getAuthClient();
      const calendar = google.calendar({ version: "v3", auth });

      const event = {
        summary: title,
        description: description || "",
        location: location || "",
        start: { dateTime: startDateTime, timeZone: "Asia/Karachi" },
        end: { dateTime: endDateTime, timeZone: "Asia/Karachi" },
      };

      if (attendeeEmail) {
        event.attendees = [{ email: attendeeEmail }];
      }

      const res = await calendar.events.insert({
        calendarId: "primary",
        resource: event,
      });

      return {
        content: [{
          type: "text",
          text: `✅ Event created!\n**Title:** ${title}\n**Start:** ${startDateTime}\n**Link:** ${res.data.htmlLink}`,
        }],
      };
    } catch (err) {
      return { content: [{ type: "text", text: `Error: ${err.message}` }] };
    }
  }
);

// Tool 3: Today's schedule
server.tool(
  "get_today_schedule",
  {},
  async () => {
    try {
      const auth = getAuthClient();
      const calendar = google.calendar({ version: "v3", auth });

      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);

      const res = await calendar.events.list({
        calendarId: "primary",
        timeMin: today.toISOString(),
        timeMax: tomorrow.toISOString(),
        singleEvents: true,
        orderBy: "startTime",
      });

      const events = res.data.items || [];
      if (events.length === 0) {
        return { content: [{ type: "text", text: "Aaj koi event nahi hai." }] };
      }

      const list = events.map((e) => {
        const start = e.start.dateTime
          ? new Date(e.start.dateTime).toLocaleTimeString("en-PK", { hour: "2-digit", minute: "2-digit" })
          : "All day";
        return `- **${start}** — ${e.summary || "No title"}`;
      }).join("\n");

      return { content: [{ type: "text", text: `**Today's Schedule (${events.length} events):**\n\n${list}` }] };
    } catch (err) {
      return { content: [{ type: "text", text: `Error: ${err.message}` }] };
    }
  }
);

// Tool 4: Delete event
server.tool(
  "delete_event",
  {
    eventId: z.string().describe("Event ID jo delete karni hai"),
  },
  async ({ eventId }) => {
    try {
      const auth = getAuthClient();
      const calendar = google.calendar({ version: "v3", auth });
      await calendar.events.delete({ calendarId: "primary", eventId });
      return { content: [{ type: "text", text: `✅ Event deleted: ${eventId}` }] };
    } catch (err) {
      return { content: [{ type: "text", text: `Error: ${err.message}` }] };
    }
  }
);

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
