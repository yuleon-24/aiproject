import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)

# ==================================================
# 1. 페이지 설정 및 디자인
# ==================================================

st.set_page_config(
    page_title="Penguin AI Lab",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(
            180deg,
            #f4f8fc 0%,
            #ffffff 45%,
            #f0f7ff 100%
        );
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .hero {
        padding: 30px;
        border-radius: 24px;
        background: linear-gradient(
            120deg,
            #102a43 0%,
            #245b83 60%,
            #3c83a5 100%
        );
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(16,42,67,0.15);
    }

    .hero h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 8px;
    }

    .hero p {
        color: #dceaf5;
        font-size: 1.05rem;
    }

    .metric-card {
        background: white;
        border: 1px solid #e5edf5;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 14px rgba(16,42,67,0.05);
    }

    .metric-label {
        color: #64748b;
        font-size: 0.9rem;
    }

    .metric-value {
        color: #102a43;
        font-size: 1.7rem;
        font-weight: 700;
        margin-top: 6px;
    }

    .section-title {
        color: #102a43;
        font-size: 1.45rem;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5edf5;
        border-radius: 14px;
        padding: 16px;
    }

    div[data-testid="stSidebar"] {
        background-color: #edf4fa;
    }

    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
        min-height: 3rem;
    }
</style>
""", unsafe_allow_html=True)


# ==================================================
# 2. 상단 소개
# ==================================================

st.markdown("""
<div class="hero">
    <h1>🐧 Penguin AI Lab</h1>
    <p>
        실제 펭귄 데이터를 학습한 인공지능으로 품종을 예측하고
        두 가지 머신러닝 알고리즘의 결과를 비교합니다.
    </p>
