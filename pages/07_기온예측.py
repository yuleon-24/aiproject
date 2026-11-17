
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="월별 평균기온 분석 및 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 예측")

st.markdown("""
과거의 월별 평균기온 데이터를 이용하여
세 가지 회귀 알고리즘으로 미래 기온을 예측하고 비교합니다.
""")

st.divider()


# ==========================================
# 2. CSV 파일 불러오기
# ==========================================

@st.cache_data
def load_data():

    base_dir = Path(__file__).resolve().parent

    possible_paths = [
        base_dir / "temperature.csv",
        base_dir.parent / "temperature.csv",
        base_dir.parent.parent / "temperature.csv"
    ]

    file_path = next(
        (p for p in possible_paths if p.is_file()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다."
        )

    data = None

    for encoding in [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]:

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
            "CSV 파일의 인코딩을 확인해주세요."
        )

    data.columns = data.columns.astype(str).str.strip()

    required_columns = [
        "일시",
        "평균기온(℃)"
    ]

    for column in required_columns:

        if column not in data.columns:
            raise ValueError(
                f"'{column}' 열을 찾을 수 없습니다."
            )

    data["일시"] = pd.to_datetime(
        data["일시"].astype(str).str.strip(),
        format="%b-%y",
        errors="coerce"
    )

    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"],
        errors="coerce"
    )

    data["연도"] = data["일시"].dt.year
    data["월"] = data["일시"].dt.month

    data = data.dropna(
        subset=[
            "연도",
            "월",
            "평균기온(℃)"
        ]
    ).copy()

    data["연도"] = data["연도"].astype(int)
    data["월"] = data["월"].astype(int)

    data = data.sort_values(
        ["연도", "월"]
    ).reset_index(drop=True)

    return data


try:

    df = load_data()

except Exception as e:

    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# ==========================================
# 3. 실제 데이터 기간 제한
# ==========================================

LAST_ACTUAL_YEAR = 2025

df = df[
    df["연도"] <= LAST_ACTUAL_YEAR
].copy()

if df.empty:

    st.error("2025년까지의 기온 데이터가 없습니다.")
    st.stop()

st.success(
    f"데이터 불러오기 완료 | "
    f"실제 데이터: {df['연도'].min()}년 ~ 2025년"
)

st.caption(
    "2026년 이후의 CSV 데이터는 학습과 실제 관측 그래프에서 제외합니다."
)


# ==========================================
# 4. 사용자 입력
# ==========================================

st.subheader("⚙️ 분석 조건 선택")

col1, col2 = st.columns(2)

with col1:

    selected_month = st.selectbox(
        "분석할 월",
        options=list(range(1, 13)),
        format_func=lambda x: f"{x}월"
    )

with col2:

    selected_year = st.number_input(
        "예측할 연도",
        min_value=2026,
        max_value=2100,
        value=2027,
        step=1
    )

selected_year = int(selected_year)


# ==========================================
# 5. 알고리즘 선택
# ==========================================

st.subheader("🧠 회귀 알고리즘 선택")

algorithm_names = [
    "선형회귀 (Linear Regression)",
    "다항회귀 (Polynomial Regression)",
    "랜덤 포레스트 회귀 (Random Forest)"
]

selected_algorithm = st.selectbox(
    "사용할 알고리즘을 선택하세요.",
    algorithm_names
)

st.caption(
    "선택한 알고리즘은 그래프에서 굵은 선으로 강조됩니다. "
    "나머지 두 알고리즘도 함께 표시하여 비교할 수 있습니다."
)


# ==========================================
# 6. 월별 데이터 추출
# ==========================================

monthly_data = df[
    df["월"] == selected_month
].copy()

monthly_data = monthly_data.sort_values("연도")

if len(monthly_data) < 3:

    st.error("분석에 사용할 데이터가 부족합니다.")
    st.stop()

X = monthly_data[["연도"]]
y = monthly_data["평균기온(℃)"]

min_year = int(monthly_data["연도"].min())
last_year = int(monthly_data["연도"].max())


# ==========================================
# 7. 세 가지 회귀 모델 생성
# ==========================================

