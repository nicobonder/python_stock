import streamlit as st
import yfinance as yf
import pandas as pd


# Limpiar con un filtro las empresas basura
def clean_tickers_list(tickers):
    filtered_tickers = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        data = stock.info

        # Obtener y mostrar los valores para depuración
        free_cash_flow = data.get("freeCashflow")
        revenue_growth = data.get("revenueGrowth")
        profit_margins = data.get("profitMargins")
        debt_To_Equity = data.get("debtToEquity")

        # print(f"Ticker: {ticker}")
        # print(f"Free Cash Flow: {free_cash_flow}")
        # print(f"Revenue Growth: {revenue_growth}")
        # print(f"Profit Margins: {profit_margins}")
        # print(f"Debt to Equity: {debt_To_Equity}")

        # Filtrar por free cash flow negativo
        if free_cash_flow is None or free_cash_flow < 0:
            continue

        # Filtrar por revenue growth negativo
        if revenue_growth is None or revenue_growth < 0:
            continue

        # Filtrar por profit margin negativo
        if profit_margins is None or profit_margins < 0:
            continue

        # Filtrar por Total Debt/Equity superior al 200%
        if debt_To_Equity is None or debt_To_Equity > 200:
            continue

        filtered_tickers.append(ticker)
    # print("filtered_tickers:", filtered_tickers)
    return filtered_tickers


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


