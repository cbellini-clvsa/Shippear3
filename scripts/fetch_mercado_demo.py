# -*- coding: utf-8 -*-
# Trae datos reales de mercado (actual + 12 puntos mensuales) desde APIs publicas/gratuitas.
import json, urllib.request, time
from datetime import datetime, timezone

OUT = "C:/Users/cbellini/AppData/Local/Temp/claude/C--Ignition/35878091-a70f-4f51-ad2c-1124dc464e1a/scratchpad/mercado.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (PlataClara data fetch)"}

def get(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=35) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e; time.sleep(2)
    raise last

def monthly_from_series(series, dkey, vkey, n=12):
    bym = {}
    for it in series:
        try:
            d = str(it[dkey])[:10]; ym = d[:7]; v = it[vkey]
        except Exception:
            continue
        if v is None: continue
        try: v = float(v)
        except Exception: continue
        if ym not in bym or d >= bym[ym][0]:
            bym[ym] = (d, v)
    items = sorted(bym.items())[-n:]
    return [{"m": ym, "v": round(val, 2)} for ym, (d, val) in items]

def yahoo(ticker, n=13):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=1y&interval=1mo" % ticker
    d = get(url)
    res = d["chart"]["result"][0]
    ts = res["timestamp"]; cl = res["indicators"]["quote"][0]["close"]
    bym = {}
    for t, c in zip(ts, cl):
        if c is None: continue
        ym = datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m")
        bym[ym] = round(float(c), 2)
    items = sorted(bym.items())[-n:]
    return [{"m": k, "v": v} for k, v in items]

def yahoo_full(ticker):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=1y&interval=1mo" % ticker
    d = get(url); res = d["chart"]["result"][0]
    ts = res["timestamp"]; q = res["indicators"]["quote"][0]
    o = q.get("open", []); hi = q.get("high", []); lo = q.get("low", []); cl = q.get("close", [])
    bym = {}
    for i, t in enumerate(ts):
        ym = datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m")
        def at(a): return a[i] if i < len(a) and a[i] is not None else None
        bym[ym] = (at(o), at(hi), at(lo), at(cl))
    months = sorted(bym.keys())[-12:]
    hist = [{"m": m, "v": round(bym[m][3], 2)} for m in months if bym[m][3] is not None]
    candles = [{"t": m+"-01", "o": round(bym[m][0], 2), "h": round(bym[m][1], 2), "l": round(bym[m][2], 2), "c": round(bym[m][3], 2)} for m in months if None not in bym[m]]
    return hist, candles

out = {"generado": datetime.now().strftime("%Y-%m-%d %H:%M"), "grupos": {}}

# ---------- DOLAR ----------
dolar_now = {}
try:
    for it in get("https://dolarapi.com/v1/dolares"):
        dolar_now[it.get("casa")] = it
except Exception as e:
    print("dolarapi FAIL", e)
g = []
for casa, nombre in [("oficial","Dolar oficial"),("blue","Dolar blue"),("bolsa","Dolar MEP"),("contadoconliqui","Dolar CCL")]:
    hist = []
    try:
        hist = monthly_from_series(get("https://api.argentinadatos.com/v1/cotizaciones/dolares/%s" % casa), "fecha", "venta")
    except Exception as e:
        print("dolar hist FAIL", casa, e)
    nv = dolar_now.get(casa, {})
    val = nv.get("venta") or (hist[-1]["v"] if hist else None)
    g.append({"key":"dolar_"+casa,"name":nombre,"val":val,"unit":"ARS","compra":nv.get("compra"),"venta":nv.get("venta"),"hist":hist,"src":"dolarapi.com / ArgentinaDatos"})
out["grupos"]["Dolar"] = g

# ---------- INDICADORES DEL ESTADO ----------
ind = []
def add_ind(url, key, name, unit, src):
    try:
        h = monthly_from_series(get(url), "fecha", "valor")
        ind.append({"key":key,"name":name,"val":h[-1]["v"] if h else None,"unit":unit,"hist":h,"src":src})
    except Exception as e:
        print("ind FAIL", key, e)
add_ind("https://api.argentinadatos.com/v1/finanzas/indices/inflacion", "ipc", "Inflacion mensual (IPC)", "%", "ArgentinaDatos / INDEC")
add_ind("https://api.argentinadatos.com/v1/finanzas/indices/inflacionInteranual", "ipc_ia", "Inflacion interanual", "%", "ArgentinaDatos / INDEC")
add_ind("https://api.argentinadatos.com/v1/finanzas/indices/uva", "uva", "UVA", "ARS", "ArgentinaDatos / BCRA")
add_ind("https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais", "riesgo", "Riesgo pais", "pb", "ArgentinaDatos")
# PBI / actividad: EMAE mensual desde datos.gob.ar (INDEC)
try:
    emae = get("https://apis.datos.gob.ar/series/api/series/?ids=143.3_NO_PR_2004_A_21&format=json&last=13")
    data = emae.get("data", [])
    h = [{"m": str(d)[:7], "v": round(float(v), 1)} for d, v in data if v is not None][-12:]
    ind.append({"key":"emae","name":"Actividad economica (EMAE, proxy del PBI)","val":h[-1]["v"] if h else None,"unit":"idx","hist":h,"src":"datos.gob.ar (INDEC)"})
