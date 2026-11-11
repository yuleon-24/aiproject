
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re
import math

# ==========================================
# 1. 페이지 기본 설정
# ==========================================

st.set_page_config(
    page_title="서울시 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 서울시 연령별 인구 분석")
st.write("행정구역, 연도, 성별에 따른 인구 분포를 분석합니다.")

# ==========================================
# 2. CSV 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    # app.py와 같은 폴더에서 CSV 찾기
    file_path = Path(__file__).resolve().parent / "population.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"population.csv 파일을 찾을 수 없습니다.\n"
            f"파일 위치: {file_path}"
        )

    # 한글 인코딩 자동 확인
    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    data = None
    used_encoding = None

    for encoding in encodings:
        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )
            used_encoding = encoding
            break

        except UnicodeDecodeError:
            continue

    if data is None:
        raise ValueError("CSV 파일의 인코딩을 확인해주세요.")

    # 열 이름 정리
    data.columns = [
        str(col).replace("\ufeff", "").strip()
        for col in data.columns
    ]

    # 인구수 숫자 변환
    for col in data.columns:
        if col != "행정구역":

            data[col] = pd.to_numeric(
                data[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip(),
                errors="coerce"
            )

    return data, used_encoding


try:
    df, encoding = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# ==========================================
# 3. 연도 자동 추출
# ==========================================

years = set()

for column in df.columns:

    match = re.match(
        r"^(\d{4})년_",
        str(column).strip()
    )

    if match:
        years.add(match.group(1))

years = sorted(years)

if not years:
    st.error("CSV 파일에서 연도를 찾을 수 없습니다.")
    st.stop()


# ==========================================
# 4. 행정구역 설정
# ==========================================

if "행정구역" not in df.columns:
    st.error("행정구역 열을 찾을 수 없습니다.")
    st.stop()

# 괄호 안의 행정구역 코드 제거
df["행정구역명"] = (
    df["행정구역"]
    .astype(str)
    .str.split("(")
    .str[0]
    .str.strip()
)

regions = df["행정구역명"].dropna().unique().tolist()

if not regions:
    st.error("행정구역 데이터가 없습니다.")
    st.stop()


# ==========================================
# 5. 연령대 설정
# ==========================================

ages = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]


# ==========================================
# 6. 분석 조건 선택
# ==========================================

st.divider()

st.subheader("🔍 분석 조건 선택")

col1, col2, col3 = st.columns(3)

with col1:
    selected_region = st.selectbox(
        "행정구역",
        regions
    )

with col2:
    selected_year = st.selectbox(
        "연도",
        years,
        index=len(years) - 1,
        format_func=lambda x: f"{x}년"
    )

with col3:
    selected_gender = st.selectbox(
        "성별",
        ["전체", "남성", "여성"]
    )


# ==========================================
# 7. 성별에 따른 데이터 선택
# ==========================================

gender_columns = {
    "전체": "거주자",
    "남성": "남_거주자",
    "여성": "여_거주자"
}

gender_prefix = gender_columns[selected_gender]


# ==========================================
# 8. 선택한 행정구역 데이터 가져오기
# ==========================================

selected_data = df[
    df["행정구역명"] == selected_region
]

if selected_data.empty:
    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

selected_data = selected_data.iloc[0]


# ==========================================
# 9. 연령대별 인구 추출
# ==========================================

population_values = []
missing_columns = []

for age in ages:

    column_name = (
        f"{selected_year}년_"
        f"{gender_prefix}_{age}"
    )

    if column_name not in df.columns:

        missing_columns.append(column_name)
        population_values.append(0)

    else:

        value = selected_data[column_name]

        if pd.isna(value):
            value = 0

        population_values.append(int(value))


# 데이터 누락 확인
if missing_columns:

    st.error(
        "일부 연령대 데이터를 찾을 수 없습니다.\n"
        + ", ".join(missing_columns)
    )
    st.stop()


