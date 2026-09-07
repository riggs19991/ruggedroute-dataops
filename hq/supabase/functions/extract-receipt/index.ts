// extract-receipt: reads a receipt image/PDF from the hq-vault bucket with Claude and
// writes vendor, date, amounts, line items, a suggested category and per-field
// confidence back onto the hq_receipts row. Called by the app right after upload.
//
// Auth: the caller's JWT scopes every read/write through RLS. The service-role client
// is used only to read the founder's Anthropic API key from Vault (hq_read_secret)
// and to download the file bytes.

import Anthropic from "npm:@anthropic-ai/sdk";
import { zodOutputFormat } from "npm:@anthropic-ai/sdk/helpers/zod";
import { z } from "npm:zod@3";
import { createClient } from "npm:@supabase/supabase-js@2";
import { encodeBase64 } from "jsr:@std/encoding@1/base64";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const MODEL = "claude-opus-5";

const Field = <T extends z.ZodTypeAny>(t: T) =>
  z.object({ value: t.nullable(), confidence: z.number().min(0).max(1) });

const ReceiptSchema = z.object({
  vendor: Field(z.string()),
  date: Field(z.string().describe("YYYY-MM-DD")),
  subtotal: Field(z.number()),
  tax: Field(z.number()),
  tip: Field(z.number()),
  total: Field(z.number()),
  currency: z.string().describe("ISO 4217, default USD"),
  payment_method: Field(z.string().describe("cash, visa, mastercard, amex, discover, debit, check, paypal, other")),
  last4: Field(z.string().describe("last 4 digits of the card if printed")),
  suggested_category_key: Field(z.string().describe("one of the category keys provided")),
  is_receipt: z.boolean().describe("false if this is clearly not a receipt or invoice"),
  line_items: z.array(z.object({ description: z.string(), qty: z.number().nullable(), amount: z.number().nullable() })),
  full_text: z.string().describe("all legible text on the receipt, in reading order"),
  notes: z.string().describe("anything odd: handwritten total, partial, multiple receipts, etc."),
});

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  try {
    const auth = req.headers.get("Authorization") ?? "";
    if (!auth.startsWith("Bearer ")) return json({ error: "Not signed in" }, 401);
    const { receipt_id } = await req.json();
    if (!receipt_id) return json({ error: "receipt_id required" }, 400);

    const user = createClient(SUPABASE_URL, ANON_KEY, { global: { headers: { Authorization: auth } } });
    const admin = createClient(SUPABASE_URL, SERVICE_KEY);

    const { data: receipt, error: rErr } = await user
      .from("hq_receipts").select("id, owner, file_id, hq_files(storage_path, mime, bucket)")
      .eq("id", receipt_id).single();
    if (rErr || !receipt) return json({ error: "Receipt not found" }, 404);
    const file = (receipt as any).hq_files as { storage_path: string; mime: string; bucket: string } | null;
    if (!file) return json({ error: "Receipt has no file" }, 400);

    const { data: apiKey, error: kErr } = await admin.rpc("hq_read_secret", { p_owner: receipt.owner, p_key: "anthropic_api_key" });
    if (kErr) return json({ error: `Secret lookup failed: ${kErr.message}` }, 500);
    if (!apiKey) return json({ error: "No Anthropic API key on file. Add it under Settings → AI." }, 412);

    const { data: blob, error: dErr } = await admin.storage.from(file.bucket).download(file.storage_path);
    if (dErr || !blob) return json({ error: `Download failed: ${dErr?.message}` }, 500);
    const bytes = new Uint8Array(await blob.arrayBuffer());
    const b64 = encodeBase64(bytes);

    const { data: cats } = await user.from("hq_categories").select("id, key, name, schedule_c_line").eq("active", true).order("sort");
    const catList = (cats ?? []).map((c) => `${c.key}: ${c.name}`).join("\n");

    const isPdf = file.mime === "application/pdf";
    const mediaBlock = isPdf
      ? { type: "document" as const, source: { type: "base64" as const, media_type: "application/pdf" as const, data: b64 } }
      : { type: "image" as const, source: { type: "base64" as const, media_type: file.mime as "image/jpeg" | "image/png" | "image/webp" | "image/gif", data: b64 } };

    const client = new Anthropic({ apiKey });
    const response = await client.messages.parse({
      model: MODEL,
      max_tokens: 8000,
      output_config: { effort: "low", format: zodOutputFormat(ReceiptSchema) },
      system:
        "You read receipts and invoices for a small business's bookkeeping. Extract exactly what is printed; " +
        "never invent a value. Give each field a confidence from 0 to 1. Use null when a value is absent or illegible. " +
        "Dates are YYYY-MM-DD; if only month/day are printed, infer the year from context and lower the confidence. " +
        "Amounts are plain numbers without currency symbols. The total is the amount actually paid.",
      messages: [{
        role: "user",
        content: [
          mediaBlock,
          { type: "text", text: `Extract this receipt. Choose suggested_category_key from these keys only:\n${catList}\n\nBusiness: digital media production, outdoor/mapping app development, field verification trips (vehicle, fuel, camping, gear).` },
        ],
      }],
    });
    if (response.stop_reason === "refusal") return json({ error: "The model declined to read this file." }, 422);
    const out = response.parsed_output;
    if (!out) return json({ error: "Could not parse the model output" }, 502);

    // Vendor: match existing (alias / exact / prefix) else create.
    let vendorId: string | null = null; let vendorDefaultCat: string | null = null;
    if (out.vendor.value) {
      const { data: m } = await user.rpc("hq_match_vendor", { p_name: out.vendor.value });
      const match = Array.isArray(m) && m.length ? m[0] : null;
      if (match) { vendorId = match.vendor_id; vendorDefaultCat = match.default_category_id; }
      else { const { data: v } = await user.rpc("hq_upsert_vendor", { p_name: out.vendor.value }); vendorId = v ?? null; }
    }
    let categoryId: string | null = vendorDefaultCat;
    const catByKey = (cats ?? []).find((c) => c.key === out.suggested_category_key.value);
    if (!categoryId && catByKey) categoryId = catByKey.id;

    const confidence: Record<string, number> = {
      vendor: out.vendor.confidence, date: out.date.confidence, subtotal: out.subtotal.confidence,
      tax: out.tax.confidence, tip: out.tip.confidence, total: out.total.confidence,
      payment_method: out.payment_method.confidence, last4: out.last4.confidence,
      category: vendorDefaultCat ? 1 : out.suggested_category_key.confidence,
    };
    const dateOk = out.date.value && /^\d{4}-\d{2}-\d{2}$/.test(out.date.value) ? out.date.value : null;

    const update = {
      vendor_id: vendorId,
      date: dateOk,
      subtotal: out.subtotal.value, tax: out.tax.value, tip: out.tip.value, total: out.total.value,
      currency: (out.currency || "USD").toUpperCase().slice(0, 3),
      payment_method: out.payment_method.value, last4: out.last4.value,
      category_id: categoryId,
      extracted: { ...out, model: MODEL, usage: response.usage },
      extracted_text: out.full_text,
      field_confidence: confidence,
      verified_fields: [] as string[],
      notes: out.notes && out.notes.trim() ? out.notes.trim() : null,
    };
    const { error: uErr } = await user.from("hq_receipts").update(update).eq("id", receipt_id);
    if (uErr) return json({ error: `Save failed: ${uErr.message}` }, 500);

    await user.from("hq_receipt_line_items").delete().eq("receipt_id", receipt_id);
    if (out.line_items.length) {
      await user.from("hq_receipt_line_items").insert(
        out.line_items.slice(0, 60).map((li, i) => ({ receipt_id, description: li.description, qty: li.qty, amount: li.amount, sort: i })));
    }
    if (receipt.file_id) await user.from("hq_files").update({ ocr_text: out.full_text }).eq("id", receipt.file_id);

    const { data: dupes } = await user.rpc("hq_receipt_duplicates", { p_receipt_id: receipt_id });
    return json({ ok: true, is_receipt: out.is_receipt, duplicates: dupes ?? [], usage: response.usage });
  } catch (e) {
    const msg = e instanceof Anthropic.AuthenticationError ? "The Anthropic API key was rejected. Check it under Settings → AI."
      : e instanceof Anthropic.RateLimitError ? "Anthropic rate limit hit. Try again in a minute."
      : e instanceof Anthropic.APIError ? `Anthropic API error ${e.status}: ${e.message}`
      : (e as Error).message ?? String(e);
    return json({ error: msg }, 500);
  }
});
