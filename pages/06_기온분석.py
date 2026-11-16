
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ---------------------------------------
# 1. 페이지 설정
# ---------------------------------------
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하여 연도별 최고기온과 최저기온을 비교하세요.")

# ---------------------------------------
# 2. CSV 파일 불러오기
# ---------------------------------------
@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더
    base_dir = Path(__file__).resolve().parent.parent

    # CSV 파일 경로
    file_path = base_dir / "temperature.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"temperature.csv 파일을 찾을 수 없습니다.\n"
            f"파일 위치: {file_path}"
        )

    # 한글 인코딩 대응
    data = None

    for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue

    if data is None:
        raise ValueError("CSV 파일 인코딩을 확인해 주세요.")

    # 컬럼명 공백 제거
    data.columns = data.columns.str.strip()

    # 필요한 컬럼 확인
    required = [
        "일시",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in required:
        if col not in data.columns:
            raise ValueError(f"{col} 컬럼이 없습니다.")

    # 날짜 처리
    date_parts = data["일시"].astype(str).str.split("-", expand=True)

    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    data["월"] = date_parts[0].map(month_dict)

    # 연도 변환
    yy = pd.to_numeric(date_parts[1], errors="coerce")

    data["연도"] = yy.apply(
        lambda x: (
            1900 + int(x) if x >= 7
            else 2000 + int(x)
        ) if pd.notna(x) else None
    )

    # 기온 숫자 변환
    data["최고기온(℃)"] = pd.to_numeric(
        data["최고기온(℃)"],
        errors="coerce"
    )

    data["최저기온(℃)"] = pd.to_numeric(
        data["최저기온(℃)"],
        errors="coerce"
    )

    # 결측치 제거
    data = data.dropna(
        subset=[
            "월",
            "연도",
            "최고기온(℃)",
            "최저기온(℃)"
        ]
    )

    data["월"] = data["월"].astype(int)
    data["연도"] = data["연도"].astype(int)

    return data.sort_values("연도")


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# ---------------------------------------
# 3. 월 선택
# ---------------------------------------
st.subheader("📅 분석할 월 선택")

selected_month = st.selectbox(
    "월을 선택하세요.",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월"
)


# ---------------------------------------
# 4. 선택한 월의 데이터 추출
# ---------------------------------------
month_data = df[
    df["월"] == selected_month
].copy()

month_data = month_data.sort_values("연도")

if month_data.empty:
    st.warning("선택한 월의 데이터가 없습니다.")
    st.stop()


# ---------------------------------------
# 5. 그래프 생성
# ---------------------------------------
fig = go.Figure()

# 최고기온: 빨간색
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
        marker=dict(size=5)
    )
)

# 최저기온: 파란색
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
        marker=dict(size=5)
    )
)

# 그래프 제목 및 축
fig.update_layout(
    title=dict(
        text="월별 기온분석",
        x=0.5,
        xanchor="center"
    ),

    xaxis_title="연도",
    yaxis_title="온도(℃)",

    legend=dict(
        title="범례",
        orientation="h",
        y=1.1,
        x=0.5,
        xanchor="center"
    ),

    font=dict(
        family="Malgun Gothic, AppleGothic, sans-serif",
        size=13
    ),

    template="plotly_white",
    height=550,
    hovermode="x unified"
)

# 격자 표시
fig.update_xaxes(
    showgrid=True,
    dtick=10
)

fig.update_yaxes(
    showgrid=True,
    gridcolor="lightgray"
)


# ---------------------------------------
# 6. 그래프 출력
# ---------------------------------------
st.plotly_chart(
    fig,
    use_container_width=True
)


# ---------------------------------------
# 7. 데이터 확인
# ---------------------------------------
with st.expander("📋 선택한 월의 기온 데이터 확인"):

    st.dataframe(
        month_data[
            ["연도", "최고기온(℃)", "최저기온(℃)"]
        ].reset_index(drop=True),
        use_container_width=True
    )

# ---------------------------------------
# 8. 데이터 정보
# ---------------------------------------
st.divider()

st.caption(
    f"분석 월: {selected_month}월 | "
    f"분석 기간: {month_data['연도'].min()}~"
    f"{month_data['연도'].max()}년"
)

st.caption("자료 출처: temperature.csv")