# ==========================================
# 10. 분석 데이터 생성
# ==========================================

chart_df = pd.DataFrame({
    "나이": ages,
    "인구수": population_values
})

total_population = chart_df["인구수"].sum()

if total_population <= 0:
    st.warning("선택한 조건에 인구 데이터가 없습니다.")
    st.stop()


# ==========================================
# 11. 주요 분석 정보
# ==========================================

st.divider()

st.subheader("📌 분석 결과")

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric(
        "행정구역",
        selected_region
    )

with metric2:
    st.metric(
        "연도",
        f"{selected_year}년"
    )

with metric3:
    st.metric(
        "총인구수",
        f"{total_population:,}명"
    )


# ==========================================
# 12. 세로축 눈금 간격 계산
# ==========================================

def calculate_tick_interval(max_value):

    if max_value <= 0:
        return 1000

    raw_step = max_value / 6

    magnitude = 10 ** math.floor(
        math.log10(raw_step)
    )

    for multiplier in [1, 2, 5, 10]:

        step = multiplier * magnitude

        if step >= raw_step:
            return step

    return magnitude * 10


max_population = chart_df["인구수"].max()

tick_interval = calculate_tick_interval(
    max_population
)


# ==========================================
# 13. 그래프 생성
# ==========================================

st.divider()

st.subheader("📈 연령대별 인구 분포")

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=chart_df["나이"],
        y=chart_df["인구수"],

        name="인구수",

        marker_color="#2E8B57",

        text=[
            f"{value:,}"
            for value in chart_df["인구수"]
        ],

        textposition="outside",

        hovertemplate=(
            "나이: %{x}<br>"
            "인구수: %{y:,}명"
            "<extra></extra>"
        )
    )
)


# ==========================================
# 14. 그래프 디자인
# ==========================================

fig.update_layout(

    height=550,

    plot_bgcolor="white",

    paper_bgcolor="white",

    font=dict(
        family="sans-serif",
        size=13,
        color="#222222"
    ),

    xaxis=dict(
        title="나이",
        type="category",
        categoryorder="array",
        categoryarray=ages,
        showgrid=False
    ),

    yaxis=dict(
        title="인구수 (명)",

        showgrid=True,

        gridcolor="#C8D8CC",

        gridwidth=1,

        tickmode="linear",

        tick0=0,

        dtick=tick_interval,

        tickformat=",",

        rangemode="tozero",

        zeroline=True,

        zerolinecolor="#888888"
    ),

    bargap=0.25,

    showlegend=False,

    margin=dict(
        l=80,
        r=40,
        t=50,
        b=70
    )
)

# 세로축 최대 범위
fig.update_yaxes(
    range=[
        0,
        max_population * 1.2
    ]
)

# 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 15. 상세 데이터 표
# ==========================================

with st.expander("📋 연령대별 상세 인구 데이터"):

    display_df = chart_df.copy()

    display_df["인구수"] = display_df[
        "인구수"
    ].apply(lambda x: f"{x:,}명")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 16. CSV 다운로드
# ==========================================

csv_data = chart_df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="📥 분석 결과 CSV 다운로드",

    data=csv_data,

    file_name=(
        f"{selected_region}_"
        f"{selected_year}_"
        f"{selected_gender}_인구분석.csv"
    ),

    mime="text/csv"
)


# ==========================================
# 17. 데이터 정보
# ==========================================

with st.expander("⚙️ 데이터 정보"):

    st.write(f"파일 인코딩: {encoding}")

    st.write(f"데이터 크기: {df.shape}")

    st.write(f"분석 가능 연도: {', '.join(years)}")

    st.write(f"행정구역 개수: {len(regions)}")

    st.write("사용 데이터: population.csv")


# ==========================================
# 18. 마무리
# ==========================================

st.divider()

st.caption(
    "서울시 연령별 인구 분석 프로그램"
)
