import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import xmlrpc from "xmlrpc";

// ── Odoo Config ──────────────────────────────────────────────
const ODOO_URL  = process.env.ODOO_URL      || "http://localhost";
const ODOO_PORT = parseInt(process.env.ODOO_PORT || "8069");
const ODOO_DB   = process.env.ODOO_DB       || "odoo_ai_employee";
const ODOO_USER = process.env.ODOO_USER     || "anilawaqar101@gmail.com";
const ODOO_PASS = process.env.ODOO_PASSWORD || "odoo1234";

// ── XML-RPC Clients ──────────────────────────────────────────
function makeClient(path) {
  return xmlrpc.createClient({ host: "localhost", port: ODOO_PORT, path });
}

function call(client, method, params) {
  return new Promise((resolve, reject) => {
    client.methodCall(method, params, (err, val) => {
      if (err) reject(err);
      else resolve(val);
    });
  });
}

// ── Authenticate with Odoo ───────────────────────────────────
async function authenticate() {
  const common = makeClient("/xmlrpc/2/common");
  const uid = await call(common, "authenticate", [ODOO_DB, ODOO_USER, ODOO_PASS, {}]);
  if (!uid) throw new Error("Odoo authentication failed. Check credentials.");
  return uid;
}

// ── Execute Odoo Model Method ────────────────────────────────
async function odooExec(model, method, args, kwargs = {}) {
  const uid = await authenticate();
  const models = makeClient("/xmlrpc/2/object");
  return call(models, "execute_kw", [ODOO_DB, uid, ODOO_PASS, model, method, args, kwargs]);
}

// ── MCP Server ───────────────────────────────────────────────
const server = new McpServer({
  name: "odoo-accounting",
  version: "1.0.0",
});

// ── Tool: List Customers ─────────────────────────────────────
server.tool(
  "list_customers",
  "Odoo se customers/partners ki list lao",
  { limit: z.number().optional().describe("Kitne customers chahiye (default 10)") },
  async ({ limit = 10 }) => {
    const partners = await odooExec("res.partner", "search_read",
      [[["customer_rank", ">", 0]]],
      { fields: ["id", "name", "email", "phone"], limit }
    );
    if (partners.length === 0) return { content: [{ type: "text", text: "Koi customer nahi mila." }] };
    const text = partners.map(p =>
      `ID: ${p.id} | ${p.name} | ${p.email || "no email"} | ${p.phone || "no phone"}`
    ).join("\n");
    return { content: [{ type: "text", text: `Customers (${partners.length}):\n\n${text}` }] };
  }
);

// ── Tool: Create Customer ────────────────────────────────────
server.tool(
  "create_customer",
  "Odoo mein naya customer banao",
  {
    name:  z.string().describe("Customer ka naam"),
    email: z.string().optional().describe("Email address"),
    phone: z.string().optional().describe("Phone number"),
  },
  async ({ name, email, phone }) => {
    const vals = { name, customer_rank: 1 };
    if (email) vals.email = email;
    if (phone) vals.phone = phone;
    const id = await odooExec("res.partner", "create", [vals]);
    return { content: [{ type: "text", text: `Customer bana diya! ID: ${id} | Naam: ${name}` }] };
  }
);

// ── Tool: Create Invoice ─────────────────────────────────────
server.tool(
  "create_invoice",
  "Odoo mein customer invoice banao",
  {
    customer_id:  z.number().describe("Customer ka Odoo ID (list_customers se milega)"),
    description:  z.string().describe("Invoice item description"),
    amount:       z.number().describe("Amount (without tax)"),
    currency:     z.string().optional().describe("Currency code, default USD"),
  },
  async ({ customer_id, description, amount }) => {
    const invoiceVals = {
      partner_id:    customer_id,
      move_type:     "out_invoice",
      invoice_line_ids: [[0, 0, {
        name:          description,
        quantity:      1,
        price_unit:    amount,
      }]],
    };
    const invoiceId = await odooExec("account.move", "create", [invoiceVals]);
    return {
      content: [{
        type: "text",
        text: `Invoice bana diya!\nID: ${invoiceId}\nCustomer ID: ${customer_id}\nDescription: ${description}\nAmount: ${amount}\n\nOdoo mein dekho: http://localhost:8069/web#id=${invoiceId}&model=account.move`
      }]
    };
  }
);

// ── Tool: List Invoices ──────────────────────────────────────
server.tool(
  "list_invoices",
  "Odoo se invoices ki list lao",
  {
    limit:  z.number().optional().describe("Kitni invoices chahiye (default 10)"),
    state:  z.enum(["draft", "posted", "cancel", "all"]).optional().describe("Invoice status filter"),
  },
  async ({ limit = 10, state = "all" }) => {
    const domain = [["move_type", "=", "out_invoice"]];
    if (state !== "all") domain.push(["state", "=", state]);
    const invoices = await odooExec("account.move", "search_read",
      [domain],
      { fields: ["id", "name", "partner_id", "amount_total", "state", "invoice_date"], limit }
    );
    if (invoices.length === 0) return { content: [{ type: "text", text: "Koi invoice nahi mili." }] };
    const text = invoices.map(inv =>
      `ID: ${inv.id} | ${inv.name} | ${inv.partner_id[1]} | PKR ${inv.amount_total} | ${inv.state} | ${inv.invoice_date || "no date"}`
    ).join("\n");
    return { content: [{ type: "text", text: `Invoices (${invoices.length}):\n\n${text}` }] };
  }
);

// ── Tool: Confirm Invoice ────────────────────────────────────
server.tool(
  "confirm_invoice",
  "Draft invoice ko confirm/post karo",
  { invoice_id: z.number().describe("Invoice ID jo confirm karni hai") },
  async ({ invoice_id }) => {
    await odooExec("account.move", "action_post", [[invoice_id]]);
    return { content: [{ type: "text", text: `Invoice #${invoice_id} confirm ho gayi! Ab yeh posted state mein hai.` }] };
  }
);

// ── Tool: Get Invoice Details ────────────────────────────────
server.tool(
  "get_invoice",
  "Kisi invoice ki detail dekho",
  { invoice_id: z.number().describe("Invoice ID") },
  async ({ invoice_id }) => {
    const [inv] = await odooExec("account.move", "read",
      [[invoice_id]],
      { fields: ["id", "name", "partner_id", "amount_total", "amount_tax", "state", "invoice_date", "invoice_line_ids"] }
    );
    if (!inv) return { content: [{ type: "text", text: `Invoice #${invoice_id} nahi mili.` }] };
    const text = `Invoice Details:
ID: ${inv.id}
Number: ${inv.name}
Customer: ${inv.partner_id[1]}
Date: ${inv.invoice_date || "not set"}
Status: ${inv.state}
Total: ${inv.amount_total}
Tax: ${inv.amount_tax}
Link: http://localhost:8069/web#id=${inv.id}&model=account.move`;
    return { content: [{ type: "text", text }] };
  }
);

// ── Start Server ─────────────────────────────────────────────
const transport = new StdioServerTransport();
await server.connect(transport);