def app():
    st.header("Stock Ranking App")

    st.subheader("Here you have a list of tickers:")
    tickers_list = "AAPL, GRAB, APP, AXS, PANW, ATI, KALV, RGTI, MLI, LCID, ATI, CROX, ESAB, CRS, CDT, AIT, SFM, LC, TSM, GGAL, BBAR, BMA, PAM, YPF SUPV, ITUB, BBD, STLA, BYDDF, ONTO, AEHR, RITM, OKLO, UEC, SMR, CCJ, LEU, VST, MRVL, NFLX, PLTR, LULU, ONON, YELP, VCTR, NOW, SNOW, SHOP, XYZ, HOOD, ZM, DOCU, CRWD, DDOG, TWLO, NU, ROKU, VZ, ZS, OKTA, TEAM, NET, MELI, MDB, ASTS, ATAT, AFCG, TTD, U,ACHR, SE, PINS, GLOB, SNAP, PTON, ETSY, UBER, LYFT, ABNB, AMD, BIO, AG, CAC, MSFT, GOOGL, AMZN, META, TSLA, NVDA, BRK.B, JPM, V, UNH, JNJ, WMT, PG, MA, HD, CVX, NTAP, ABBV, KO, PEP, XOM, MRK, COST, AVGO, MCD, CRM, CSCO, TMO, ADBE, ACN, PFE, AMD, NFLX, LLY, INTC, NKE, AMGN, CAT, HON, UNP, MS, T, LIN, TXN, BKNG, GS, C, BA, DE, BLK, SCHW, GE, RTX, ISRG, NOW, PYPL, CMCSA, SO, ELV, CB, ADP, DHR, EQIX, MO, BMY, LOW, ZTS, SPGI, ADI, CME, BSX, AMT, MU, INTU, ICE, REGN, KDP, PGR, MMC, AON, GILD, LMT, SYK, TGT, CHTR, FISV, MDLZ, MD, USB, PNC, CI, HCA, CDNS, MSCI, TFC, MCO, IDXX, ITW, ANET, NSC, WM, ECL, ROP, TRV, VRTX, CL, AZO, KMB, CMG, SRE, IQV, PSA, F, EOG, APD, D, DUK, PCAR, ODFL, TT, YUM, MET, MAR, DXCM, ED, COF, PH, HIMS, TOST, RKLB, FTNT, KR, DG, AIG, PAYX, ORLY, SNPS, AJG, AXP, SHW, STZ, HIG, MCK, HAL, WEC, HSY, WMB, NOC, LHX, RSG, CTAS, OKE, MSCI, NEM, CTLT, EW, TSN, HSIC, FE, EMR, XEL, FAST, SYY, BAX, NDAQ, VLO, NIO, NUE, AFL, CCI, CHD, AMP, GWW, TDG, WST, ROP, JCI, CMS, ZBH, AMCR, CF, AVB, CEG, ATO, DTE, PPL, LUV, KHC, LVS, GLW, KIM, BXP, CINF, HES, EVRG, NRG, IRM, VTR, ETR, DLR, ESS, NI, HII, PEG, FDS, BRO, MKC, SWKS, TSCO, EIX, DOV, WDC, AAOI, J, UDR, HBAN, VICI, EXR, PKG, ALB, L, DHI, TRGP, XYL, AKAM, MAA, FANG, CTVA, WAT, LNT, CMS, MPWR, NDSN, AEE, RPM, TROW, CBRE, JBHT, RHI, WRB, DPZ, TTWO, ZION, BKR, MTB, POOL, KKR, PFG, RMD, VMC, HOLX, AAP, JKHY, WRK, AIZ, PKI, JAZZ, DXC, IEX, SIVB, LII, IT, JNPR, WHR, NI, HST, ROK, ETN, LNC, DRE, FRC, HBAN, VNO, IFF, MTCH, K, EXPD, VTRS, GRMN, HRL, CAG, FOXA, TPR, WY, WU, WH, PWR, UNM, NVR, KIM, LDOS, FOX, PNR, PNW, SJM, TCBI, ABBN.SW, RYAAY, NOV, CNP, STX, FTV, POWL, BTU, ASIX, LEG, RGA, BEN, AOS, NWSA, IART, CNQ, SU, RY, TD, ENB, TRP, BNS, MFC, POW, BCE, CM, CNR, CP, T, EMA, FTS, NA, SLF, WCN, IFC, GWO, PPL, BN, WSP, CCL.B, DOO, MRU, X, WPM, AGI, NGT, BTO, CG, KL, FNV, SSRM, PAAS, AEM, PVG, IMG, DGC, K, ASR, FM, LUN, IVN, ABT, AIZ, ANSS, ARE, ATO, ATR, BALL, BAX, BDX, BIO, BKH, BMY, BURL, BWA, CAH, CBOE, CCI, CCL, CEG, CHRW, CHTR, CLX, CMI, CNC, CNMD, COO, COP, CPB, CSX, CTSH, CTXS, CVNA, DELL, DGX, DIS, DOW, DRI, EFX, EIX, EL, ENPH, EQH, ET, HUBS, EXC, FCX, FFIV, FITB, FRC, GE, GL, GPN, GRMN, GWW, HBI, HIG, HOLX, HPQ, HRB, HUM, IAC, IBM, ICE, INCY, INTC, IP, IQV, IRM, JBHT, JKHY, KEYS, KMI, KRC, KR, L, LH, LHX, LLY, LMT, LPX, LRCX, LVS, MA, MAR, MAS, MCHP, MCO, MD, MHK, MLM, MRNA, MSCI, MTB, MXIM, NDAQ, NEE, NI, NLOK, NOV, NRG, NTRS, NVR, NWL, OMC, O, ORCL, ORLY, OTIS, OXY, PBCT, PCG, PGR, PKI, PKG, PM, PNR, PNW, PPL, PRU, PSA, PXD, QGEN, QRVO, RCL, REG, ROK, ROST, RPM, RSG, RY, SBNY, SBUX, SBAC, SEDG, SEE, SHW, SLB, SNA, SNPS, SO, SPGI, SRE, STZ, SWK, EVLV, SYK, TAP, TD, TEL, TER, TFX, TMO, TMUS, TRMB, TRV, TSCO, TT, TYL, UDR, ULTA, UMBF, UNP, UNM, UNP, UPS, URI, UTX, VFC, VLO, VMC, VNO, VRSK, VRSN, VRTX, WAT, WBA, WDC, WEC, WELL, WEN, WFC, WHR, WLTW, WM, WMT, WRB, WY, XEL, XLNX, XYL, ZBH, ZION, ENSG"

    unique_tickers = ", ".join(sorted(set(tickers_list.split(", "))))
    # print tickers_list.length
    print("unique_tickers length:", len(unique_tickers.split(", ")))

    st.write(unique_tickers)

    tickers = st.text_area("Enter tickers separated by commas").split(',')
    tickers = [ticker.strip().upper() for ticker in tickers]

    if st.button("Submit"):
        filtered_tickers = clean_tickers_list(tickers)

        if filtered_tickers:
            scores = [calculate_score(ticker) for ticker in filtered_tickers]

            value_ranking = sorted(
                scores, key=lambda x: x["value_score"], reverse=True)[:20]
            growth_ranking = sorted(
                scores, key=lambda x: x["growth_score"], reverse=True)[:20]

            value_ranking_df = pd.DataFrame(
                [{"ticker": stock["ticker"], "Value Score": stock["value_score"]} for stock in value_ranking])
            growth_ranking_df = pd.DataFrame(
                [{"ticker": stock["ticker"], "Growth Score": stock["growth_score"]} for stock in growth_ranking])

            st.subheader("Top 20 Value Stocks")
            st.dataframe(value_ranking_df)
            st.subheader("Top 20 Growth Stocks")
            st.dataframe(growth_ranking_df)
        else:
            st.write("No tickers passed the filters.")


if __name__ == "__main__":
    app()

# if st.button("Submit"):
#     filtered_tickers = clean_tickers_list(tickers)
#     scores = [calculate_score(ticker) for ticker in tickers]
#     value_ranking = sorted(
#         scores, key=lambda x: x["value_score"], reverse=True)[:20]
#     growth_ranking = sorted(
#         scores, key=lambda x: x["growth_score"], reverse=True)[:20]

#     value_ranking_df = pd.DataFrame(
#         [{"ticker": stock["ticker"], "Value Score": stock["value_score"]} for stock in value_ranking])
#     growth_ranking_df = pd.DataFrame(
#         [{"ticker": stock["ticker"], "Growth Score": stock["growth_score"]} for stock in growth_ranking])

#     st.subheader("Top 20 Value Stocks")
#     st.dataframe(value_ranking_df)
#     st.subheader("Top 20 Growth Stocks")
#     st.dataframe(growth_ranking_df)
