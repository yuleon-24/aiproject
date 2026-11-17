
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="월별 평균기온 분석 및 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 예측")
st.write(
    "과거 기온 데이터를 바탕으로 선형회귀 알고리즘을 학습하고 "
    "미래의 월별 평균기온을 예측하는 프로그램입니다."
)

st.divider()


# ==========================================
# 2. CSV 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    # 현재 app.py가 위치한 폴더
    base_dir = Path(__file__).resolve().parent

    # temperature.csv 파일 위치 탐색
    possible_paths = [
        base_dir / "temperature.csv",
        base_dir.parent / "temperature.csv",
        base_dir.parent.parent / "temperature.csv"
    ]

    file_path = next(
        (path for path in possible_paths if path.is_file()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다. "
            "app.py와 같은 폴더에 CSV 파일을 넣어주세요."
        )

    # CSV 인코딩 자동 확인
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
        raise ValueError("CSV 파일의 인코딩을 읽을 수 없습니다.")

    # 열 이름 공백 제거
    data.columns = data.columns.astype(str).str.strip()

    # 필요한 열 확인
    required_columns = [
        "일시",
        "평균기온(℃)"
    ]

    for column in required_columns:
        if column not in data.columns:
            raise ValueError(
                f"CSV 파일에 '{column}' 열이 없습니다."
            )

    # 날짜 변환
    data["일시"] = pd.to_datetime(
        data["일시"].astype(str).str.strip(),
        format="%b-%y",
        errors="coerce"
    )

    # 평균기온 숫자 변환
    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"],
        errors="coerce"
    )

    # 연도와 월 추출
    data["연도"] = data["일시"].dt.year
    data["월"] = data["일시"].dt.month

    # 결측치 제거
    data = data.dropna(
        subset=[
            "연도",
            "월",
            "평균기온(℃)"
        ]
    ).copy()

    data["연도"] = data["연도"].astype(int)
    data["월"] = data["월"].astype(int)

    # 데이터 정렬
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

# 2025년까지만 실제 데이터로 사용
LAST_ACTUAL_YEAR = 2025

df = df[
    df["연도"] <= LAST_ACTUAL_YEAR
].copy()

if df.empty:
    st.error("2025년까지의 기온 데이터가 없습니다.")
    st.stop()

st.success(
    f"기온 데이터 불러오기 완료 | "
    f"실제 분석 기간: {df['연도'].min()}년 ~ {LAST_ACTUAL_YEAR}년"
)

st.caption(
    "※ CSV에 포함된 2026년 데이터는 요청에 따라 분석에서 제외했습니다."
)


# ==========================================
# 4. 사용자 입력
# ==========================================

st.subheader("📅 분석 조건 선택")

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
# 5. 선택한 월의 데이터 추출
# ==========================================

monthly_data = df[
    df["월"] == selected_month
].copy()

monthly_data = monthly_data.sort_values("연도")

if len(monthly_data) < 2:
    st.error("선택한 월의 데이터가 2개 이상 필요합니다.")
    st.stop()

# 실제 관측 연도와 평균기온
X = monthly_data[["연도"]]
y = monthly_data["평균기온(℃)"]

min_year = int(monthly_data["연도"].min())
last_year = int(monthly_data["연도"].max())


# ==========================================
# 6. 선형회귀 알고리즘 학습
# ==========================================

model = LinearRegression()

# 과거 실제 데이터를 이용한 학습
model.fit(X, y)

# 예측 연도의 평균기온 계산
prediction = model.predict(
    pd.DataFrame({
        "연도": [selected_year]
    })
)[0]

# 과거 실제 데이터에 대한 회귀선 예측
historical_fitted = model.predict(X)

# 기울기와 절편
slope = float(model.coef_[0])
intercept = float(model.intercept_)

# 결정계수
r2 = model.score(X, y)

# 평균 절대 오차
mae = float(
    np.mean(
        np.abs(y.to_numpy() - historical_fitted)
    )
)


# ==========================================
# 7. 그래프용 데이터 계산
# ==========================================

# 실제 데이터가 존재하는 기간의 회귀선
historical_line_years = np.linspace(
    min_year,
    last_year,
    200
)

historical_line_temps = model.predict(
    pd.DataFrame({
        "연도": historical_line_years
    })
)

# 2025년 이후 미래 예측선
future_line_years = np.linspace(
    last_year,
    selected_year,
    100
)

future_line_temps = model.predict(
    pd.DataFrame({
        "연도": future_line_years
    })
)


# ==========================================
# 8. 예측 결과 출력
# ==========================================

st.divider()

st.subheader("🔮 기온 예측 결과")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        label="예측 대상",
        value=f"{selected_year}년 {selected_month}월"
    )

with col2:

    st.metric(
        label="예측 평균기온",
        value=f"{prediction:.2f} ℃"
    )

