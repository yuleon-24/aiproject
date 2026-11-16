
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from pathlib import Path

# -----------------------------------------
# 1. 페이지 설정
# -----------------------------------------
st.set_page_config(
    page_title="행정구역별 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 행정구역별 연령 인구 분석")
st.write("행정구역, 연도, 성별을 선택하여 연령대별 인구수를 확인하세요.")

# -----------------------------------------
# 2. CSV 파일 불러오기
# -----------------------------------------
@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더 경로
    BASE_DIR = Path(__file__).resolve().parent.parent

    # CSV 파일 경로
    CSV_PATH = BASE_DIR / "population.csv"

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"population.csv 파일을 찾을 수 없습니다.\n"
            f"파일 위치: {CSV_PATH}"
        )

    # 한글 인코딩 대응
    encodings = ["euc-kr", "cp949", "utf-8-sig", "utf-8"]

    data = None

    for encoding in encodings:
        try:
            data = pd.read_csv(
                CSV_PATH,
                encoding=encoding
            )
            break
        except UnicodeDecodeError:
            continue

    if data is None:
        raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")

    # 컬럼명 공백 제거
    data.columns = data.columns.astype(str).str.strip()

    # 행정구역 컬럼 확인
    if "행정구역" not in data.columns:
        raise ValueError("'행정구역' 컬럼이 없습니다.")

    return data


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# -----------------------------------------
# 3. 연도 및 성별 선택을 위한 컬럼 분석
# -----------------------------------------

# 인구 데이터 컬럼 분석
pattern = re.compile(
    r"(?P<year>20\d{2})년_(?P<gender>남|여)_거주자_(?P<age>.+)"
)

records = []

for col in df.columns:

    match = pattern.fullmatch(col)

    if match:
        records.append({
            "컬럼": col,
            "연도": int(match.group("year")),
            "성별": match.group("gender"),
            "나이": match.group("age")
        })

if not records:
    st.error(
        "인구 데이터 컬럼을 찾을 수 없습니다. "
        "CSV의 컬럼명이 예상한 형식인지 확인해 주세요."
    )
    st.stop()

column_info = pd.DataFrame(records)

years = sorted(column_info["연도"].unique())
districts = sorted(
    df["행정구역"].dropna().astype(str).unique()
)

# -----------------------------------------
# 4. 사용자 선택
# -----------------------------------------

st.subheader("🔎 분석 조건 선택")

col1, col2, col3 = st.columns(3)

with col1:
    selected_district = st.selectbox(
        "행정구역 선택",
        districts
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
        ["남성", "여성"]
    )

gender_code = {
    "남성": "남",
    "여성": "여"
}

# -----------------------------------------
# 5. 선택 조건에 맞는 데이터 추출
# -----------------------------------------

selected_columns = column_info[
    (column_info["연도"] == selected_year) &
    (column_info["성별"] == gender_code[selected_gender])
].copy()

if selected_columns.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

# 선택한 행정구역 데이터
district_data = df[
    df["행정구역"].astype(str) == selected_district
]

if district_data.empty:
    st.warning("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

# 해당 행정구역의 한 행 추출
row = district_data.iloc[0]

# -----------------------------------------
# 6. 연령대별 인구 데이터 정리
# -----------------------------------------

age_data = []

for _, item in selected_columns.iterrows():

    age = item["나이"]
    column = item["컬럼"]

    population = pd.to_numeric(
        str(row[column]).replace(",", "").strip(),
        errors="coerce"
    )

    if pd.notna(population):

        # 연령대 숫자 추출
        numbers = re.findall(r"\d+", age)

        if numbers:
            age_order = int(numbers[0])
        else:
            age_order = 999

        age_data.append({
            "나이": age,
            "인구수": int(population),
            "정렬": age_order
        })

result = pd.DataFrame(age_data)

if result.empty:
    st.warning("표시할 인구 데이터가 없습니다.")
    st.stop()

result = result.sort_values("정렬")

# -----------------------------------------
# 7. 선택 조건 표시
# -----------------------------------------

st.divider()

st.subheader("📌 분석 결과")

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric("행정구역", selected_district)

with metric2:
    st.metric("분석 연도", f"{selected_year}년")

with metric3:
    st.metric("선택 성별", selected_gender)

# -----------------------------------------
# 8. 꺾은선 그래프
# -----------------------------------------

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=result["나이"],
        y=result["인구수"],
        mode="lines+markers",
        name="인구수",
        line=dict(
            color="green",
            width=3
        ),
        marker=dict(
            size=8,
            color="green"
        ),
        hovertemplate=
        "연령대: %{x}<br>" +
        "인구수: %{y:,.0f}명" +
        "<extra></extra>"
    )
)

fig.update_layout(
    title={
        "text": f"{selected_district} {selected_year}년 {selected_gender} 연령별 인구",
        "x": 0.5,
        "xanchor": "center"
    },

    xaxis_title="나이",
    yaxis_title="인구수 (명)",

    font=dict(
        family="Malgun Gothic, AppleGothic, sans-serif",
        size=13
    ),

    template="plotly_white",

    height=550,

    hovermode="x unified",

    showlegend=True
)

# 세로축 가로 구분선
fig.update_yaxes(
    showgrid=True,
    gridcolor="lightgray",
    separatethousands=True,
    rangemode="tozero"
)

# 가로축 설정
fig.update_xaxes(
    showgrid=True,
    gridcolor="lightgray",
    tickangle=0
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------------------
# 9. 데이터 표 출력
# -----------------------------------------

with st.expander("📋 연령대별 인구 데이터 확인"):

    display_data = result[["나이", "인구수"]].copy()

    display_data["인구수"] = display_data["인구수"].map(
        lambda x: f"{x:,}명"
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

# -----------------------------------------
# 10. 자료 안내
# -----------------------------------------

st.divider()

st.caption(
    "자료 출처: population.csv | "
    "분석 도구: Python Pandas 및 Plotly"
)
