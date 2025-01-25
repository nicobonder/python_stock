import streamlit as st
import yfinance as yf
import pandas as pd


def app():
    st.header("Choose your tickers")
    ticker_list = st.text_input(
        "Enter tickers separated by commas (e.g., AAPL, MSFT, GOOGL):", "AAPL, MSFT").strip().upper()
    tickers = [ticker.strip()
               for ticker in ticker_list.split(",") if ticker.strip()]

    def calculate_score(stock_ticker):
        try:
            stock = yf.Ticker(stock_ticker)
            data = stock.info

            # Obtener valores reales desde la API
            pe_ratio = data.get("trailingPE")
            pb_ratio = data.get("priceToBook")
            ps_ratio = data.get("priceToSalesTrailing12Months")
            dividend_yield = data.get("dividendYield")
            free_cash_flow = data.get("freeCashflow")
            revenue_growth = data.get("revenueGrowth")
            eps_growth = data.get("earningsGrowth")
            profit_margins = data.get("profitMargins")
            peg_ratio = data.get("trailingPegRatio")

            # Rango de valores para normalización
            ranges = {
                "pe_ratio": (5, 50),
                "pb_ratio": (0.5, 10),
                "ps_ratio": (0.1, 20),
                "dividend_yield": (0, 0.1),
                "free_cash_flow": (1e9, 1e12),
                "revenue_growth": (-0.1, 0.5),
                "eps_growth": (-0.1, 0.5),
                "profit_margins": (0, 0.5),
                "peg_ratio": (0, 3)
            }

            def normalize(value, min_value, max_value, reverse=False):
                if value is None:
                    return 0
                value = max(min_value, min(value, max_value))
                normalized = (value - min_value) / (max_value - min_value) if not reverse else (
                    max_value - value) / (max_value - min_value)
                return round(5 * normalized, 2)

            # Normalizar valores
            value_scores = {
                "pe_ratio": normalize(pe_ratio, *ranges["pe_ratio"], reverse=True),
                "pb_ratio": normalize(pb_ratio, *ranges["pb_ratio"], reverse=True),
                "ps_ratio": normalize(ps_ratio, *ranges["ps_ratio"], reverse=True),
                "dividend_yield": normalize(dividend_yield, *ranges["dividend_yield"]),
                "free_cash_flow": normalize(free_cash_flow, *ranges["free_cash_flow"]),
            }
            growth_scores = {
                "revenue_growth": normalize(revenue_growth, *ranges["revenue_growth"]),
                "eps_growth": normalize(eps_growth, *ranges["eps_growth"]),
                "profit_margins": normalize(profit_margins, *ranges["profit_margins"]),
                "peg_ratio": normalize(peg_ratio, *ranges["peg_ratio"], reverse=True),
            }

            # Ponderaciones
            value_weights = {
                "pe_ratio": 0.25,
                "pb_ratio": 0.20,
                "ps_ratio": 0.15,
                "dividend_yield": 0.20,
                "free_cash_flow": 0.20
            }
            growth_weights = {
                "revenue_growth": 0.30,
                "eps_growth": 0.30,
                "profit_margins": 0.20,
                "peg_ratio": 0.20
            }

            # Aplicar ponderaciones correctamente
            weighted_value_score = round(
                sum(value_scores[k] * value_weights[k] for k in value_scores), 2)
            weighted_growth_score = round(
                sum(growth_scores[k] * growth_weights[k] for k in growth_scores), 2)

            return {
                "ticker": stock_ticker,
                "value_score": weighted_value_score,
                "growth_score": weighted_growth_score
            }
        except Exception as e:
            print(f"Error processing {stock_ticker}: {e}")
            return {"ticker": stock_ticker, "value_score": 0, "growth_score": 0}

    st.subheader("Here you have a list of tickers:")
    tickers_list = "AAPL, PLTR, TSM, BYDDF, NFLX, PLTR, LULU, ONON, VCTR, CRM, NOW, SNOW, SHOP, SQ, ZM, DOCU, CRWD, DDOG, TWLO, ROKU, ZS, OKTA, TEAM, NET, MDB, TTD, U, SE, PINS, SNAP, PTON, ETSY, UBER, LYFT, ABNB, AMD, SERVICE, SAUDI, INSIGHT, CROPX, BIO, ROVENSA, AG, CAC, MSFT, GOOGL, AMZN, META, TSLA, NVDA, BRK.B, JPM, V, UNH, JNJ, WMT, PG, MA, HD, CVX, ABBV, KO, PEP, XOM, MRK, COST, AVGO, MCD, CRM, CSCO, TMO, ADBE, ACN, PFE, AMD, NFLX, LLY, INTC, NKE, AMGN, CAT, HON, UNP, MS, T, LIN, TXN, BKNG, GS, C, BA, DE, BLK, SCHW, GE, RTX, ISRG, NOW, PYPL, SO, ELV, CB, ADP, DHR, EQIX, MO, BMY, LOW, ZTS, SPGI, ADI, CME, BSX, AMT, MU, INTU, ICE, REGN, KDP, PGR, MMC, AON, GILD, LMT, SYK, TGT, CHTR, FISV, MDLZ, MD, USB, PNC, CI, HCA, CDNS, MSCI, TFC, MCO, IDXX, ITW, ANET, NSC, WM, ECL, ROP, TRV, VRTX, CL, AZO, KMB, CMG, SRE, IQV, PSA, F, EOG, APD, D, DUK, PCAR, ODFL, TT, YUM, MET, MAR, DXCM, ED, COF, PH, FTNT, KR, DG, AIG, PAYX, ORLY, SNPS, AJG, AXP, SHW, STZ, HIG, MCK, HAL, WEC, HSY, WMB, NOC, LHX, RSG, CTAS, OKE, MSCI, NEM, CTLT, EW, TSN, HSIC, FE, EMR, XEL, FAST, SYY, BAX, NDAQ, VLO, NUE, AFL, CCI, CHD, BF.B, AMP, GWW, TDG, WST, ROP, JCI, CMS, ZBH, AMCR, CF, AVB, CEG, ATO, DTE, PPL, LUV, KHC, LVS, GLW, KIM, BXP, CINF, HES, EVRG, NRG, IRM, VTR, ETR, DLR, ESS, NI, HII, PEG, FDS, BRO, MKC, SWKS, TSCO, EIX, DOV, BLL, WDC, J, UDR, HBAN, VICI, EXR, PKG, ALB, L, DHI, TRGP, XYL, AKAM, MAA, FANG, CTVA, WAT, LNT, CMS, MPWR, NDSN, AEE, RPM, TROW, CBRE, JBHT, RHI, WRB, DPZ, TTWO, ZION, BKR, MTB, POOL, KKR, PFG, RMD, VMC, HOLX, AAP, JKHY, WRK, AIZ, PKI, JAZZ, DXC, IEX, SIVB, LII, IT, JNPR, WHR, NI, FMC, HST, ROK, ETN, LNC, DRE, FRC, HBAN, VNO, IFF, MTCH, K, EXPD, VTRS, AES, GRMN, HRL, CAG, FOXA, TPR, WY, WU, APA, WH, PWR, UNM, PXD, NVR, KIM, LDOS, FOX, PNR, PNW, SJM, TCBI, NOV, CNP, STX, FTV, LEG, RGA, BEN, AOS, NWSA, IART, CNQ, SU, BMO, RY, TD, ENB, TRP, BNS, MFC, POW, BCE, CM, CNR, CP, T, EMA, FTS, NA, SLF, WCN, AQN, IFC, GWO, PPL, BAM, BN, WSP, ATD, CCL.B, DOO, MRU, BBD.B, X, TECK.B, WPM, ABX, AGI, NGT, BTO, CG, KL, FNV, SSRM, PAAS, AEM, PVG, IMG, DGC, K, ASR, FM, LUN, IVN, ABT, AIZ, ANSS, ARE, ATO, ATR, BALL, BAX, BDX, BIO, BKH, BKU, BMY, BURL, BWA, CAH, CBOE, CCI, CDAY, CCL, CE, CEG, CHRW, CHTR, CLX, CMI, CNC, CNMD, COO, COP, CPB, CSX, CTSH, CTXS, CVNA, DELL, DGX, DIS, DOW, DRI, EFX, EIX, EL, ENPH, EQH, ET, EXC, FCX, FFIV, FITB, FRC, GE, GL, GPN, GRMN, GWW, HBI, HIG, HOLX, HPQ, HRB, HUM, IAC, IBM, ICE, INCY, INTC, IP, IQV, IRM, JBHT, JKHY, KEYS, KMI, KRC, KR, KSS, L, LH, LHX, LLY, LMT, LPX, LRCX, LVS, LYB, MA, MAR, MAS, MCHP, MCO, MD, MHK, MLM, MRNA, MSCI, MTB, MXIM, NDAQ, NEE, NI, NLOK, NOV, NRG, NTRS, NVR, NWL, OMC, O, ORCL, ORLY, OTIS, OXY, PBCT, PCG, PGR, PKI, PKG, PM, PNR, PNW, PPL, PRU, PSA, PXD, QGEN, QRVO, RCL, REG, ROK, ROST, RPM, RSG, RY, SBNY, SBUX, SBAC, SEDG, SEE, SHW, SIVB, SLB, SNA, SNPS, SO, SPGI, SRE, STZ, SWK, SYK, TAP, TD, TEL, TER, TFX, TMO, TMUS, TRMB, TRV, TSCO, TT, TYL, UDR, ULTA, UMBF, UNP, UNM, UNP, UPS, URI, UTX, VFC, VLO, VMC, VNO, VRSK, VRSN, VRTX, WAT, WBA, WDC, WEC, WELL, WEN, WFC, WHR, WLTW, WM, WMT, WRB, WRK, WY, XEL, XLNX, XYL, ZBH, ZION"
    unique_tickers = ", ".join(sorted(set(tickers_list.split(", "))))
    st.write(unique_tickers)

    if st.button("Submit"):
        results = [calculate_score(ticker) for ticker in tickers]
        value_ranking = sorted(
            results, key=lambda x: x["value_score"], reverse=True)[:20]
        growth_ranking = sorted(
            results, key=lambda x: x["growth_score"], reverse=True)[:20]

        value_ranking_df = pd.DataFrame(
            [{"ticker": stock["ticker"], "Value Score": stock["value_score"]} for stock in value_ranking])
        growth_ranking_df = pd.DataFrame(
            [{"ticker": stock["ticker"], "Growth Score": stock["growth_score"]} for stock in growth_ranking])

        st.subheader("Top 20 Value Stocks")
        st.dataframe(value_ranking_df)
        st.subheader("Top 20 Growth Stocks")
        st.dataframe(growth_ranking_df)
