
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------
# 1. 기본 설정
# --------------------------------

st.set_page_config(
    page_title="세계 국가별 MBTI 통계",
    page_icon="🌍",
    layout="wide"
)

MBTI_TYPES = [
    "INFJ", "ISFJ", "INTP", "ISFP",
    "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP",
    "ESTP", "ISTJ", "ENFJ", "ESFJ"
]


# --------------------------------
# 2. 디자인 설정
# --------------------------------

st.markdown("""
<style>
.main-title {
    font-size: 2.25rem;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 0.2rem;
}
.sub-title {
    color: #8b949e;
    margin-bottom: 1.5rem;
}
div[data-testid="stMetric"] {
    background: rgba(128, 128, 128, 0.08);
    border: 1px solid rgba(128, 128, 128, 0.18);
    padding: 16px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------
# 3. CSV 데이터 불러오기
# --------------------------------

@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더에서 CSV 찾기
    csv_path = (
        Path(__file__).resolve().parent.parent
        / "countriesMBTI_16types.csv"
    )

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다: {csv_path}"
        )

    data = pd.read_csv(csv_path)

    # 필요한 열 확인
    missing_columns = [
        col for col in ["Country"] + MBTI_TYPES
        if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"CSV에 필요한 열이 없습니다: {missing_columns}"
        )

    data["Country"] = (
        data["Country"].astype(str).str.strip()
    )

    # 숫자 데이터 변환
    for col in MBTI_TYPES:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    # 결측값 제거
    data = data.dropna(
        subset=["Country"] + MBTI_TYPES
    )

    return data


# --------------------------------
# 4. 메인 화면
# --------------------------------

st.markdown(
    '<div class="main-title">'
    '🌍 세계 국가별 MBTI 통계'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '158개 국가의 MBTI 16가지 유형별 비율을 비교해 보세요.'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------
# 5. 데이터 오류 처리
# --------------------------------

try:

    df = load_data()

except Exception as error:

    st.error(
        f"데이터를 불러오지 못했습니다: {error}"
    )

    st.info(
        "CSV 파일이 프로젝트 최상위 폴더에 있는지 확인하세요."
    )

    st.stop()


# --------------------------------
# 6. 국가 선택
# --------------------------------

country_list = sorted(
    df["Country"].unique().tolist()
)

left, right = st.columns([2, 1])

with left:

    selected_country = st.selectbox(
        "국가 선택",
        country_list,
        index=(
            country_list.index("South Korea")
            if "South Korea" in country_list
            else 0
        )
    )

with right:

    sort_order = st.radio(
        "그래프 정렬",
        ["높은 비율순", "MBTI 유형순"],
        horizontal=True
    )


# --------------------------------
# 7. 선택 국가 데이터 추출
# --------------------------------

selected_row = df.loc[
    df["Country"] == selected_country
].iloc[0]

chart_data = pd.DataFrame({

    "MBTI": MBTI_TYPES,

    "비율": [
        float(selected_row[mbti]) * 100
        for mbti in MBTI_TYPES
    ]

})


# --------------------------------
# 8. 그래프 정렬
# --------------------------------

if sort_order == "높은 비율순":

    chart_data = chart_data.sort_values(
        "비율",
        ascending=False
    ).reset_index(drop=True)

else:

    chart_data = chart_data.sort_values(
        "MBTI"
    ).reset_index(drop=True)


# --------------------------------
# 9. 그래프 색상 설정
# --------------------------------

# 비율이 가장 높은 MBTI 찾기
ranked = chart_data.sort_values(
    "비율",
    ascending=False
).reset_index(drop=True)

# 1위 빨간색
color_by_mbti = {
    ranked.loc[0, "MBTI"]: "#EF4444"
}

# 나머지 파란색 그라데이션
blue_palette = [
    "#2563EB",
    "#3B82F6",
    "#4F8DF7",
    "#6398F8",
    "#77A5F9",
    "#8BB2FA",
    "#9FBFFC",
    "#B3CCFC",
    "#C1D5FD",
    "#C9DAFD",
    "#D1DFFD",
    "#D9E5FE",
    "#DDE8FE",
    "#E2ECFE",
    "#E7EFFE"
]

for rank, row in ranked.iloc[1:].iterrows():

    color_by_mbti[row["MBTI"]] = blue_palette[
        min(rank - 1, len(blue_palette) - 1)
    ]

chart_data["색상"] = chart_data["MBTI"].map(
    color_by_mbti
)


# --------------------------------
# 10. 통계 정보
# --------------------------------

top_mbti = ranked.iloc[0]["MBTI"]

top_percent = ranked.iloc[0]["비율"]

average_percent = chart_data["비율"].mean()

metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    "선택 국가",
    selected_country
)

metric2.metric(
    "가장 높은 유형",
    top_mbti,
    f"{top_percent:.2f}%"
)

metric3.metric(
    "16개 유형 평균",
    f"{average_percent:.2f}%"
)


# --------------------------------
# 11. MBTI 그래프 생성
# --------------------------------

st.subheader(
    f"{selected_country}의 MBTI 비율"
)

fig = go.Figure()

fig.add_trace(
    go.Bar(

        x=chart_data["비율"],

        y=chart_data["MBTI"],

        orientation="h",

        marker=dict(
            color=chart_data["색상"],
            line=dict(
                color="rgba(255,255,255,0.35)",
                width=0.6
            )
        ),

        text=[
            f"{value:.2f}%"
            for value in chart_data["비율"]
        ],

        textposition="outside",

        cliponaxis=False,

        hovertemplate=
        "<b>%{y}</b><br>"
        "비율: %{x:.2f}%"
        "<extra></extra>"

    )
)


# --------------------------------
# 12. 그래프 디자인
# --------------------------------

fig.update_layout(

    height=620,

    template="plotly_white",

    xaxis=dict(
        title="비율 (%)",
        rangemode="tozero",
        showgrid=True,
        gridcolor="rgba(120,120,120,0.18)"
    ),

    yaxis=dict(
        title="MBTI 유형",
        autorange=(
            "reversed"
            if sort_order == "높은 비율순"
            else True
        )
    ),

    margin=dict(
        l=35,
        r=75,
        t=20,
        b=45
    ),

    showlegend=False,

    font=dict(size=13)

)


# --------------------------------
# 13. 그래프 출력
# --------------------------------

st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------
# 14. 상세 데이터 표
# --------------------------------

with st.expander(
    "선택한 국가의 상세 데이터 보기"
):

    display_data = chart_data[
        ["MBTI", "비율"]
    ].copy()

    display_data["비율"] = display_data[
        "비율"
    ].map(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------
# 15. 하단 안내
# --------------------------------

st.caption(
    "참고: 수치는 제공된 CSV 데이터의 비율을 "
    "백분율로 변환한 값입니다. "
    "실제 국가 전체 인구의 MBTI 분포와 다를 수 있습니다."
)
