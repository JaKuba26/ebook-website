/* Kurz-Links aus Videos: /kaufen und /code zählen den Klick und leiten dann sofort zu Gumroad weiter. */
import { BOTS, zaehle } from "../lib/zaehlen.mjs";

const ZIELE = {
  kaufen: "https://businessmind355.gumroad.com/l/popdsw",
  code: "https://businessmind355.gumroad.com/l/popdsw/NICHTNORMAL", // Rabattcode aus dem Spiel (50 %, max. 100)
};

export default async (req) => {
  const name = new URL(req.url).pathname.startsWith("/code") ? "code" : "kaufen";
  if (!BOTS.test(req.headers.get("user-agent") || "")) {
    // Zählen darf die Weiterleitung nie aufhalten: höchstens 1,5 Sekunden warten
    await Promise.race([zaehle("weiter:" + name).catch(() => {}), new Promise((r) => setTimeout(r, 1500))]);
  }
  return new Response(null, { status: 302, headers: { Location: ZIELE[name], "Cache-Control": "no-store" } });
};

export const config = { path: ["/kaufen", "/kaufen/", "/code", "/code/"] };
