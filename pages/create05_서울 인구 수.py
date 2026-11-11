
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="서울시 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 서울시 연령별 인구 분석")
st.write("행정구역, 연도, 성별에 따른 연령별 인구 분포를 분석합니다.")

# ==========================================
# 2. CSV 파일 불러오기
# ==========================================

@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더
    base_dir = Path(__file__).resolve().parent.parent

    # CSV 파일 경로
    file_path = base_dir / "population.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"population.csv 파일을 찾을 수 없습니다.\n{file_path}"
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
        raise ValueError("CSV 파일의 인코딩을 읽을 수 없습니다.")

    # 열 이름 공백 제거
    data.columns = data.columns.astype(str).str.strip()

    # 숫자 데이터 변환
    for col in data.columns:
        if col != "행정구역":
            data[col] = pd.to_numeric(
                data[col].astype(str).str.replace(
                    ",", "", regex=False
                ).str.strip(),
                errors="coerce"
            )

    return data, used_encoding


try:
    df, used_encoding = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# ==========================================
# 3. 실제 CSV 열 이름에서 연도 추출
# ==========================================

years = []

for column in df.columns:

    match = re.match(
        r"^(\d{4})년_",
        str(column).strip()
    )

    if match:
        year = match.group(1)

        if year not in years:
            years.append(year)

# 연도 정렬
years = sorted(years)

if len(years) == 0:
    st.error(
        "연도를 찾을 수 없습니다. "
        "CSV의 첫 번째 행과 열 이름을 확인해주세요."
    )

    st.write("실제 CSV 열 이름:")
    st.write(df.columns.tolist())

    st.stop()


# ==========================================
# 4. 행정구역 데이터 정리
# ==========================================

if "행정구역" not in df.columns:
    st.error("'행정구역' 열이 CSV에 없습니다.")
    st.stop()

# 괄호 뒤의 행정구역 코드 제거
df["구역명"] = (
    df["행정구역"]
    .astype(str)
    .str.split("(")
    .str[0]
    .str.strip()
)

# 빈 행정구역 제거
df = df[
    df["구역명"].notna() &
    (df["구역명"] != "")
].copy()

regions = df["구역명"].tolist()


# ==========================================
# 5. 연령대 설정
# ==========================================

age_columns = [
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
        regions,
        index=0
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
# 7. 선택한 데이터 추출
# ==========================================

region_data = df[
    df["구역명"] == selected_region
]

if region_data.empty:
    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

region_data = region_data.iloc[0]

# 성별에 따른 열 이름
gender_prefix = {
    "전체": "거주자",
    "남성": "남_거주자",
    "여성": "여_거주자"
}

prefix = gender_prefix[selected_gender]

population_values = []

for age in age_columns:

    column_name = (
        f"{selected_year}년_"
        f"{prefix}_{age}"
    )

    # 실제 데이터 열이 있는지 확인
    if column_name in df.columns:

        value = region_data[column_name]

        if pd.isna(value):
            value = 0

    else:
        value = 0

    population_values.append(int(value))


# ==========================================
# 8. 그래프용 데이터 생성
# ==========================================

chart_df = pd.DataFrame({
    "연령대": age_columns,
    "인구수": population_values
})

total_population = chart_df["인구수"].sum()

# 데이터가 없는 경우
if total_population == 0:

    st.warning(
        "선택한 조건에 해당하는 인구 데이터가 없습니다."
    )

    st.stop()


# ==========================================
# 9. 주요 분석 정보
# ==========================================

st.divider()

st.subheader("📌 분석 결과")

metric1, metric2, metric3 = st.columns(3)

with metric1:

    st.metric(
        label="행정구역",
        value=selected_region
    )

with metric2:

    st.metric(
        label="분석 연도",
        value=f"{selected_year}년"
    )

with metric3:

    st.metric(
        label="총인구수",
        value=f"{total_population:,}명"
    )


# ==========================================
# 10. 세로축 눈금 간격 계산
# ==========================================

def calculate_tick_interval(max_value):

    if max_value <= 0:
        return 1000

    raw_step = max_value / 6

    magnitude = 10 ** (
        len(str(int(raw_step))) - 1
    )

    for multiplier in [1, 2, 5, 10]:

        step = multiplier * magnitude

        if step >= raw_step:
            return step

    return magnitude * 10


tick_interval = calculate_tick_interval(
    chart_df["인구수"].max()
)


# ==========================================
# 11. 그래프 생성
# ==========================================

st.divider()

st.subheader("📈 연령대별 인구 분포")

fig = go.Figure()

fig.add_trace(
    go.Bar(

        x=chart_df["연령대"],

        y=chart_df["인구수"],

        name="인구수",

        marker=dict(
            color="#2E8B57"
        ),

        text=[
            f"{value:,}"
            for value in chart_df["인구수"]
        ],

        textposition="outside",

        hovertemplate=
        "연령대: %{x}<br>" +
        "인구수: %{y:,}명" +
        "<extra></extra>"
    )
)


# 그래프 디자인
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

        showgrid=False,

        categoryorder="array",

        categoryarray=age_columns
    ),

    yaxis=dict(

        title="인구수 (명)",

        showgrid=True,

        gridcolor="#D9E5DC",

        gridwidth=1,

        tickmode="linear",

        tick0=0,

        dtick=tick_interval,

        tickformat=",",

        rangemode="tozero",

        zeroline=True,

        zerolinecolor="#888888",

        zerolinewidth=1
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


# 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 12. 상세 데이터 표
# ==========================================

with st.expander("📋 연령대별 상세 인구 데이터"):

    display_df = chart_df.copy()

    display_df["인구수"] = display_df[
        "인구수"
    ].apply(
        lambda x: f"{x:,}명"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 13. CSV 다운로드
# ==========================================

csv_data = chart_df.to_csv(
    index=False,
    encoding="utf-8-sig"
)

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
# 14. 데이터 정보
# ==========================================

with st.expander("데이터 정보"):

    st.write(f"파일 인코딩: {used_encoding}")

    st.write(f"전체 데이터 크기: {df.shape}")

    st.write(f"분석 가능한 연도: {', '.join(years)}")

    st.write(f"행정구역 개수: {len(regions)}")

    st.write(f"CSV 파일 경로: {Path(__file__).resolve().parent.parent / 'population.csv'}")


st.divider()

st.caption(
    "서울시 인구 통계 데이터를 활용한 연령대별 인구 분석 프로그램"
)
