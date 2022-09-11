import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('国内自動車企業の株価可視化アプリ')

# サイドバーの設定：日数と株価の指定範囲
st.sidebar.write("""
# GAFA株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("""
## 表示日数選択
""")

days = st.sidebar.slider('日数', 1, 365, 180)

# **〇〇** 太字に設定
# f｛変数名} 数字を代入コメントで表示
st.write(f"""
### 過去 **{days}日間** の日本自動車メーカー株価            
""")


@st.cache
def get_data(days, tickers):                            # get_data 数字と会社情報（名称、企業名コード)
    df = pd.DataFrame()                                 # DataFrame の母体
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])               # 企業の情報取得で企業名コードの入力
        hist = tkr.history(period=f'{days}d')           # 何日分の取得をするのか？
        hist.index = hist.index.strftime('%d %B %Y')    # 日付形式の入れ替え
        hist = hist[['Close']] 
        hist.columns = [company] 
        hist = hist.T                                   # 縦・横の入れ替え
        hist.index.name = 'Name'
        df = pd.concat([df, hist])                      # 接続
    return df


try:                                                    # 何かerrorが起きたらコメント発生させる。
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider(                     # 株価表示用の範囲を指定する
        '範囲を指定してください。',
        0.0, 6000.0, (0.0, 6000.0)
    )

    tickers = {                                         # 企業名、企業名コードの格納
        'TOYOTA'   : '7203.T',
        'HONDA'    : '7267.T',
        'Mazda'    : '7261.T',
        'NISSAN'   : '7201.T',
        'MITSUBISHI': '7211.T',
        'SUZUKI'   : '7269.T',    
        'YAMAHA'   : '7272.T',            
    }

    df = get_data(days, tickers)
    companies = st.multiselect(                         # 選択・検索ツール？    〇〇業界の指定ができれば面白そう!
        '会社名を選択してください。',
        list(df.index),
        ['TOYOTA', 'HONDA','Mazda','NISSAN','MITSUBISHI','SUZUKI','YAMAHA' ]
    )

    if not companies:
        st.error('少なくとも一社は選んでください。')
    else:
        data = df.loc[companies]                         # df内の指定したcompanyのデータのみ取得する
        st.write("### 株価 (円)", data.sort_index())
        data = data.T.reset_index()                      # データの縦・横の入れ替え＆データ表示用で加工する。reset(初期条件の数字が読み込めない？)
        data = pd.melt(data, id_vars=['Date']).rename(   # DATA変換 date,appleの株価、faceの株価, ⇒　date, apple(facebook), apple(facebook)の株価にする。　３⇒２ 
            columns={'value': 'Stock Prices(円)'}        # 名前の変換をしている
        )

        # st.dataframe(data)

        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)           # 指定：clip=true はみ出したものを消す
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(円):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)

    selected_firm = st.selectbox(
    '詳細表示する企業を選択：',
    ['TOYOTA', 'HONDA','Mazda','NISSAN','MITSUBISHI','SUZUKI','YAMAHA' ]
    )
    ticker = tickers[selected_firm]
    data2 = yf.download(ticker, period  = "6mo", interval = "1d")
    df2 = data2

    price = df2["Close"]
    span = 5
    df2["sma05"] = price.rolling(window=span).mean()
    df2["sma05"] = price.rolling(window=span, min_periods=1).mean()
    st.dataframe(df2)

    df2.index = df2.index.strftime('%d %B %Y')    # 日付形式の入れ替え
    data3 = df2[['Close','sma05']]
    data3.columns = ['終始値','平均値']
    data3 = data3.T                                   # 縦・横の入れ替え
    df3   = data3.T.reset_index()
    df3   = pd.melt(df3, id_vars=['Date']).rename(   # DATA変換 date,appleの株価、faceの株価, ⇒　date, apple(facebook), apple(facebook)の株価にする。　３⇒２ 
            columns={'value': 'Stock Prices(円)'}        # 名前の変換をしている
    )

    # st.dataframe(df3)   
    st.subheader(f'{selected_firm}の株価グラフ')

    chart2 = (
            alt.Chart(df3)
            .mark_line(opacity=0.8, clip=True)           # 指定：clip=true はみ出したものを消す
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(円):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
    )
    st.altair_chart(chart2, use_container_width=True)

except:
    st.error(
        "おっと！なにかエラーが起きているようです。"
    )