models = {

    "선형회귀 (Linear Regression)": (
        LinearRegression()
    ),

    "다항회귀 (Polynomial Regression)": (
        make_pipeline(
            PolynomialFeatures(
                degree=2,
                include_bias=False
            ),
            LinearRegression()
        )
    ),

    "랜덤 포레스트 회귀 (Random Forest)": (
        RandomForestRegressor(
            n_estimators=300,
            max_depth=4,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
    )
}


# ==========================================
# 8. 세 가지 알고리즘 학습 및 예측
# ==========================================

results = {}

for name, model in models.items():

    # 모델 학습
    model.fit(X, y)

    # 과거 데이터에 대한 예측
    historical_predictions = model.predict(X)

    # 미래 연도 예측
    future_prediction = model.predict(
        pd.DataFrame({
            "연도": [selected_year]
        })
    )[0]

    # 모델 성능 계산
    mae = mean_absolute_error(
        y,
        historical_predictions
    )

    r2 = r2_score(
        y,
        historical_predictions
    )

    results[name] = {

        "model": model,

        "historical": historical_predictions,

        "prediction": float(future_prediction),

        "mae": float(mae),

        "r2": float(r2)
    }


# ==========================================
# 9. 선택된 알고리즘 결과
# ==========================================

selected_result = results[selected_algorithm]

prediction = selected_result["prediction"]

st.divider()

st.subheader("🔮 선택한 알고리즘의 예측 결과")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "예측 대상",
        f"{selected_year}년 {selected_month}월"
    )

with col2:

    st.metric(
        "예측 평균기온",
        f"{prediction:.2f} ℃"
    )

with col3:

    st.metric(
        "결정계수 (R²)",
        f"{selected_result['r2']:.3f}"
    )


# ==========================================
# 10. 그래프에 사용할 연도 생성
# ==========================================

historical_years = np.linspace(
    min_year,
    last_year,
    200
)

future_years = np.linspace(
    last_year,
    selected_year,
    150
)

historical_X = pd.DataFrame({
    "연도": historical_years
})

future_X = pd.DataFrame({
    "연도": future_years
})


# ==========================================
# 11. 세 가지 알고리즘 비교 그래프
# ==========================================

st.divider()

st.subheader("📈 세 가지 알고리즘 예측 비교")

st.markdown(
    f"**분석 대상: {selected_month}월 | "
    f"예측 연도: {selected_year}년**"
)

fig = go.Figure()

# 실제 기온 데이터
fig.add_trace(
    go.Scatter(
        x=monthly_data["연도"],
        y=monthly_data["평균기온(℃)"],
        mode="lines+markers",
        name="실제 평균기온",
        line=dict(
            color="royalblue",
            width=2
        ),
        marker=dict(size=7),
        hovertemplate=
        "%{x}년<br>실제 기온: %{y:.2f}℃<extra></extra>"
    )
)


# 알고리즘별 색상
colors = {
    "선형회귀 (Linear Regression)": "#E74C3C",
    "다항회귀 (Polynomial Regression)": "#16A085",
    "랜덤 포레스트 회귀 (Random Forest)": "#8E44AD"
}


# 알고리즘별 회귀선
for name, result in results.items():

    model = result["model"]

    color = colors[name]

    is_selected = name == selected_algorithm

    line_width = 4 if is_selected else 2

    opacity = 1.0 if is_selected else 0.45

    # 과거 학습 구간
    historical_values = model.predict(
        historical_X
    )

    fig.add_trace(
        go.Scatter(
            x=historical_years,
            y=historical_values,
            mode="lines",
            name=f"{name} - 과거 추세",
            line=dict(
                color=color,
                width=line_width
            ),
            opacity=opacity,
            hovertemplate=
            "%{x:.1f}년<br>"
            "모델 계산 기온: %{y:.2f}℃<extra></extra>"
        )
    )

    # 미래 예측 구간
    future_values = model.predict(
        future_X
    )

    fig.add_trace(
        go.Scatter(
            x=future_years,
            y=future_values,
            mode="lines",
            name=f"{name} - 미래 예측",
            line=dict(
                color=color,
                width=line_width,
                dash="dash"
            ),
            opacity=opacity,
            hovertemplate=
            "%{x:.1f}년<br>"
            "미래 예측: %{y:.2f}℃<extra></extra>"
        )
    )

    # 미래 예측 지점
    fig.add_trace(
        go.Scatter(
            x=[selected_year],
            y=[result["prediction"]],
            mode="markers",
            name=f"{name} - 최종 예측",
            marker=dict(
                color=color,
                size=15 if is_selected else 9,
                symbol="star" if is_selected else "circle",
                line=dict(
                    color="white",
                    width=1
                )
            ),
            opacity=opacity,
            hovertemplate=
            "%{x}년<br>"
            "예측 평균기온: %{y:.2f}℃<extra></extra>"
        )
    )


# 2025년 실제 데이터 종료 기준선
fig.add_vline(
    x=LAST_ACTUAL_YEAR,
    line_width=2,
    line_dash="dot",
    line_color="gray",
    annotation_text="실제 데이터 종료 (2025년)",
    annotation_position="top left"
)