except Exception as e:
    print("emae FAIL", e)
out["grupos"]["Indicadores del Estado"] = ind

# ---------- ACCIONES (BYMA via Yahoo) ----------
g = []
for tk, nm in [("GGAL.BA","Grupo Galicia"),("YPFD.BA","YPF"),("PAMP.BA","Pampa Energia"),("ALUA.BA","Aluar"),("BMA.BA","Banco Macro"),("TXAR.BA","Ternium Argentina")]:
    try:
        h, candles = yahoo_full(tk)
        if h:
            g.append({"key":tk,"name":nm,"ticker":tk.replace(".BA",""),"val":h[-1]["v"],"unit":"ARS","hist":h,"candles":candles,"src":"Yahoo Finance (BYMA)"})
        time.sleep(0.6)
    except Exception as e:
        print("accion FAIL", tk, e)
out["grupos"]["Acciones"] = g

# ---------- BONOS (data912: precio actual real; sin serie historica gratuita) ----------
g = []
try:
    bmap = {}
    for it in get("https://data912.com/live/arg_bonds"):
        bmap[it.get("symbol")] = it
    NOTA_BONOS = "La fuente gratuita (data912) da solo el precio del dia; la serie historica mensual de bonos se integra en la app real."
    for sym, nm in [("AL30","AL30 - Bonar 2030"),("GD30","GD30 - Global 2030"),("AL35","AL35 - Bonar 2035"),("GD35","GD35 - Global 2035"),("AE38","AE38 - Bonar 2038"),("GD41","GD41 - Global 2041")]:
        it = bmap.get(sym)
        if it:
            g.append({"key":sym,"name":nm,"ticker":sym,"val":it.get("c"),"unit":"ARS","pct":it.get("pct_change"),"hist":[],"nota":NOTA_BONOS,"src":"data912.com (BYMA)"})
except Exception as e:
    print("bonos FAIL", e)
out["grupos"]["Bonos"] = g

# ---------- CRYPTO (CoinGecko: velas OHLC mensuales) ----------
g = []
try:
    now = get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true")
except Exception as e:
    now = {}; print("coingecko price FAIL", e)
for cid, nm, sym in [("bitcoin","Bitcoin","BTC"),("ethereum","Ethereum","ETH"),("solana","Solana","SOL")]:
    try:
        oh = get("https://api.coingecko.com/api/v3/coins/%s/ohlc?vs_currency=usd&days=365" % cid)
        bym = {}
        for row in oh:
            ms, o, hi, lo, c = row[0], row[1], row[2], row[3], row[4]
            ym = datetime.fromtimestamp(ms/1000, tz=timezone.utc).strftime("%Y-%m")
            if ym not in bym:
                bym[ym] = [o, hi, lo, c]          # primera vela del mes = apertura
            else:
                e2 = bym[ym]
                if hi > e2[1]: e2[1] = hi          # maximo del mes
                if lo < e2[2]: e2[2] = lo          # minimo del mes
                e2[3] = c                          # cierre = ultima vela del mes
        months = sorted(bym.keys())[-12:]
        candles = [{"t": m+"-01", "o": round(bym[m][0],2), "h": round(bym[m][1],2), "l": round(bym[m][2],2), "c": round(bym[m][3],2)} for m in months]
        h = [{"m": m, "v": round(bym[m][3],2)} for m in months]
        val = (now.get(cid, {}) or {}).get("usd") or (candles[-1]["c"] if candles else None)
        g.append({"key":cid,"name":nm,"ticker":sym,"val":val,"unit":"USD","hist":h,"candles":candles,"src":"CoinGecko (OHLC)"})
        time.sleep(2)
    except Exception as e:
        print("cripto FAIL", cid, e)
out["grupos"]["Crypto"] = g

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)

print("=== RESUMEN ===  generado", out["generado"])
for gname, items in out["grupos"].items():
    print("%-26s %d instrumentos" % (gname, len(items)))
    for it in items:
        print("    %-34s val=%-12s hist=%d" % (it["name"][:34], str(it.get("val")), len(it.get("hist", []))))
print("JSON ->", OUT)
