// extract-receipt (free edition): turns receipt text into fields. Text comes from the
// phone's on-device OCR (sent with the upload as hq_files.ocr_text) or, for PDFs, from
// the PDF's own text layer extracted here. No paid APIs, no keys.

import { createClient } from "npm:@supabase/supabase-js@2";
import { extractText, getDocumentProxy } from "npm:unpdf";
import { parseReceipt } from "./parser.js";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

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
    const { receipt_id, text: overrideText } = await req.json();
    if (!receipt_id) return json({ error: "receipt_id required" }, 400);

    const user = createClient(SUPABASE_URL, ANON_KEY, { global: { headers: { Authorization: auth } } });
    const admin = createClient(SUPABASE_URL, SERVICE_KEY);

    const { data: receipt, error: rErr } = await user
      .from("hq_receipts").select("id, owner, file_id, hq_files(storage_path, mime, bucket, ocr_text)")
      .eq("id", receipt_id).single();
    if (rErr || !receipt) return json({ error: "Receipt not found" }, 404);
    const file = (receipt as any).hq_files as { storage_path: string; mime: string; bucket: string; ocr_text: string | null } | null;

    let text: string | null = (overrideText as string | undefined)?.trim() || file?.ocr_text?.trim() || null;
    let textSource = overrideText ? "override" : "device_ocr";
    if (!text && file?.mime === "application/pdf") {
      const { data: blob, error: dErr } = await admin.storage.from(file.bucket).download(file.storage_path);
      if (dErr || !blob) return json({ error: `Download failed: ${dErr?.message}` }, 500);
      const pdf = await getDocumentProxy(new Uint8Array(await blob.arrayBuffer()));
      const { text: pdfText } = await extractText(pdf, { mergePages: true });
      text = (pdfText as string)?.trim() || null;
      textSource = "pdf_text";
    }
    if (!text) {
      return json({ ok: false, no_text: true, error: "No readable text. Fill in the fields by hand." }, 200);
    }

    const out = parseReceipt(text);

    const { data: cats } = await user.from("hq_categories").select("id, key").eq("active", true);
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

    const { error: uErr } = await user.from("hq_receipts").update({
      vendor_id: vendorId,
      date: out.date.value,
      subtotal: out.subtotal.value, tax: out.tax.value, tip: out.tip.value, total: out.total.value,
      currency: out.currency,
      payment_method: out.payment_method.value, last4: out.last4.value,
      category_id: categoryId,
      extracted: { ...out, engine: "hq-parser", text_source: textSource },
      extracted_text: out.full_text,
      field_confidence: confidence,
      verified_fields: [],
    }).eq("id", receipt_id);
    if (uErr) return json({ error: `Save failed: ${uErr.message}` }, 500);
    if (receipt.file_id && textSource === "pdf_text") {
      await user.from("hq_files").update({ ocr_text: out.full_text }).eq("id", receipt.file_id);
    }

    const { data: dupes } = await user.rpc("hq_receipt_duplicates", { p_receipt_id: receipt_id });
    return json({ ok: true, is_receipt: out.is_receipt, duplicates: dupes ?? [], text_source: textSource });
  } catch (e) {
    return json({ error: (e as Error).message ?? String(e) }, 500);
  }
});
