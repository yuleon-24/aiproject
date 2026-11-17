
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pathlib import Path

# -----------------------------------
# 1. 기본 페이지 설정
# -----------------------------------

st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 예측")
st.write("선형회귀 알고리즘을 이용하여 과거 기온을 분석하고 미래 기온을 예측합니다.")

# -----------------------------------
# 2. CSV 파일 불러오기
# -----------------------------------

@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent

    # temperature.csv 파일 위치 탐색
    possible_paths = [
        base_dir / "temperature.csv",
        base_dir.parent / "temperature.csv",
        base_dir.parent.parent / "temperature.csv"
    ]

    file_path = next(
        (p for p in possible_paths if p.exists()),
        None
    )

    if file_path is None:
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다."
        )

    # 한글 CSV 인코딩 처리
    for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            data = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("CSV 파일 인코딩을 확인해주세요.")

    data.columns = data.columns.str.strip()

    # 날짜 데이터 변환
    data["일시"] = pd.to_datetime(
        data["일시"],
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
        subset=["연도", "월", "평균기온(℃)"]
    )

    data["연도"] = data["연도"].astype(int)
    data["월"] = data["월"].astype(int)

    return data


try:
    df = load_data()
    st.success("기온 데이터가 정상적으로 불러와졌습니다.")

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# -----------------------------------
# 3. 사용자 입력
# -----------------------------------

st.subheader("📅 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "분석할 월을 선택하세요.",
        list(range(1, 13)),
        format_func=lambda x: f"{x}월"
    )

with col2:
    selected_year = st.number_input(
        "예측할 연도를 입력하세요.",
        min_value=2007,
        max_value=2100,
        value=2027,
        step=1
    )

selected_year = int(selected_year)

# -----------------------------------
# 4. 선택한 월의 데이터 추출
# -----------------------------------

monthly_data = df[
    df["월"] == selected_month
].copy()

monthly_data = monthly_data.sort_values("연도")

if len(monthly_data) < 2:
    st.error("선택한 월의 데이터가 부족합니다.")
    st.stop()

X = monthly_data[["연도"]]
y = monthly_data["평균기온(℃)"]

# -----------------------------------
# 5. 선형회귀 알고리즘 학습
# -----------------------------------

model = LinearRegression()

model.fit(X, y)

# 예측 기온 계산
prediction = model.predict(
    pd.DataFrame({"연도": [selected_year]})
)[0]

# 회귀선 계산
min_year = int(monthly_data["연도"].min())
max_year = max(
    int(monthly_data["연도"].max()),
    selected_year
)

line_years = np.linspace(
    min_year,
    max_year,
    200
)

line_predictions = model.predict(
    pd.DataFrame({"연도": line_years})
)

# 회귀식 정보
slope = model.coef_[0]
intercept = model.intercept_
r2 = model.score(X, y)

# -----------------------------------
# 6. 예측 결과 출력
# -----------------------------------

st.divider()
st.subheader("📊 기온 예측 결과")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "예측 연도",
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
        f"{r2:.3f}"
    )

# -----------------------------------
# 7. 그래프 시각화
# -----------------------------------

st.subheader("📈 과거 기온 및 미래 기온 예측 그래프")

fig = go.Figure()

# 실제 기온 데이터
fig.add_trace(
    go.Scatter(
        x=monthly_data["연도"],
        y=monthly_data["평균기온(℃)"],
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            size=9,
            color="royalblue"
        ),
        hovertemplate=
        "%{x}년<br>실제 평균기온: %{y:.2f}℃<extra></extra>"
    )
)

# 선형회귀 추세선
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=line_predictions,
        mode="lines",
        name="선형회귀 예측선",
        line=dict(
            color="red",
            width=3
        ),
        hovertemplate=
        "연도: %{x:.1f}<br>회귀 예측: %{y:.2f}℃<extra></extra>"
    )
)

# 예측 지점
fig.add_trace(
    go.Scatter(
        x=[selected_year],
        y=[prediction],
        mode="markers",
        name="최종 예측기온",
        marker=dict(
            size=16,
            color="orange",
            symbol="star",
            line=dict(width=2, color="black")
        ),
        hovertemplate=
        "%{x}년<br>예측 평균기온: %{y:.2f}℃<extra></extra>"
    )
)