with col3:

    st.metric(
        label="결정계수 (R²)",
        value=f"{r2:.3f}"
    )

if slope > 0:
    st.info(
        f"📈 과거 데이터를 분석한 결과, "
        f"평균기온이 연간 약 {slope:.3f}℃ 상승하는 추세입니다."
    )

elif slope < 0:
    st.info(
        f"📉 과거 데이터를 분석한 결과, "
        f"평균기온이 연간 약 {abs(slope):.3f}℃ 하락하는 추세입니다."
    )

else:
    st.info("➡️ 과거 기온의 장기적인 변화 추세가 거의 없습니다.")


# ==========================================
# 9. 그래프 시각화
# ==========================================

st.divider()

st.subheader(
    f"📈 {selected_month}월 평균기온 변화 및 예측 그래프"
)

fig = go.Figure()


# ------------------------------------------
# 실제 기온 데이터
# ------------------------------------------

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

        marker=dict(
            size=7
        ),

        hovertemplate=
        "%{x}년<br>"
        "실제 평균기온: %{y:.2f}℃"
        "<extra></extra>"
    )
)


# ------------------------------------------
# 과거 선형회귀 추세선
# ------------------------------------------

fig.add_trace(
    go.Scatter(
        x=historical_line_years,
        y=historical_line_temps,

        mode="lines",

        name="과거 선형회귀 추세선",

        line=dict(
            color="red",
            width=3
        ),

        hovertemplate=
        "%{x:.1f}년<br>"
        "회귀 예측: %{y:.2f}℃"
        "<extra></extra>"
    )
)


# ------------------------------------------
# 미래 예측 구간
# ------------------------------------------

fig.add_trace(
    go.Scatter(
        x=future_line_years,
        y=future_line_temps,

        mode="lines",

        name="미래 예측 구간",

        line=dict(
            color="orange",
            width=3,
            dash="dash"
        ),

        hovertemplate=
        "%{x:.1f}년<br>"
        "예측 기온: %{y:.2f}℃"
        "<extra></extra>"
    )
)


# ------------------------------------------
# 최종 예측 지점
# ------------------------------------------

fig.add_trace(
    go.Scatter(
        x=[selected_year],
        y=[prediction],

        mode="markers",

        name="최종 예측 평균기온",

        marker=dict(
            size=16,
            color="orange",
            symbol="star",
            line=dict(
                color="black",
                width=1
            )
        ),

        hovertemplate=
        "%{x}년<br>"
        "예측 평균기온: %{y:.2f}℃"
        "<extra></extra>"
    )
)


# ------------------------------------------
# 실제 기온과 회귀선의 차이
# 잔차(Residual) 시각화
# ------------------------------------------

residual_x = []
residual_y = []

for _, row in monthly_data.iterrows():

    year = int(row["연도"])
    actual_temp = float(row["평균기온(℃)"])

    fitted_temp = float(
        model.predict(
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
        actual_temp,
        fitted_temp,
        None
    ])


fig.add_trace(
    go.Scatter(
        x=residual_x,
        y=residual_y,

        mode="lines",

        name="예측 오차 (잔차)",

        line=dict(
            color="gray",
            width=1,
            dash="dot"
        ),

        hoverinfo="skip"
    )
)


# ------------------------------------------
# 2025년 기준선
# ------------------------------------------

fig.add_vline(
    x=LAST_ACTUAL_YEAR,
    line_width=2,
    line_dash="dot",
    line_color="gray",
    annotation_text="실제 데이터 마지막 연도 (2025)",
    annotation_position="top left"
)


# ------------------------------------------
# 그래프 디자인
# ------------------------------------------

fig.update_layout(

    title=dict(
        text=f"{selected_month}월 평균기온 선형회귀 분석",
        x=0.5
    ),

    xaxis_title="연도",

    yaxis_title="평균기온 (℃)",

    template="plotly_white",

    height=620,

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
        t=100,
        b=60
    )
)

