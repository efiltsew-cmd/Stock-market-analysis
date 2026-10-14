import json, datetime
import yfinance as yf

IDX = {"나스닥": "^IXIC", "S&P 500": "^GSPC", "다우존스": "^DJI",
       "코스피": "^KS11", "코스닥": "^KQ11", "니케이 225": "^N225"}

# 미국: 섹터 ETF(섹터 지수 대용) + 대표 상위 10종목
US = {
 "XLK": ("정보기술", "NVDA MSFT AAPL AVGO ORCL PLTR AMD CSCO IBM CRM"),
 "XLC": ("커뮤니케이션", "META GOOGL GOOG NFLX TMUS DIS CMCSA VZ T EA"),
 "XLY": ("경기소비재", "AMZN TSLA HD MCD BKNG TJX LOW SBUX NKE ORLY"),
 "XLP": ("필수소비재", "WMT COST PG KO PM PEP MDLZ MO CL MNST"),
 "XLE": ("에너지", "XOM CVX COP WMB EOG SLB KMI OKE PSX MPC"),
 "XLF": ("금융", "BRK-B JPM V MA BAC WFC GS MS AXP C"),
 "XLV": ("헬스케어", "LLY JNJ ABBV UNH MRK ABT ISRG TMO AMGN GILD"),
 "XLI": ("산업재", "GE CAT RTX GEV UBER BA HON UNP DE ETN"),
 "XLB": ("소재", "LIN SHW ECL APD FCX CTVA NEM MLM VMC DD"),
 "XLRE": ("부동산", "PLD AMT WELL EQIX SPG DLR PSA O CCI VICI"),
 "XLU": ("유틸리티", "NEE SO DUK CEG AEP SRE D VST EXC XEL"),
}

# 한국: 테마별 10종목 (이름:코드)
KR = {
 "반도체": "삼성전자:005930.KS SK하이닉스:000660.KS 한미반도체:042700.KS DB하이텍:000990.KS 리노공업:058470.KQ 이오테크닉스:039030.KQ 원익IPS:240810.KQ 주성엔지니어링:036930.KQ 하나마이크론:067310.KQ 테크윙:089030.KQ",
 "원전·SMR": "두산에너빌리티:034020.KS 한전기술:052690.KS 한전KPS:051600.KS 우리기술:032820.KQ 일진파워:094820.KQ 비에이치아이:083650.KQ 현대건설:000720.KS 삼성물산:028260.KS 한신기계:011700.KS 우진:105840.KS",
 "로보틱스": "레인보우로보틱스:277810.KQ 두산로보틱스:454910.KS 로보티즈:108490.KQ 유진로봇:056080.KQ 에스피지:058610.KQ 현대위아:011210.KS 하이젠알앤엠:160190.KQ 클로봇:466100.KQ 티로보틱스:117730.KQ 뉴로메카:348340.KQ",
 "2차전지": "LG에너지솔루션:373220.KS 삼성SDI:006400.KS 에코프로비엠:247540.KQ 에코프로:086520.KQ POSCO홀딩스:005490.KS 포스코퓨처엠:003670.KS 엘앤에프:066970.KQ SK이노베이션:096770.KS 코스모신소재:005070.KS 엔켐:348370.KQ",
 "방위산업": "한화에어로스페이스:012450.KS LIG넥스원:079550.KS 한국항공우주:047810.KS 현대로템:064350.KS 한화시스템:272210.KS 풍산:103140.KS 빅텍:065450.KQ 스페코:013810.KS 휴니드:005870.KS 퍼스텍:010820.KS",
 "항공우주": "한국항공우주:047810.KS 한화에어로스페이스:012450.KS 대한항공:003490.KS 한화시스템:272210.KS 쎄트렉아이:099320.KQ AP위성:211270.KQ 인텔리안테크:189300.KQ 컨텍:451760.KQ 켄코아에어로스페이스:274090.KQ 제노코:361390.KQ",
 "조선": "HD한국조선해양:009540.KS HD현대중공업:329180.KS 삼성중공업:010140.KS 한화오션:042660.KS HD현대미포:010620.KS 한화엔진:082740.KS HD현대마린엔진:071970.KS 세진중공업:075580.KS 동성화인텍:033500.KQ STX엔진:077970.KS",
}

kr = {k: [x.split(":") for x in v.split()] for k, v in KR.items()}
tickers = set(IDX.values())
for c, (_, s) in US.items():
    tickers |= {c, *s.split()}
for v in kr.values():
    tickers |= {t for _, t in v}

df = yf.download(sorted(tickers), period="10d", auto_adjust=True, progress=False)["Close"]

def q(t):
    if t not in df:
        print("누락:", t); return None
    s = df[t].dropna()
    if len(s) < 2:
        print("누락:", t); return None
    l, p = float(s.iloc[-1]), float(s.iloc[-2])
    return {"p": round(l, 2), "c": round(l - p, 2), "r": round((l / p - 1) * 100, 2), "d": str(s.index[-1].date())}

out = {
 "updated": datetime.datetime.utcnow().isoformat() + "Z",
 "indices": [{"n": n, **(q(t) or {})} for n, t in IDX.items()],
 "us": [{"n": n, "t": c, "q": q(c), "s": [{"t": t, "q": q(t)} for t in s.split()]} for c, (n, s) in US.items()],
 "kr": [{"n": k, "s": [{"n": n, "t": t, "q": q(t)} for n, t in v]} for k, v in kr.items()],
}
json.dump(out, open("data.json", "w"), ensure_ascii=False)

# 지수 캔들 차트용 일봉 (3년)
hist = {}
for n, t in IDX.items():
    h = yf.Ticker(t).history(period="3y", auto_adjust=False).dropna(subset=["Close"])
    hist[n] = [[str(i.date()), round(r.Open, 2), round(r.High, 2), round(r.Low, 2), round(r.Close, 2)] for i, r in h.iterrows()]
json.dump(hist, open("history.json", "w"), ensure_ascii=False)
