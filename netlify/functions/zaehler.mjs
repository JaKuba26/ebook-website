/* POST {"e": "aufruf:/spiel"}  -> zählt das Ereignis für heute (von js/zaehler.js)
   GET  ?k=<Lese-Schlüssel>      -> alle Zahlen als JSON (für den Assistenten Midi) */
import { createHash } from "node:crypto";
import { BOTS, speicher, zaehle } from "../lib/zaehlen.mjs";

const LESE_HASH = "47a5faf1f69edfb605256f5572a34edfd227d9425ad3e768776d0e3281afaa59";

export default async (req) => {
  if (req.method === "POST") {
    if (!BOTS.test(req.headers.get("user-agent") || "")) {
      try {
        const { e } = JSON.parse((await req.text()).slice(0, 300) || "{}");
        if (typeof e === "string") await zaehle(e.toLowerCase());
      } catch (_) { /* kaputte Anfrage ignorieren */ }
    }
    return new Response(null, { status: 204 });
  }

  const k = new URL(req.url).searchParams.get("k") || "";
  if (createHash("sha256").update(k).digest("hex") !== LESE_HASH) {
    return new Response("Kein Zugriff", { status: 403 });
  }
  const store = speicher();
  const { blobs } = await store.list();
  const tage = {}, gesamt = {};
  for (const { key } of blobs.sort((a, b) => a.key.localeCompare(b.key))) {
    const daten = (await store.get(key, { type: "json" })) || {};
    tage[key] = daten;
    for (const [e, n] of Object.entries(daten)) gesamt[e] = (gesamt[e] || 0) + n;
  }
  return Response.json({ seit: Object.keys(tage)[0] || null, gesamt, tage }, { headers: { "Cache-Control": "no-store" } });
};
