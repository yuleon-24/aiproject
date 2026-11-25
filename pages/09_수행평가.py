import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix


# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="펭귄 종 예측 AI",
    page_icon="🐧",
    layout="wide"
)


# --------------------------------------------------
# 전체 색상 테마
# 어두운 배경 + 밝은 글씨로 대비 강화
# --------------------------------------------------
st.markdown(
    """
    <style>
    /* 전체 앱 배경과 기본 글자색 */
    .stApp {
        background-color: #0b1120;
        color: #f8fafc;
    }

    html, body, [class*="css"] {
        color: #f8fafc !important;
    }

    /* 기본 글자 */
    p, li, label, span, div {
        color: #f1f5f9;
    }

    /* 제목 */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    /* 주요 콘텐츠 영역 */
    [data-testid="stAppViewBlockContainer"] {
        background-color: #0b1120;
    }

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    /* 카드 */
    .info-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .info-card h3 {
        color: #ffffff !important;
        margin-top: 0;
    }

    .info-card p {
        color: #e2e8f0 !important;
    }

    /* 입력창 */
    input, textarea {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #64748b !important;
        border-radius: 8px !important;
    }

    /* 숫자 입력창 내부 글씨 */
    [data-testid="stNumberInput"] input {
        color: #ffffff !important;
        background-color: #1e293b !important;
    }

    /* 선택창 */
    [data-testid="stSelectbox"] div,
    [data-testid="stMultiSelect"] div {
        color: #f8fafc !important;
    }

    [data-testid="stSelectbox"] [role="combobox"],
    [data-testid="stMultiSelect"] [role="combobox"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }

    /* 드롭다운 메뉴 */
    [role="listbox"],
    [role="option"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }

    /* 슬라이더 */
    [data-testid="stSlider"] * {
        color: #f8fafc !important;
    }

    /* 버튼 */
    .stButton > button,
    .stDownloadButton > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #60a5fa !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
        border-color: #93c5fd !important;
    }

    /* 탭 */
    button[data-baseweb="tab"] {
        color: #cbd5e1 !important;
        background-color: #111827 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        background-color: #1d4ed8 !important;
        border-bottom: 3px solid #93c5fd !important;
    }

    /* 표 */
    [data-testid="stDataFrame"] {
        background-color: #1e293b;
    }

    /* 안내 메시지 */
    [data-testid="stAlert"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #475569 !important;
    }

    /* 구분선 */
    hr {
        border-color: #334155 !important;
    }

    /* 펼침 영역 */
    [data-testid="stExpander"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
    }

    /* 메트릭 */
    [data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("penguins.csv")

    # 컬럼명 앞뒤 공백 제거
    df.columns = df.columns.str.strip()

    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "penguins.csv 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 penguins.csv 파일을 넣어주세요."
    )
    st.stop()


# --------------------------------------------------
# 사용할 컬럼 확인
# --------------------------------------------------
required_columns = [
    "species",
    "flipper_length_mm",
    "body_mass_g",
    "bill_length_mm"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(
        "CSV 파일에 필요한 컬럼이 없습니다: "
        + ", ".join(missing_columns)
    )
    st.stop()


# 부리 깊이(bill_depth_mm)는 사용하지 않음
feature_columns = [
    "flipper_length_mm",
    "body_mass_g",
    "bill_length_mm"
]

df = df[required_columns].copy()
df = df.dropna(subset=required_columns)

if df.empty:
    st.error("분석할 수 있는 데이터가 없습니다.")
    st.stop()


# --------------------------------------------------
# 모델 학습
# --------------------------------------------------
X = df[feature_columns]
y = df["species"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


@st.cache_resource
def train_models(X_train, X_test, y_train, y_test):
    # 랜덤 포레스트
    rf_model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )
    rf_model.fit(X_train, y_train)

    # SVM
    svm_model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", SVC(
                kernel="rbf",
                probability=True,
                class_weight="balanced",
                random_state=42
            ))
        ]
    )
    svm_model.fit(X_train, y_train)

    rf_pred = rf_model.predict(X_test)
    svm_pred = svm_model.predict(X_test)

    rf_accuracy = accuracy_score(y_test, rf_pred)
    svm_accuracy = accuracy_score(y_test, svm_pred)

    return (
        rf_model,
        svm_model,
        rf_accuracy,
        svm_accuracy,
        rf_pred,
        svm_pred
    )


(
    rf_model,
    svm_model,
    rf_accuracy,
    svm_accuracy,
    rf_pred,
    svm_pred
) = train_models(X_train, X_test, y_train, y_test)


# --------------------------------------------------
# 제목
# --------------------------------------------------
st.title("🐧 펭귄 종 예측 AI")
st.markdown(
    """
    펭귄의 **날개 길이, 몸무게, 부리 길이**를 입력하면
    AI가 펭귄의 종을 예측합니다.
    """
)


# --------------------------------------------------
# 데이터 요약
# --------------------------------------------------
st.subheader("📊 데이터 미리보기")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("전체 데이터 수", f"{len(df):,}개")

with col2:
    st.metric("펭귄 종 수", f"{df['species'].nunique()}종")

with col3:
    st.metric("사용한 입력 변수", "3개")

with st.expander("데이터 일부 보기"):
    st.dataframe(df.head(10), use_container_width=True)


# --------------------------------------------------
# 사용자 입력
# --------------------------------------------------
st.subheader("🔎 펭귄 정보 입력")

st.markdown(
    "아래 입력창에서 값을 선택하세요. 각 입력창의 최소·최대 범위는 "
    "CSV 데이터에 들어 있는 실제 값의 범위를 기준으로 설정됩니다."
)

input_col1, input_col2, input_col3 = st.columns(3)

flipper_min = int(df["flipper_length_mm"].min())
flipper_max = int(df["flipper_length_mm"].max())
flipper_default = int(df["flipper_length_mm"].median())

mass_min = int(df["body_mass_g"].min())
mass_max = int(df["body_mass_g"].max())
mass_default = int(df["body_mass_g"].median())

bill_min = float(df["bill_length_mm"].min())
bill_max = float(df["bill_length_mm"].max())
bill_default = float(df["bill_length_mm"].median())

with input_col1:
    flipper_length = st.slider(
        "날개 길이 (mm)",
        min_value=flipper_min,
        max_value=flipper_max,
        value=flipper_default
    )

with input_col2:
    body_mass = st.slider(
        "몸무게 (g)",
        min_value=mass_min,
        max_value=mass_max,
        value=mass_default,
        step=50
    )

with input_col3:
    bill_length = st.slider(
        "부리 길이 (mm)",
        min_value=float(bill_min),
        max_value=float(bill_max),
        value=float(bill_default),
        step=0.1
    )


# --------------------------------------------------
# 예측 모델 선택
# --------------------------------------------------
model_choice = st.selectbox(
    "사용할 예측 알고리즘 선택",
    ["랜덤 포레스트", "서포트 벡터 머신(SVM)"]
)

if model_choice == "랜덤 포레스트":
    selected_model = rf_model
else:
    selected_model = svm_model


# --------------------------------------------------
# 예측 실행
# --------------------------------------------------
if st.button("🔮 펭귄 종 예측하기", use_container_width=True):
    user_input = pd.DataFrame(
        [[flipper_length, body_mass, bill_length]],
        columns=feature_columns
    )

    prediction = selected_model.predict(user_input)[0]
    probabilities = selected_model.predict_proba(user_input)[0]

    classes = selected_model.classes_
    probability_df = pd.DataFrame({
        "펭귄 종": classes,
        "예측 확률": probabilities
    }).sort_values("예측 확률", ascending=False)

    st.session_state["prediction"] = prediction
    st.session_state["probability_df"] = probability_df
    st.session_state["user_input"] = user_input
    st.session_state["model_choice"] = model_choice


# --------------------------------------------------
# 예측 결과
# --------------------------------------------------
if "prediction" in st.session_state:
    st.subheader("🎯 예측 결과")

    result_col1, result_col2 = st.columns([1, 2])

    with result_col1:
        st.markdown(
            f"""
            <div class="info-card">
                <h3>AI가 예측한 종</h3>
                <h2 style="color:#93c5fd !important;">
                    {st.session_state["prediction"]}
                </h2>
                <p>사용 알고리즘: {st.session_state["model_choice"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with result_col2:
        st.markdown("**종별 예측 확률**")
        probability_df = st.session_state["probability_df"]

        fig_prob = px.bar(
            probability_df,
            x="펭귄 종",
            y="예측 확률",
            color="펭귄 종",
            text=probability_df["예측 확률"].map(
                lambda x: f"{x:.1%}"
            )
        )

        fig_prob.update_layout(
            paper_bgcolor="#1e293b",
            plot_bgcolor="#1e293b",
            font=dict(color="#f8fafc"),
            yaxis=dict(
                tickformat=".0%",
                gridcolor="#475569"
            ),
            xaxis=dict(gridcolor="#475569"),
            showlegend=False
        )

        st.plotly_chart(fig_prob, use_container_width=True)


# --------------------------------------------------
# 산점도: 날개 길이와 부리 길이
# --------------------------------------------------
st.subheader("📍 펭귄 데이터 산점도")
st.markdown(
    "가로축은 **날개 길이**, 세로축은 **부리 길이**입니다. "
    "예측을 실행하면 입력한 펭귄이 별표로 표시됩니다."
)

fig_scatter = px.scatter(
    df,
    x="flipper_length_mm",
    y="bill_length_mm",
    color="species",
    hover_data=["body_mass_g"],
    labels={
        "flipper_length_mm": "날개 길이 (mm)",
        "bill_length_mm": "부리 길이 (mm)",
        "species": "펭귄 종",
        "body_mass_g": "몸무게 (g)"
    },
    color_discrete_sequence=[
        "#38bdf8",
        "#fbbf24",
        "#f472b6"
    ]
)

if "user_input" in st.session_state:
    user_point = st.session_state["user_input"]

    fig_scatter.add_trace(
        go.Scatter(
            x=user_point["flipper_length_mm"],
            y=user_point["bill_length_mm"],
            mode="markers",
            name="내가 입력한 펭귄",
            marker=dict(
                symbol="star",
                size=20,
                color="#ffffff",
                line=dict(color="#ef4444", width=3)
            )
        )
    )

fig_scatter.update_layout(
    paper_bgcolor="#0b1120",
    plot_bgcolor="#1e293b",
    font=dict(color="#f8fafc"),
    xaxis=dict(
        title="날개 길이 (mm)",
        gridcolor="#475569",
        zerolinecolor="#64748b"
    ),
    yaxis=dict(
        title="부리 길이 (mm)",
        gridcolor="#475569",
        zerolinecolor="#64748b"
    ),
    legend=dict(
        bgcolor="#1e293b",
        font=dict(color="#f8fafc")
    )
)

st.plotly_chart(fig_scatter, use_container_width=True)


# --------------------------------------------------
# 알고리즘 비교
# --------------------------------------------------
st.subheader("⚖️ 두 알고리즘 성능 비교")

compare_col1, compare_col2 = st.columns(2)

with compare_col1:
    st.metric("랜덤 포레스트 정확도", f"{rf_accuracy:.1%}")

with compare_col2:
    st.metric("SVM 정확도", f"{svm_accuracy:.1%}")

comparison_df = pd.DataFrame({
    "알고리즘": ["랜덤 포레스트", "SVM"],
    "정확도": [rf_accuracy, svm_accuracy]
})

fig_compare = px.bar(
    comparison_df,
    x="알고리즘",
    y="정확도",
    text=comparison_df["정확도"].map(lambda x: f"{x:.1%}"),
    color="알고리즘",
    color_discrete_sequence=["#38bdf8", "#fbbf24"]
)

fig_compare.update_layout(
    paper_bgcolor="#0b1120",
    plot_bgcolor="#1e293b",
    font=dict(color="#f8fafc"),
    yaxis=dict(
        range=[0, 1],
        tickformat=".0%",
        gridcolor="#475569"
    ),
    xaxis=dict(gridcolor="#475569"),
    showlegend=False
)

st.plotly_chart(fig_compare, use_container_width=True)


# --------------------------------------------------
# 알고리즘 설명
# --------------------------------------------------
st.subheader("🧠 사용한 알고리즘 설명")

tab1, tab2 = st.tabs(["랜덤 포레스트", "서포트 벡터 머신(SVM)"])

with tab1:
    st.markdown(
        """
        **랜덤 포레스트(Random Forest)**

        여러 개의 결정 트리를 만들고, 각 트리의 예측 결과를 모아
        최종 종을 결정하는 알고리즘입니다.

        - 여러 트리의 결과를 종합해 예측합니다.
        - 변수 사이의 복잡한 관계를 학습할 수 있습니다.
        - 이번 프로젝트에서는 펭귄의 세 가지 측정값을 이용해 종을 분류합니다.
        """
    )

with tab2:
    st.markdown(
        """
        **서포트 벡터 머신(Support Vector Machine, SVM)**

        데이터를 서로 구분할 수 있는 경계선을 찾고,
        그 경계를 바탕으로 새로운 데이터의 종을 예측하는 알고리즘입니다.

        - 데이터 사이의 구분 경계를 찾습니다.
        - 변수의 크기 차이가 결과에 영향을 줄 수 있어 표준화를 함께 사용합니다.
        - 이번 프로젝트에서는 날개 길이, 몸무게, 부리 길이를 이용해 종을 분류합니다.
        """
    )


# --------------------------------------------------
# 마무리 안내
# --------------------------------------------------
st.markdown("---")
st.caption(
    "※ 예측 결과는 학습 데이터와 알고리즘에 따른 추정값이며, "
    "실제 펭귄의 종을 확정하는 용도로 사용하지 않습니다."
)
