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

# 미국 테마별 대표 종목 (미국 상장, 조선은 전업 종목이 적어 해양·해운 위주)
UST = {
 "반도체": "NVDA TSM AVGO AMD ASML MU QCOM AMAT LRCX INTC",
 "원자력·SMR": "CEG VST CCJ BWXT SMR OKLO LEU NNE UEC GEV",
 "로보틱스": "ISRG TSLA SYM TER ROK ABBNY PRCT SERV ZBRA CGNX",
 "2차전지": "ALB SQM ENVX QS EOSE FLNC SLDP MP TSLA ENS",
 "방위산업": "LMT RTX NOC GD LHX HII KTOS AVAV LDOS TDG",
 "항공우주": "BA GE HWM TDG RKLB ASTS LUNR PL SPR RDW",
 "조선·해운": "HII GD KEX MATX DAC ZIM FRO STNG SBLK GSL",
}

# 한국 WICS(GICS 기반) 11개 섹터: 섹터별 대표 종목 (직접 분류, 최대 10개)
KRS = {
 "에너지": "SK이노베이션:096770.KS S-Oil:010950.KS GS:078930.KS HD현대:267250.KS 흥구석유:024060.KS 중앙에너비스:000440.KS SK가스:018670.KS 극동유화:014530.KS 한국ANKOR유전:152550.KS",
 "소재": "POSCO홀딩스:005490.KS LG화학:051910.KS 롯데케미칼:011170.KS 고려아연:010130.KS 현대제철:004020.KS 포스코퓨처엠:003670.KS 금호석유화학:011780.KS 영풍:000670.KS 한화솔루션:009830.KS 효성첨단소재:298050.KS",
 "산업재": "한화에어로스페이스:012450.KS HD현대중공업:329180.KS 두산에너빌리티:034020.KS 삼성물산:028260.KS 현대로템:064350.KS HD한국조선해양:009540.KS 한화오션:042660.KS 삼성중공업:010140.KS LS일렉트릭:010120.KS HD현대일렉트릭:267260.KS",
 "경기관련소비재": "현대차:005380.KS 기아:000270.KS 현대모비스:012330.KS 한온시스템:018880.KS 호텔신라:008770.KS 강원랜드:035250.KS 코웨이:021240.KS 한국타이어앤테크놀로지:161390.KS HL만도:204320.KS 현대위아:011210.KS",
 "필수소비재": "KT&G:033780.KS CJ제일제당:097950.KS 아모레퍼시픽:090430.KS 오리온:271560.KS 농심:004370.KS 삼양식품:003230.KS 오뚜기:007310.KS LG생활건강:051900.KS 이마트:139480.KS 롯데웰푸드:280360.KS",
 "건강관리": "삼성바이오로직스:207940.KS 셀트리온:068270.KS 알테오젠:196170.KQ 유한양행:000100.KS 한미약품:128940.KS 리가켐바이오:141080.KQ HLB:028300.KQ 에이비엘바이오:298380.KQ 클래시스:214150.KQ 삼천당제약:000250.KQ",
 "금융": "KB금융:105560.KS 신한지주:055550.KS 하나금융지주:086790.KS 우리금융지주:316140.KS 삼성생명:032830.KS 삼성화재:000810.KS 메리츠금융지주:138040.KS 한국금융지주:071050.KS 카카오뱅크:323410.KS 기업은행:024110.KS",
 "IT": "삼성전자:005930.KS SK하이닉스:000660.KS 삼성전기:009150.KS LG이노텍:011070.KS 삼성SDS:018260.KS 한미반도체:042700.KS 리노공업:058470.KQ 이오테크닉스:039030.KQ 원익IPS:240810.KQ DB하이텍:000990.KS",
 "커뮤니케이션서비스": "NAVER:035420.KS 카카오:035720.KS SK텔레콤:017670.KS KT:030200.KS LG유플러스:032640.KS 크래프톤:259960.KS 엔씨소프트:036570.KS 넷마블:251270.KS 하이브:352820.KS 제일기획:030000.KS",
 "유틸리티": "한국전력:015760.KS 한국가스공사:036460.KS 한국지역난방공사:071320.KS 서울가스:017390.KS 삼천리:004690.KS 경동도시가스:267290.KS 대성에너지:117580.KS 지에스이:053050.KS",
 "부동산": "롯데리츠:330590.KS ESR켄달스퀘어리츠:365550.KS 신한알파리츠:293940.KS SK리츠:395400.KS 이리츠코크렙:088260.KS 제이알글로벌리츠:348950.KS 이지스밸류리츠:334890.KS 케이탑리츠:145270.KS 한화리츠:451800.KS 삼성FN리츠:448730.KS",
}

