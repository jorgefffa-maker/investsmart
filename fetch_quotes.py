import json, os, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

key = os.environ.get("ALPHA_VANTAGE_API_KEY")
if not key:
    raise SystemExit("Falta o segredo ALPHA_VANTAGE_API_KEY no GitHub.")
symbols = {
    "AAPL": ("Apple", "Ações"),
    "MSFT": ("Microsoft", "Ações"),
    "VOO": ("Vanguard S&P 500 ETF", "ETFs"),
    "QQQ": ("Invesco QQQ ETF", "ETFs"),
}
assets = {}
for symbol, (name, category) in symbols.items():
    query = urllib.parse.urlencode({"function":"TIME_SERIES_DAILY","symbol":symbol,"outputsize":"compact","apikey":key})
    req = urllib.request.Request("https://www.alphavantage.co/query?"+query, headers={"User-Agent":"InvestSmart educational demo"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
    series = data.get("Time Series (Daily)")
    if not series:
        raise SystemExit(f"Erro para {symbol}: "+str(data.get("Note") or data.get("Information") or data.get("Error Message") or "sem dados"))
    days = sorted(series, reverse=True)
    price = float(series[days[0]]["4. close"])
    previous = float(series[days[1]]["4. close"]) if len(days)>1 else price
    assets[symbol] = {"name":name,"category":category,"price":round(price,4),"change":round((price/previous-1)*100,4),"date":days[0],"currency":"USD"}
    time.sleep(1)
Path("data.json").write_text(json.dumps({"source":"Alpha Vantage","updated_at":datetime.now(timezone.utc).isoformat(),"data_type":"daily_close","assets":assets},ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
print("data.json atualizado.")