fig.update_xaxes(
    range=[
        min_year - 0.5,
        max(selected_year, LAST_ACTUAL_YEAR) + 0.5
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
# 10. 그래프 범례 설명
# ==========================================

st.markdown("### 📌 그래프 읽는 방법")

legend_col1, legend_col2 = st.columns(2)

with legend_col1:

    st.markdown("""
    🔵 **파란색 선과 점**

    실제로 관측된 과거 평균기온

    🔴 **빨간색 실선**

    과거 데이터를 학습한 선형회귀 추세선

    ⚪ **회색 점선**

    실제 기온과 회귀선 사이의 차이인 잔차
    """)

with legend_col2:

    st.markdown("""
    🟠 **주황색 점선**

    2025년 이후의 미래 예측 구간

    ⭐ **주황색 별**

    사용자가 입력한 연도의 최종 예측기온

    │ **회색 세로 기준선**

    실제 데이터의 마지막 연도인 2025년
    """)


# ==========================================
# 11. 선형회귀 분석 정보
# ==========================================

st.divider()

st.subheader("🔍 선형회귀 분석 상세 정보")

col1, col2 = st.columns(2)

with col1:

    st.markdown("#### 선형회귀 방정식")

    st.latex(
        rf"\hat{{y}} = {slope:.4f}x + {intercept:.2f}"
    )

    st.write(f"기울기: {slope:.4f}")

    st.write(f"절편: {intercept:.2f}")

    st.write(
        f"예측 연도: {selected_year}년"
    )

    st.write(
        f"예측 평균기온: {prediction:.2f}℃"
    )


with col2:

    st.markdown("#### 모델 성능 및 데이터 정보")

    st.write(
        f"분석 시작 연도: {min_year}년"
    )

    st.write(
        f"실제 데이터 마지막 연도: {last_year}년"
    )

    st.write(
        f"학습에 사용한 데이터: {len(monthly_data)}개"
    )

    st.write(
        f"결정계수 (R²): {r2:.4f}"
    )

    st.write(
        f"평균 절대 오차 (MAE): {mae:.2f}℃"
    )


# ==========================================
# 12. 실제 데이터 확인
# ==========================================

st.divider()

with st.expander("📋 분석에 사용된 실제 기온 데이터 확인"):

    display_data = monthly_data[
        ["연도", "월", "평균기온(℃)"]
    ].copy()

    display_data.columns = [
        "연도",
        "월",
        "평균기온(℃)"
    ]

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 13. 선형회귀 알고리즘 설명
# ==========================================

st.divider()

st.subheader("📚 선형회귀 알고리즘이란?")

st.markdown("""
선형회귀는 여러 데이터 사이의 관계를 분석하여
가장 적합한 직선을 찾고, 그 직선을 이용하여
새로운 값을 예측하는 머신러닝 알고리즘입니다.

이 프로그램에서는 과거 같은 월의 평균기온을 분석하여
미래의 평균기온을 예측합니다.
""")

st.markdown("### ① 실제 데이터 수집")

st.write(
    "2007년부터 2025년까지 선택한 월의 평균기온을 수집합니다. "
    "예를 들어 3월을 선택하면 과거 모든 3월의 평균기온을 분석합니다."
)

st.markdown("### ② 가장 적합한 직선 찾기")

st.write(
    "수집한 실제 기온 데이터를 그래프의 점으로 표시하고, "
    "각 점과 직선 사이의 오차가 전체적으로 가장 작아지도록 "
    "알고리즘이 직선을 계산합니다."
)

st.markdown("### ③ 기울기와 절편 계산")

st.write(
    "기울기는 연도가 1년 증가할 때 평균기온이 얼마나 변하는지를 나타냅니다. "
    "절편은 회귀 직선의 위치를 결정합니다."
)

st.markdown("### ④ 미래 평균기온 예측")

st.write(
    "계산된 직선의 방정식에 사용자가 선택한 미래 연도를 대입하여 "
    "예상 평균기온을 계산합니다."
)

st.latex(
    r"\hat{y} = b_0 + b_1x"
)

st.markdown("""
| 기호 | 의미 |
|---|---|
| x | 연도 |
| ŷ | 예측 평균기온 |
| b₀ | 절편 |
| b₁ | 기울기 |

### ⑤ 예측 결과 해석

- 기울기가 양수이면 장기적으로 기온이 상승하는 추세입니다.
- 기울기가 음수이면 장기적으로 기온이 하락하는 추세입니다.
- 기울기가 0에 가까우면 장기적인 변화가 적다는 의미입니다.

**결정계수(R²)**는 회귀모델이 과거 데이터의 변화를 얼마나 설명하는지 나타내는 지표입니다. 일반적으로 1에 가까울수록 과거 데이터에 대한 설명력이 높습니다.

**평균 절대 오차(MAE)**는 실제 기온과 모델이 계산한 기온 사이의 평균적인 차이를 나타냅니다. 값이 작을수록 과거 데이터에 대한 예측 오차가 작습니다.
""")

st.warning(
    "주의: 선형회귀는 과거의 기온 변화 추세가 미래에도 이어진다고 가정합니다. "
    "실제 미래 기온은 기후 변화, 이상기후 등 다양한 요인에 따라 달라질 수 있습니다. "
    "따라서 이 결과는 실제 기상예보가 아닌 통계적 추정값입니다."
)

# ==========================================
# 14. 프로그램 하단
# ==========================================

st.divider()

st.caption(
    "월별 평균기온 분석 및 예측 프로그램 | "
    "Python · Pandas · NumPy · Scikit-learn · Plotly · Streamlit"
)
