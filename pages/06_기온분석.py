
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ----------------------------------
# 1. 페이지 설정
# ----------------------------------
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하여 연도별 최고기온과 최저기온을 비교해 보세요.")

# ----------------------------------
# 2. CSV 파일 불러오기
# ----------------------------------
@st.cache_data
def load_data():

    # 한글 인코딩 대응
    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]

    for encoding in encodings:
        try:
            data = pd.read_csv(
                "temperature.csv",
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("CSV 파일 인코딩을 확인해 주세요.")

    # 필요한 컬럼 확인
    required_columns = [
        "일시",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"'{col}' 컬럼이 없습니다.")

    # 날짜 데이터 분리
    date_parts = data["일시"].str.split("-", expand=True)

    # 월 이름을 숫자로 변환
    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    data["월"] = date_parts[0].map(month_dict)

    # 연도 변환
    # 07~99는 1900년대, 00~26은 2000년대로 처리
    yy = pd.to_numeric(date_parts[1], errors="coerce")

    data["연도"] = yy.apply(
        lambda x: 1900 + int(x) if x >= 7
        else 2000 + int(x)
    )

    # 기온 데이터 숫자형 변환
    data["최고기온(℃)"] = pd.to_numeric(
        data["최고기온(℃)"], errors="coerce"
    )

    data["최저기온(℃)"] = pd.to_numeric(
        data["최저기온(℃)"], errors="coerce"
    )

    data = data.dropna(
        subset=["월", "연도", "최고기온(℃)", "최저기온(℃)"]
    )

    data["연도"] = data["연도"].astype(int)

    return data.sort_values("연도")


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# ----------------------------------
# 3. 월 선택
# ----------------------------------
month_names = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월"
}

selected_month = st.selectbox(
    "📅 분석할 월을 선택하세요.",
    options=list(month_names.keys()),
    format_func=lambda x: month_names[x]
)


# ----------------------------------
# 4. 선택한 월의 데이터 추출
# ----------------------------------
month_data = df[df["월"] == selected_month].copy()

month_data = month_data.sort_values("연도")


# ----------------------------------
# 5. 꺾은선 그래프 생성
# ----------------------------------
fig = go.Figure()

# 최고기온 (빨간색)
fig.add_trace(
    go.Scatter(
        x=month_data["연도"],
        y=month_data["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(
            color="red",
            width=2
        ),
        marker=dict(size=6)
    )
)

# 최저기온 (파란색)
fig.add_trace(
    go.Scatter(
        x=month_data["연도"],
        y=month_data["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(
            color="blue",
            width=2
        ),
        marker=dict(size=6)
    )
)

# 그래프 제목 및 축 설정
fig.update_layout(
    title={
        "text": "월별 기온분석",
        "x": 0.5,
        "xanchor": "center"
    },

    xaxis_title="연도",
    yaxis_title="온도(℃)",

    legend=dict(
        title="범례",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),

    font=dict(
        family="Malgun Gothic, AppleGothic, sans-serif",
        size=13
    ),

    hovermode="x unified",

    template="plotly_white",

    height=550
)

fig.update_xaxes(
    showgrid=True,
    dtick=10
)

fig.update_yaxes(
    showgrid=True
)


# ----------------------------------
# 6. 그래프 출력
# ----------------------------------
st.plotly_chart(
    fig,
    use_container_width=True
)


# ----------------------------------
# 7. 데이터 확인
# ----------------------------------
with st.expander("선택한 월의 기온 데이터 확인"):

    st.dataframe(
        month_data[
            ["연도", "최고기온(℃)", "최저기온(℃)"]
        ].reset_index(drop=True),
        use_container_width=True
    )

st.caption("※ 자료 출처: temperature.csv")