# 실제 기온과 회귀선의 차이(잔차) 표시
residual_x = []
residual_y = []

for _, row in monthly_data.iterrows():
    year = row["연도"]
    actual = row["평균기온(℃)"]

    fitted = model.predict(
        pd.DataFrame({"연도": [year]})
    )[0]

    residual_x.extend([year, year, None])
    residual_y.extend([actual, fitted, None])

fig.add_trace(
    go.Scatter(
        x=residual_x,
        y=residual_y,
        mode="lines",
        name="예측 오차(잔차)",
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
    title=f"{selected_month}월 평균기온 선형회귀 분석",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="closest",
    template="plotly_white",
    height=600,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    )
)

fig.update_xaxes(
    dtick=1
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------------
# 8. 선형회귀 알고리즘 분석 결과
# -----------------------------------

st.subheader("🔍 선형회귀 분석 정보")

col1, col2 = st.columns(2)

with col1:
    st.write("**선형회귀 방정식**")
    st.latex(
        rf"\hat{{y}} = {slope:.4f}x + {intercept:.2f}"
    )

    st.write(f"기울기: {slope:.4f}")
    st.write(f"절편: {intercept:.2f}")

with col2:
    st.write("**모델 분석 결과**")

    if slope > 0:
        st.write("📈 장기적으로 기온이 상승하는 추세입니다.")
    elif slope < 0:
        st.write("📉 장기적으로 기온이 하락하는 추세입니다.")
    else:
        st.write("➡️ 장기적인 기온 변화가 거의 없습니다.")

    st.write(f"사용한 실제 데이터: {len(monthly_data)}개")
    st.write(f"분석 기간: {min_year}년 ~ {monthly_data['연도'].max()}년")

# -----------------------------------
# 9. 실제 데이터 표
# -----------------------------------

with st.expander("📋 분석에 사용된 실제 기온 데이터 확인"):

    display_data = monthly_data[
        ["연도", "평균기온(℃)"]
    ].copy()

    display_data.columns = [
        "연도",
        "실제 평균기온(℃)"
    ]

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

# -----------------------------------
# 10. 선형회귀 알고리즘 설명
# -----------------------------------

st.divider()

st.subheader("📚 선형회귀 알고리즘이란?")

st.markdown("""
선형회귀는 여러 데이터 사이의 관계를 분석하여
가장 적합한 직선을 찾고, 그 직선을 이용해 미래의 값을 예측하는 알고리즘입니다.

**① 실제 데이터 수집**

과거 여러 해의 같은 월 평균기온을 수집합니다.

**② 가장 적합한 직선 찾기**

수집한 데이터 점들과 직선 사이의 오차가 전체적으로
가장 작아지도록 직선을 계산합니다.

**③ 기울기와 절편 계산**

직선의 기울기는 시간이 지남에 따라 기온이 얼마나
변하는지를 나타내며, 절편은 직선의 시작 위치를 결정합니다.

**④ 미래 기온 예측**

사용자가 입력한 연도를 직선의 방정식에 대입하여
해당 연도의 예상 평균기온을 계산합니다.
""")

st.latex(r"\hat{y} = b_0 + b_1x")

st.markdown("""
- **x** : 연도
- **ŷ** : 예측 평균기온
- **b₀** : 절편
- **b₁** : 기울기

### 그래프 읽는 방법

- 🔵 파란 점: 실제로 관측된 과거 평균기온
- 🔴 빨간 선: 선형회귀 알고리즘이 계산한 추세선
- 🟠 주황색 별: 사용자가 선택한 연도의 예측기온
- 회색 점선: 실제 기온과 회귀선 사이의 오차

**핵심:** 실제 데이터가 직선 주변에 얼마나 가까이 분포하는지,
그리고 회귀선이 어떤 방향으로 기울어져 있는지를 보면
알고리즘이 과거의 기온 변화를 어떻게 학습했는지 알 수 있습니다.

※ 이 프로그램은 과거의 같은 월 기온 변화 추세를 이용한 예측입니다.
실제 미래 기온은 기후 변화, 이상기후 및 다양한 환경 요인에 따라 달라질 수 있습니다.
""")

st.caption("기온 데이터 분석 및 예측 프로그램 | Linear Regression")
