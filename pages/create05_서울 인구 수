
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
st.caption("행정구역, 연도, 성별에 따른 인구 분포 분석")

# ==========================================
# 2. CSV 파일 불러오기
# ==========================================

@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더 경로
    base_dir = Path(__file__).resolve().parent.parent

    # 상위 폴더에 있는 CSV 파일
    file_path = base_dir / "population.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다: {file_path}"
        )

    # 한글 인코딩 자동 처리
    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    data = None

    for encoding in encodings:
        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break

        except UnicodeDecodeError:
            continue

    if data is None:
        raise ValueError(
            "CSV 인코딩을 확인해주세요."
        )

    # 인구수 쉼표 제거 및 숫자 변환
    for col in data.columns[1:]:
        data[col] = pd.to_numeric(
            data[col].astype(str).str.replace(
                ",", "", regex=False
            ),
            errors="coerce"
        )

    return data


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# ==========================================
# 3. 데이터 설정
# ==========================================

# 행정구역 이름 정리
df["구역명"] = (
    df["행정구역"]
    .astype(str)
    .str.split("(")
    .str[0]
    .str.strip()
)

# 연도 추출
years = sorted(
    set(
        re.findall(
            r"(\d{4})년_",
            " ".join(df.columns)
        )
    )
)

if not years:
    st.error("연도 데이터를 찾을 수 없습니다.")
    st.stop()

# 연령대
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
# 4. 분석 조건 선택
# ==========================================

st.subheader("🔍 분석 조건 선택")

col1, col2, col3 = st.columns(3)

with col1:
    regions = df["구역명"].dropna().unique().tolist()

    selected_region = st.selectbox(
        "행정구역 선택",
        regions,
        index=0
    )

with col2:
    selected_year = st.selectbox(
        "연도 선택",
        years,
        index=len(years) - 1
    )

with col3:
    selected_gender = st.selectbox(
        "성별 선택",
        ["전체", "남성", "여성"]
    )

# ==========================================
# 5. 선택한 데이터 추출
# ==========================================

region_data = df[
    df["구역명"] == selected_region
]

if region_data.empty:
    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

region_data = region_data.iloc[0]

# 성별에 따른 컬럼 접두사
if selected_gender == "전체":
    gender_prefix = "거주자"
elif selected_gender == "남성":
    gender_prefix = "남_거주자"
else:
    gender_prefix = "여_거주자"

# 연령대별 인구 추출
population_values = []

for age in age_columns:

    column_name = (
        f"{selected_year}년_"
        f"{gender_prefix}_{age}"
    )

    if column_name in df.columns:
        value = region_data[column_name]
    else:
        value = 0

    population_values.append(
        0 if pd.isna(value) else int(value)
    )

chart_df = pd.DataFrame({
    "연령대": age_columns,
    "인구수": population_values
})

# ==========================================
# 6. 주요 정보 표시
# ==========================================

total_population = chart_df["인구수"].sum()

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
        "분석 연도",
        f"{selected_year}년"
    )

with metric3:
    st.metric(
        "선택 조건의 총인구",
        f"{total_population:,}명"
    )

# ==========================================
# 7. 세로축 눈금 간격 계산
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
# 8. 그래프 생성
# ==========================================

st.subheader("📈 연령대별 인구 분포")

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=chart_df["연령대"],
        y=chart_df["인구수"],
        name="인구수",
        marker_color="#2E8B57",
        text=chart_df["인구수"].apply(
            lambda x: f"{x:,}"
        ),
        textposition="outside",
        hovertemplate=(
            "연령대: %{x}<br>"
            "인구수: %{y:,}명"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    height=550,
    plot_bgcolor="white",
    paper_bgcolor="white",

    font=dict(
        family="Arial, Malgun Gothic, sans-serif",
        size=13,
        color="#222222"
    ),

    xaxis=dict(
        title="나이",
        type="category",
        showgrid=False,
        tickangle=0
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
        zerolinecolor="#888888"
    ),

    bargap=0.25,
    showlegend=False,

    margin=dict(
        l=70,
        r=30,
        t=40,
        b=70
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================
# 9. 상세 데이터 확인
# ==========================================

with st.expander("📋 연령대별 상세 인구 데이터"):

    display_df = chart_df.copy()

    display_df["인구수"] = display_df[
        "인구수"
    ].map(lambda x: f"{x:,}명")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# 10. CSV 다운로드
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
# 11. 마무리
# ==========================================

st.divider()

st.caption(
    "서울시 인구 통계 자료를 활용한 연령대별 인구 분석 프로그램"
)