</div>
""", unsafe_allow_html=True)


# ==================================================
# 3. 데이터 불러오기
# ==================================================

@st.cache_data
def load_data():
    data = pd.read_csv("penguins.csv")

    required_columns = [
        "species",
        "flipper_length_mm",
        "body_mass_g",
        "bill_length_mm",
        "bill_depth_mm"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"CSV 파일에 필요한 열이 없습니다: {missing_columns}"
        )

    data = data[required_columns].copy()

    data = data.dropna(
        subset=required_columns
    )

    return data


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "penguins.csv 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 CSV 파일을 넣어주세요."
    )
    st.stop()

except ValueError as e:
    st.error(str(e))
    st.stop()


# ==================================================
# 4. 데이터와 변수 설정
# ==================================================

FEATURES = [
    "flipper_length_mm",
    "body_mass_g",
    "bill_length_mm"
]

TARGET = "species"

X = df[FEATURES]
y = df[TARGET]

species_names = sorted(df[TARGET].unique())

species_korean = {
    "Adelie": "아델리펭귄",
    "Chinstrap": "턱끈펭귄",
    "Gentoo": "젠투펭귄"
}

# 실제 데이터 범위
flipper_min = int(df["flipper_length_mm"].min())
flipper_max = int(df["flipper_length_mm"].max())

mass_min = int(df["body_mass_g"].min())
mass_max = int(df["body_mass_g"].max())

bill_min = float(df["bill_length_mm"].min())
bill_max = float(df["bill_length_mm"].max())

depth_min = float(df["bill_depth_mm"].min())
depth_max = float(df["bill_depth_mm"].max())


# ==================================================
# 5. 학습 데이터와 테스트 데이터 분리
# ==================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ==================================================
# 6. 두 가지 분류 알고리즘
# ==================================================

@st.cache_resource
def train_models(X_train, X_test, y_train, y_test):

    models = {
        "랜덤 포레스트": RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            random_state=42,
            class_weight="balanced"
        ),

        "서포트 벡터 머신": make_pipeline(
            StandardScaler(),
            SVC(
                kernel="rbf",
                C=1.0,
                gamma="scale",
                probability=True,
                random_state=42,
                class_weight="balanced"
            )
        )
    }

    trained_models = {}
    results = {}

    for name, model in models.items():

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        accuracy = accuracy_score(
            y_test,
            predictions
        )

        trained_models[name] = model

        results[name] = {
            "accuracy": accuracy,
            "predictions": predictions,
            "confusion_matrix": confusion_matrix(
                y_test,
                predictions,
                labels=species_names
            ),
            "report": classification_report(
                y_test,
                predictions,
                labels=species_names,
                output_dict=True,
                zero_division=0
            )
        }

    return trained_models, results


with st.spinner("AI 모델을 학습하고 있습니다..."):

    models, model_results = train_models(
        X_train,
        X_test,
        y_train,
        y_test
    )


# ==================================================
# 7. 데이터 요약
# ==================================================

st.markdown(
    '<div class="section-title">📊 데이터 요약</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "전체 펭귄 데이터",
        f"{len(df):,}마리"
    )

with col2:
    st.metric(
        "학습 데이터",
        f"{len(X_train):,}마리"
    )

with col3:
    st.metric(
        "테스트 데이터",
        f"{len(X_test):,}마리"
    )

with col4:
    st.metric(
        "분류 품종",
        f"{len(species_names)}종"
    )

with st.expander("데이터 구성 및 품종별 개체 수"):

    st.write(
        "CSV 파일에서 필요한 측정값이 모두 존재하는 데이터를 사용합니다."
    )

    species_count = (
        df["species"]
        .value_counts()
        .rename_axis("품종")
        .reset_index(name="개체 수")
    )

    st.dataframe(
        species_count,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# 8. 사용자 입력
# ==================================================

st.markdown(
    '<div class="section-title">🧬 펭귄 신체 정보 입력</div>',
    unsafe_allow_html=True
)

st.info(
    f"""
    **입력 가능한 값의 범위**

    - 날개 길이: {flipper_min}~{flipper_max} mm
    - 몸무게: {mass_min:,}~{mass_max:,} g
    - 부리 길이: {bill_min:.1f}~{bill_max:.1f} mm
    - 부리 깊이: {depth_min:.1f}~{depth_max:.1f} mm

    범위는 업로드한 실제 데이터의 최솟값과 최댓값을 기준으로 합니다.
    """
)

with st.container(border=True):

    st.subheader("예측할 펭귄의 측정값")

    input_col1, input_col2 = st.columns(2)

    with input_col1:

        flipper_length = st.slider(
            "날개 길이 (mm)",
            min_value=flipper_min,
            max_value=flipper_max,
            value=int(df["flipper_length_mm"].median()),
            help="펭귄의 날개 길이를 입력합니다."
        )

        body_mass = st.slider(
            "몸무게 (g)",
            min_value=mass_min,
            max_value=mass_max,
            value=int(df["body_mass_g"].median()),
            step=100,
            help="펭귄의 몸무게를 입력합니다."
        )

    with input_col2:

        bill_length = st.slider(
            "부리 길이 (mm)",
            min_value=float(bill_min),
            max_value=float(bill_max),
            value=float(df["bill_length_mm"].median()),
            step=0.1,
            help="펭귄의 부리 길이를 입력합니다."
        )

        bill_depth = st.slider(
            "부리 깊이 (mm) · 그래프 표시용",
            min_value=float(depth_min),
            max_value=float(depth_max),
            value=float(df["bill_depth_mm"].median()),
            step=0.1,
            help="품종 예측에는 사용하지 않고 그래프에만 표시합니다."
        )

    st.caption(
        "부리 깊이는 그래프의 세로축에 사용됩니다. "
        "품종 예측에는 날개 길이, 몸무게, 부리 길이만 사용합니다."
    )


# ==================================================
# 9. 예측 실행
# ==================================================

st.markdown(
    '<div class="section-title">🔍 AI 품종 예측</div>',
    unsafe_allow_html=True
)

predict_button = st.button(
    "🐧 펭귄 품종 예측하기",
    type="primary",
    use_container_width=True
)

if predict_button:

    user_data = pd.DataFrame(
        [[
            flipper_length,
            body_mass,
            bill_length
        ]],
        columns=FEATURES
    )

    st.session_state["user_data"] = user_data
    st.session_state["bill_depth"] = bill_depth

    st.session_state["predictions"] = {
        name: model.predict(user_data)[0]
        for name, model in models.items()
    }

    st.session_state["probabilities"] = {
        name: model.predict_proba(user_data)[0]
        for name, model in models.items()
    }

    st.session_state["predicted"] = True

    st.balloons()


# ==================================================
# 10. 예측 결과
# ==================================================

if st.session_state.get("predicted", False):

    user_data = st.session_state["user_data"]

    predictions = st.session_state["predictions"]

    probabilities = st.session_state["probabilities"]

    st.success("예측이 완료되었습니다!")

    result_col1, result_col2 = st.columns(2)

    with result_col1:

        st.markdown("### 🌳 랜덤 포레스트")

        st.markdown(
            f"## {species_korean.get(predictions['랜덤 포레스트'], predictions['랜덤 포레스트'])}"
        )

        st.write(
            f"예측 품종: **{predictions['랜덤 포레스트']}**"
        )

    with result_col2:

        st.markdown("### 🎯 서포트 벡터 머신")

        st.markdown(
            f"## {species_korean.get(predictions['서포트 벡터 머신'], predictions['서포트 벡터 머신'])}"
        )

        st.write(
            f"예측 품종: **{predictions['서포트 벡터 머신']}**"
        )

    if predictions["랜덤 포레스트"] == predictions["서포트 벡터 머신"]:

        st.success(
            "두 알고리즘이 같은 품종을 예측했습니다."
        )

    else:

        st.warning(
            "두 알고리즘의 예측 결과가 다릅니다. "
            "아래 확률과 정확도를 함께 비교해보세요."
        )

    # 품종별 예측 확률
    st.subheader("알고리즘별 품종 예측 확률")

    prob_df = pd.DataFrame({
        "품종": species_names,
        "랜덤 포레스트": probabilities["랜덤 포레스트"],
        "서포트 벡터 머신": probabilities["서포트 벡터 머신"]
    })

    prob_long = prob_df.melt(
        id_vars="품종",
        var_name="알고리즘",
        value_name="예측 확률"
    )

    fig_prob = px.bar(
        prob_long,
        x="품종",
        y="예측 확률",
        color="알고리즘",
        barmode="group",
        text_auto=".1%",
        title="품종별 예측 확률 비교"
    )

    fig_prob.update_layout(
        yaxis_tickformat=".0%",
        yaxis_range=[0, 1],
        legend_title="알고리즘"
    )

    st.plotly_chart(
        fig_prob,
        use_container_width=True
    )


# ==================================================
# 11. 알고리즘 정확도 비교
# ==================================================

st.markdown(
    '<div class="section-title">📈 알고리즘 성능 비교</div>',
    unsafe_allow_html=True
)

accuracy_df = pd.DataFrame([
    {
        "알고리즘": name,
        "정확도": result["accuracy"]
    }
    for name, result in model_results.items()
])

accuracy_df["정확도(%)"] = (
    accuracy_df["정확도"] * 100
).round(2)

best_model = accuracy_df.loc[
    accuracy_df["정확도"].idxmax()
]

st.info(
    f"현재 테스트 데이터에서 가장 높은 정확도를 보인 알고리즘은 "
    f"**{best_model['알고리즘']}**이며, 정확도는 "
    f"**{best_model['정확도(%)']:.2f}%**입니다."
)

fig_accuracy = px.bar(
    accuracy_df,
    x="알고리즘",
    y="정확도",
    color="알고리즘",
    text="정확도",
    title="두 알고리즘의 테스트 데이터 정확도 비교",
    range_y=[0, 1]
)

fig_accuracy.update_traces(
    texttemplate="%{text:.1%}",
    textposition="outside"
)

fig_accuracy.update_layout(
    yaxis_tickformat=".0%",
    yaxis_title="정확도",
    xaxis_title="분류 알고리즘",
    showlegend=False
)

st.plotly_chart(
    fig_accuracy,
    use_container_width=True
)

st.caption(
    "정확도는 테스트 데이터에서 실제 품종과 예측 품종이 일치한 비율입니다. "
    "실제 펭귄 전체에 대한 정확도를 보장하지는 않습니다."
)


# ==================================================
# 12. 펭귄 신체 특징 산점도
# ==================================================

st.markdown(
    '<div class="section-title">🗺️ 펭귄 신체 특징 시각화</div>',
    unsafe_allow_html=True
)

st.write(
    "가로축은 날개 길이, 세로축은 부리 깊이입니다. "
    "색상은 실제 품종을 나타내며, 빨간 별은 입력한 펭귄입니다."
)

fig_scatter = px.scatter(
    df,
    x="flipper_length_mm",
    y="bill_depth_mm",
    color="species",
    hover_data=[
        "bill_length_mm",
        "body_mass_g"
    ],
    labels={
        "flipper_length_mm": "날개 길이 (mm)",
        "bill_depth_mm": "부리 깊이 (mm)",
        "species": "실제 품종",
        "bill_length_mm": "부리 길이 (mm)",
        "body_mass_g": "몸무게 (g)"
    },
    title="실제 펭귄 데이터 분포"
)

if st.session_state.get("predicted", False):

    fig_scatter.add_trace(
        go.Scatter(
            x=[flipper_length],
            y=[st.session_state["bill_depth"]],
            mode="markers",
            marker=dict(
                symbol="star",
                size=22,
                color="red",
                line=dict(
                    color="white",
                    width=2
                )
            ),
            name="입력한 펭귄",
            hovertemplate=(
                "입력한 펭귄<br>"
                "날개 길이: %{x} mm<br>"
                "부리 깊이: %{y} mm"
                "<extra></extra>"
            )
        )
    )

fig_scatter.update_layout(
    xaxis_title="날개 길이 (mm)",
    yaxis_title="부리 깊이 (mm)",
    legend_title="실제 품종"
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True
)


# ==================================================
# 13. 혼동 행렬
# ==================================================

st.markdown(
    '<div class="section-title">🧩 혼동 행렬</div>',
    unsafe_allow_html=True
)

st.write(
    "혼동 행렬은 실제 품종과 AI가 예측한 품종을 비교하는 표입니다. "
    "대각선에 있는 값이 클수록 정확하게 분류한 데이터가 많다는 뜻입니다."
)

tab1, tab2 = st.tabs([
    "랜덤 포레스트",
    "서포트 벡터 머신"
])

for tab, name in zip(
    [tab1, tab2],
    ["랜덤 포레스트", "서포트 벡터 머신"]
):

    with tab:

        cm = model_results[name]["confusion_matrix"]

        fig_cm = px.imshow(
            cm,
            x=species_names,
            y=species_names,
            text_auto=True,
            color_continuous_scale="Blues",
            labels={
                "x": "예측 품종",
                "y": "실제 품종",
                "color": "개체 수"
            },
            title=f"{name} 혼동 행렬"
        )

        st.plotly_chart(
            fig_cm,
            use_container_width=True
        )


# ==================================================
# 14. 알고리즘 작동 원리
# ==================================================

st.markdown(
    '<div class="section-title">🧠 인공지능 알고리즘 알아보기</div>',
    unsafe_allow_html=True
)

with st.expander("🌳 랜덤 포레스트 작동 원리"):

    st.write("""
    랜덤 포레스트는 여러 개의 의사결정나무를 만들어 예측 결과를 종합하는 알고리즘입니다.

    1. 학습 데이터를 무작위로 선택해 여러 학습용 데이터 집합을 만듭니다.
    2. 각각의 데이터 집합으로 의사결정나무를 학습시킵니다.
    3. 각 나무가 펭귄의 품종을 예측합니다.
    4. 가장 많은 나무가 선택한 품종을 최종 결과로 결정합니다.

    여러 나무의 결과를 종합하기 때문에 하나의 나무에 비해
    예측 결과가 안정적일 수 있습니다.
    """)

with st.expander("🎯 서포트 벡터 머신 작동 원리"):

    st.write("""
    서포트 벡터 머신(SVM)은 서로 다른 품종의 데이터를 가장 잘 구분하는
    경계선을 찾는 알고리즘입니다.

    1. 펭귄의 신체 측정값을 좌표상의 점으로 나타냅니다.
    2. 품종을 가장 잘 구분할 수 있는 경계를 학습합니다.
    3. 새로운 펭귄이 경계의 어느 쪽에 위치하는지 판단합니다.
    4. 해당 위치에 맞는 품종을 예측합니다.

    이 프로그램은 RBF 커널을 사용합니다. 따라서 단순한 직선으로
    구분하기 어려운 데이터의 복잡한 경계도 학습할 수 있습니다.

    SVM은 입력 변수의 크기에 영향을 받기 때문에
    StandardScaler로 데이터를 표준화한 뒤 학습합니다.
    """)


# ==================================================
# 15. 하단 안내
# ==================================================

st.divider()

st.caption(
    "Penguin AI Lab | 인공지능 기초 수행평가 프로젝트"
)

st.caption(
    "본 프로그램은 Palmer Penguins 데이터셋을 활용합니다. "
    "예측 결과는 학습 데이터에 기반한 추정값이며, 실제 품종과 다를 수 있습니다."
)