# 선택한 알고리즘의 잔차 표시
residual_x = []
residual_y = []

for _, row in monthly_data.iterrows():

    year = int(row["연도"])

    actual = float(row["평균기온(℃)"])

    fitted = float(
        selected_result["model"].predict(
            pd.DataFrame({
                "연도": [year]
            })
        )[0]
    )

    residual_x.extend([
        year,
        year,
        None
    ])

    residual_y.extend([
        actual,
        fitted,
        None
    ])


fig.add_trace(
    go.Scatter(
        x=residual_x,
        y=residual_y,
        mode="lines",
        name="선택 모델의 예측 오차",
        line=dict(
            color="gray",
            width=1,
            dash="dot"
        ),
        hoverinfo="skip"
    )
)


# 그래프 디자인
fig.update_layout(

    title=dict(
        text=f"{selected_month}월 평균기온 회귀 알고리즘 비교",
        x=0.5
    ),

    xaxis_title="연도",

    yaxis_title="평균기온 (℃)",

    template="plotly_white",

    height=700,

    hovermode="closest",

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),

    margin=dict(
        l=50,
        r=30,
        t=110,
        b=60
    )
)

fig.update_xaxes(
    range=[
        min_year - 0.5,
        selected_year + 0.5
    ],
    dtick=(
        1 if selected_year <= 2040
        else 5 if selected_year <= 2070
        else 10
    ),
    showgrid=True
)

fig.update_yaxes(
    showgrid=True,
    zeroline=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 12. 알고리즘별 예측 결과 한눈에 비교
# ==========================================

st.divider()

st.subheader("📊 세 가지 알고리즘 예측 결과 비교")

comparison_data = []

for name, result in results.items():

    comparison_data.append({

        "알고리즘": name,

        "예측 평균기온(℃)": round(
            result["prediction"], 2
        ),

        "평균 절대 오차(MAE)": round(
            result["mae"], 3
        ),

        "결정계수(R²)": round(
            result["r2"], 3
        ),

        "선택 여부": (
            "⭐ 선택됨"
            if name == selected_algorithm
            else ""
        )
    })


comparison_df = pd.DataFrame(comparison_data)

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)


# 알고리즘별 예측 기온 막대그래프
bar_fig = go.Figure()

bar_colors = [
    colors[name]
    for name in algorithm_names
]

bar_fig.add_trace(
    go.Bar(
        x=[
            results[name]["prediction"]
            for name in algorithm_names
        ],
        y=[
            "선형회귀",
            "다항회귀",
            "랜덤 포레스트"
        ],
        orientation="h",
        marker_color=bar_colors,
        text=[
            f"{results[name]['prediction']:.2f}℃"
            for name in algorithm_names
        ],
        textposition="outside"
    )
)

bar_fig.update_layout(
    title=f"{selected_year}년 {selected_month}월 알고리즘별 예측기온",
    xaxis_title="예측 평균기온 (℃)",
    yaxis_title="알고리즘",
    template="plotly_white",
    height=350
)

st.plotly_chart(
    bar_fig,
    use_container_width=True
)


# ==========================================
# 13. 알고리즘별 상세 설명
# ==========================================

st.divider()

st.subheader("🧠 선택한 회귀 알고리즘 알아보기")

if selected_algorithm == algorithm_names[0]:

    st.markdown("""
    ### ① 선형회귀 (Linear Regression)

    과거 데이터의 전체적인 변화 추세를 하나의 직선으로 표현하는 방법입니다.

    - 데이터의 상승 및 하락 추세를 파악합니다.
    - 기울기를 이용하여 연간 기온 변화량을 계산합니다.
    - 단순하고 해석하기 쉽다는 장점이 있습니다.

    **수학적 표현**
    """)

    st.latex(
        r"\hat{y} = b_0 + b_1x"
    )

    st.info(
        "기울기가 양수이면 상승 추세, "
        "음수이면 하락 추세를 의미합니다."
    )


elif selected_algorithm == algorithm_names[1]:

    st.markdown("""
    ### ② 다항회귀 (Polynomial Regression)

    직선이 아닌 곡선으로 데이터의 변화 추세를 표현하는 방법입니다.

    이번 프로그램에서는 2차 다항회귀를 사용합니다.

    - 기온 변화가 일정한 직선 형태가 아닐 때 활용할 수 있습니다.
    - 상승과 하락이 포함된 곡선 형태를 학습합니다.
    - 예측 연도가 멀어지면 곡선이 지나치게 커지거나 작아질 수 있습니다.

    **수학적 표현**
    """)

    st.latex(
        r"\hat{y} = b_0 + b_1x + b_2x^2"
    )

    st.info(
        "x² 항을 추가하여 직선보다 다양한 곡선 형태를 표현합니다."
    )