kr = {k: [x.split(":") for x in v.split()] for k, v in KR.items()}
krs = {k: [x.split(":") for x in v.split()] for k, v in KRS.items()}
tickers = set(IDX.values())
tickers |= {t for s in UST.values() for t in s.split()}
for c, (_, s) in US.items():
    tickers |= {c, *s.split()}
for v in [*kr.values(), *krs.values()]:
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

def sec(k, v):
    s = [{"n": n, "t": t, "q": q(t)} for n, t in v]
    r = [x["q"]["r"] for x in s if x["q"]]
    return {"n": k, "a": round(sum(r) / len(r), 2) if r else None, "s": s}

out = {
 "krs": [sec(k, v) for k, v in krs.items()],
 "ust": [{"n": k, "s": [{"t": t, "q": q(t)} for t in s.split()]} for k, s in UST.items()],
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

# 종목별 캔들 차트용 일봉 (2년, 미국/한국 파일 분리)
def ohlc(ts, nd):
    d = yf.download(sorted(ts), period="2y", auto_adjust=True, progress=False, group_by="ticker").dropna(how="all")
    res = {}
    for t in ts:
        try:
            x = d[t]
        except KeyError:
            print("차트 누락:", t); continue
        res[t] = {k: [None if v != v else round(float(v), nd) for v in x[c]]
                  for k, c in zip("ohlc", ["Open", "High", "Low", "Close"])}
    return {"dates": [str(i.date()) for i in d.index], "s": res}

us_t = {c for c in US} | {t for _, s in US.values() for t in s.split()} | {t for s in UST.values() for t in s.split()}
kr_t = {t for v in [*kr.values(), *krs.values()] for _, t in v}
json.dump(ohlc(us_t, 2), open("us_hist.json", "w"), ensure_ascii=False)
json.dump(ohlc(kr_t, 0), open("kr_hist.json", "w"), ensure_ascii=False)

# 밸류에이션(PER·PEG): 테마 종목만. 실패해도 위 데이터는 그대로 저장되도록 보호
try:
    from concurrent.futures import ThreadPoolExecutor

    def num(x):
        return round(float(x), 2) if isinstance(x, (int, float)) and x == x and abs(x) != float("inf") else None

    def val(t):
        try:
            i = yf.Ticker(t).info
        except Exception:
            return t, {}
        pe, fpe = i.get("trailingPE"), i.get("forwardPE")
        peg = i.get("pegRatio") or i.get("trailingPegRatio")
        if peg is None:  # Yahoo에 없으면 선행 이익 증가율로 추정
            te, fe = i.get("trailingEps"), i.get("forwardEps")
            if isinstance(pe, (int, float)) and isinstance(te, (int, float)) and isinstance(fe, (int, float)) and te > 0 and fe > te:
                peg = pe / ((fe / te - 1) * 100)
        return t, {"pe": num(pe), "fpe": num(fpe), "peg": num(peg)}

    vt = {t for s in UST.values() for t in s.split()} | {t for v in kr.values() for _, t in v}
    with ThreadPoolExecutor(4) as ex:
        vals = dict(ex.map(val, sorted(vt)))
    json.dump(vals, open("val.json", "w"), ensure_ascii=False)
except Exception as e:
    print("밸류에이션 수집 실패:", e)