elif selected_algorithm == algorithm_names[2]:

    st.markdown("""
    ### ③ 랜덤 포레스트 회귀 (Random Forest Regression)

    여러 개의 의사결정나무를 만들고, 각 나무의 예측 결과를 평균 내어 최종 값을 계산하는 방법입니다.

    - 여러 의사결정나무의 결과를 결합합니다.
    - 데이터의 복잡한 관계를 학습할 수 있습니다.
    - 단일 직선이나 곡선에 의존하지 않습니다.
    - 과거 데이터 범위를 벗어난 미래 연도에서는 새로운 추세를 외삽하지 못하는 한계가 있습니다.

    **수학적 표현**
    """)

    st.latex(
        r"\hat{y} = \frac{1}{N}\sum_{i=1}^{N}T_i(x)"
    )

    st.info(
        "여러 의사결정나무가 각각 계산한 예측값을 평균하여 결과를 만듭니다."
    )


# ==========================================
# 14. 세 알고리즘의 차이점
# ==========================================

st.divider()

st.subheader("📖 세 가지 알고리즘 비교")

difference_data = pd.DataFrame({

    "구분": [
        "예측 방식",
        "그래프 형태",
        "장점",
        "주의할 점"
    ],

    "선형회귀": [
        "하나의 직선",
        "직선",
        "단순하고 해석하기 쉬움",
        "복잡한 변화 표현이 어려움"
    ],

    "다항회귀": [
        "다항식",
        "곡선",
        "비선형 추세 표현",
        "미래에 곡선이 과도하게 변할 수 있음"
    ],

    "랜덤 포레스트": [
        "여러 결정트리의 평균",
        "계단형 변화",
        "복잡한 데이터 관계 학습",
        "학습 범위 밖의 외삽에 취약함"
    ]
})

st.dataframe(
    difference_data,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 15. 데이터 및 모델 성능 확인
# ==========================================

st.divider()

with st.expander("📋 분석에 사용된 실제 기온 데이터"):

    display_data = monthly_data[
        ["연도", "월", "평균기온(℃)"]
    ].copy()

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


with st.expander("📚 모델 성능 지표 알아보기"):

    st.markdown("""
    **결정계수 (R²)**

    모델이 학습에 사용한 과거 기온 데이터의 변화를 얼마나 설명하는지 나타냅니다.

    일반적으로 1에 가까울수록 학습 데이터에 대한 설명력이 높습니다.

    **평균 절대 오차 (MAE)**

    실제 기온과 모델이 예측한 기온의 차이를 절댓값으로 계산한 평균입니다.

    값이 작을수록 학습 데이터에서 발생한 평균 오차가 작습니다.

    ※ 여기 표시되는 R²와 MAE는 학습에 사용한 데이터에 대한 평가입니다.
    미래 예측의 정확도를 보장하는 수치는 아닙니다.
    """)


# ==========================================
# 16. 선형회귀와 머신러닝 설명
# ==========================================

st.divider()

st.subheader("📚 회귀 알고리즘이란?")

st.markdown("""
회귀 알고리즘은 과거에 수집된 데이터를 학습하여
새로운 숫자 값을 예측하는 머신러닝 방법입니다.

이번 프로그램에서는 과거의 같은 월 평균기온을 학습하여
미래의 평균기온을 계산합니다.

**알고리즘 작동 과정**

1. 과거 기온 데이터를 수집합니다.
2. 선택한 회귀 알고리즘이 데이터의 특징을 학습합니다.
3. 학습한 모델에 미래 연도를 입력합니다.
4. 모델이 해당 연도의 예상 평균기온을 계산합니다.

**이번 프로그램의 특징**

같은 기온 데이터를 사용하더라도 알고리즘에 따라
예측 결과가 다르게 나타날 수 있습니다.

이는 각각의 알고리즘이 데이터를 학습하고
변화 추세를 표현하는 방법이 서로 다르기 때문입니다.
""")

st.warning("""
주의: 이 프로그램은 과거 기온 데이터만 이용한 통계적 예측입니다.
실제 기온은 기후 변화, 이상기후 등 다양한 요인의 영향을 받으므로
예측값을 실제 기상예보와 동일하게 해석해서는 안 됩니다.
""")

st.divider()

st.caption(
    "월별 평균기온 분석 및 예측 프로그램 | "
    "Streamlit · Pandas · NumPy · Scikit-learn · Plotly"
)
