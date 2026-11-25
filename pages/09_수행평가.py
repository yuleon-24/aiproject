import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix


# =========================================================
# 1) 페이지 설정
# =========================================================
st.set_page_config(
    page_title="펭귄 품종 예측 연구소",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 2) 색상 및 화면 디자인
#    config.toml과 함께 사용하면 밝은 테마에서 안정적으로 표시됨
# =========================================================
st.markdown(
    """
    <style>
    /* 전체 화면 */
    .stApp {
        background-color: #F4F7FB !important;
        color: #172B4D !important;
    }

    [data-testid="stHeader"] {
        background-color: #F4F7FB !important;
    }

    [data-testid="stSidebar"] {
        background-color: #E8EEF7 !important;
        border-right: 1px solid #C9D5E5;
    }

    /* 기본 글자색 */
    html, body, [class*="css"], .stMarkdown,
    .stMarkdown p, .stMarkdown li, .stMarkdown span,
    label, [data-testid="stCaptionContainer"] {
        color: #172B4D !important;
    }

    /* 제목 */
    h1, h2, h3, h4, h5, h6 {
        color: #102A43 !important;
        font-weight: 800 !important;
    }

    /* 본문 */
    p, li {
        color: #243B53 !important;
        line-height: 1.65;
    }

    /* 링크 */
    a {
        color: #075985 !important;
        font-weight: 700;
    }

    /* 입력창, 숫자 입력창, 선택창 */
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        background-color: #FFFFFF !important;
        color: #102A43 !important;
        -webkit-text-fill-color: #102A43 !important;
        border: 1px solid #9FB3C8 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #102A43 !important;
        border-color: #9FB3C8 !important;
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input {
        color: #102A43 !important;
        -webkit-text-fill-color: #102A43 !important;
    }

    /* 슬라이더 설명과 값 */
    [data-testid="stSlider"] label,
    [data-testid="stSlider"] p,
    [data-testid="stSlider"] div {
        color: #172B4D !important;
    }

    /* 버튼 */
    .stButton > button,
    .stDownloadButton > button {
        background-color: #145DA0 !important;
        color: #FFFFFF !important;
        border: 1px solid #145DA0 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        min-height: 44px;
    }

    .stButton > button *,
    .stDownloadButton > button * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #0B3D68 !important;
        border-color: #0B3D68 !important;
    }

    /* 탭 */
    button[data-baseweb="tab"] {
        color: #243B53 !important;
        font-weight: 700 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #075985 !important;
        border-bottom-color: #075985 !important;
    }

    /* 카드 */
    .info-card {
        background-color: #FFFFFF;
        border: 1px solid #D5DFEA;
        border-radius: 14px;
        padding: 18px 20px;
        margin: 8px 0;
        box-shadow: 0 3px 10px rgba(16, 42, 67, 0.06);
    }

    .info-card h3 {
        color: #102A43 !important;
        margin-top: 0;
    }

    .info-card p {
        color: #243B53 !important;
        margin-bottom: 0;
    }

    .eyebrow {
        color: #075985 !important;
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 0.06em;
    }

    .hero {
        background: linear-gradient(120deg, #E0F2FE 0%, #EFF6FF 55%, #F0FDFA 100%);
        border: 1px solid #BAE6FD;
        border-radius: 18px;
        padding: 26px 28px;
        margin-bottom: 18px;
    }

    .hero h1 {
        color: #0C2D48 !important;
        margin: 6px 0 10px 0;
    }

    .hero p {
        color: #24445E !important;
        margin-bottom: 0;
    }

    /* 알림 상자 */
    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* 데이터프레임 */
    [data-testid="stDataFrame"] {
        border: 1px solid #D5DFEA;
        border-radius: 10px;
        overflow: hidden;
    }

    /* 구분선 */
    hr {
        border-color: #D5DFEA !important;
    }

    /* 모바일 화면 */
    @media (max-width: 768px) {
        .hero {
            padding: 20px;
        }

        .hero h1 {
            font-size: 1.8rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3) 상단 소개
# =========================================================
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">DATA SCIENCE · CLASSIFICATION</div>
        <h1>🐧 펭귄 품종 예측 연구소</h1>
        <p>
            펭귄의 신체 측정값을 입력하고, 머신러닝 모델이 어떤 품종으로
            분류하는지 확인해 보세요.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 4) 데이터 불러오기 및 전처리
# =========================================================
@st.cache_data
def load_data():
    data = pd.read_csv("penguins.csv")

    # 데이터셋에서 사용할 열 이름
    required_columns = [
        "species",
        "flipper_length_mm",
        "body_mass_g",
        "bill_length_mm",
    ]

    missing_columns = [
        col for col in required_columns if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "CSV 파일에 필요한 열이 없습니다: "
            + ", ".join(missing_columns)
        )

    data = data[required_columns].copy()

    # 숫자형 열을 숫자로 변환
    numeric_columns = [
        "flipper_length_mm",
        "body_mass_g",
        "bill_length_mm",
    ]

    for col in numeric_columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    # 필요한 열에 결측값이 있는 행 제거
    data = data.dropna(subset=required_columns)

    # 품종 이름 앞뒤 공백 제거
    data["species"] = data["species"].astype(str).str.strip()

    return data


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "penguins.csv 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 penguins.csv를 업로드해 주세요."
    )
    st.stop()
except Exception as e:
    st.error(f"데이터를 불러오는 중 문제가 발생했습니다: {e}")
    st.stop()


FEATURES = [
    "flipper_length_mm",
    "body_mass_g",
    "bill_length_mm",
]

TARGET = "species"

X = df[FEATURES]
y = df[TARGET]

if y.nunique() < 2:
    st.error("품종이 2종 이상 포함된 데이터가 필요합니다.")
    st.stop()


# =========================================================
# 5) 학습 및 평가 데이터 분리
# =========================================================
try:
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )
except ValueError:
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )


# =========================================================
# 6) 두 가지 분류 모델 학습
# =========================================================
@st.cache_resource
def train_models():
    # 모델 1: 랜덤 포레스트
    random_forest = RandomForestClassifier(
        n_estimators=250,
        max_depth=None,
        random_state=42,
        class_weight="balanced",
    )

    # 모델 2: 서포트 벡터 머신
    svm = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "model",
                SVC(
                    kernel="rbf",
                    C=2.0,
                    probability=True,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )

    random_forest.fit(X_train, y_train)
    svm.fit(X_train, y_train)

    return random_forest, svm


rf_model, svm_model = train_models()

rf_pred = rf_model.predict(X_test)
svm_pred = svm_model.predict(X_test)

rf_accuracy = accuracy_score(y_test, rf_pred)
svm_accuracy = accuracy_score(y_test, svm_pred)


# =========================================================
# 7) 데이터 요약
# =========================================================
st.subheader("📊 데이터 한눈에 보기")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("전체 데이터 수", f"{len(df):,}개")

with col2:
    st.metric("펭귄 품종 수", f"{df['species'].nunique()}종")

with col3:
    st.metric("사용하는 측정 항목", "3개")

with st.expander("데이터 표 확인하기"):
    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")


# =========================================================
# 8) 입력 범위 계산
# =========================================================
flipper_min = int(np.floor(df["flipper_length_mm"].min()))
flipper_max = int(np.ceil(df["flipper_length_mm"].max()))

mass_min = int(np.floor(df["body_mass_g"].min()))
mass_max = int(np.ceil(df["body_mass_g"].max()))

bill_min = int(np.floor(df["bill_length_mm"].min()))
bill_max = int(np.ceil(df["bill_length_mm"].max()))


# =========================================================
# 9) 사용자 입력 및 예측
# =========================================================
st.subheader("🔍 펭귄 측정값 입력")

st.write(
    "아래 범위 안에서 값을 입력하면 두 모델이 각각 품종을 예측합니다."
)

with st.container(border=True):
    input_col1, input_col2, input_col3 = st.columns(3)

    with input_col1:
        flipper_length = st.slider(
            "날개 길이 (mm)",
            min_value=flipper_min,
            max_value=flipper_max,
            value=int(df["flipper_length_mm"].median()),
            help=f"입력 가능 범위: {flipper_min}~{flipper_max} mm",
        )
        st.caption(f"입력 범위: {flipper_min}~{flipper_max} mm")

    with input_col2:
        body_mass = st.slider(
            "몸무게 (g)",
            min_value=mass_min,
            max_value=mass_max,
            value=int(df["body_mass_g"].median()),
            step=50,
            help=f"입력 가능 범위: {mass_min}~{mass_max} g",
        )
        st.caption(f"입력 범위: {mass_min}~{mass_max} g")

    with input_col3:
        bill_length = st.slider(
            "부리 길이 (mm)",
            min_value=bill_min,
            max_value=bill_max,
            value=int(df["bill_length_mm"].median()),
            help=f"입력 가능 범위: {bill_min}~{bill_max} mm",
        )
        st.caption(f"입력 범위: {bill_min}~{bill_max} mm")


input_data = pd.DataFrame(
    [[flipper_length, body_mass, bill_length]],
    columns=FEATURES,
)

rf_result = rf_model.predict(input_data)[0]
svm_result = svm_model.predict(input_data)[0]

rf_probabilities = rf_model.predict_proba(input_data)[0]
svm_probabilities = svm_model.predict_proba(input_data)[0]

rf_classes = rf_model.classes_
svm_classes = svm_model.named_steps["model"].classes_


# =========================================================
# 10) 예측 결과 표시
# =========================================================
st.markdown("### 🏆 예측 결과")

result_col1, result_col2 = st.columns(2)

with result_col1:
    st.markdown(
        """
        <div class="info-card">
            <div class="eyebrow">MODEL 01</div>
            <h3>랜덤 포레스트</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.success(f"예측 품종: {rf_result}")

with result_col2:
    st.markdown(
        """
        <div class="info-card">
            <div class="eyebrow">MODEL 02</div>
            <h3>서포트 벡터 머신 (SVM)</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(f"예측 품종: {svm_result}")

if rf_result == svm_result:
    st.success("두 모델이 같은 품종으로 예측했습니다.")
else:
    st.warning(
        "두 모델의 예측 결과가 다릅니다. "
        "아래 모델 비교와 확률을 함께 확인해 보세요."
    )


# =========================================================
# 11) 예측 확률
# =========================================================
st.markdown("### 예측 확률")

prob_col1, prob_col2 = st.columns(2)

with prob_col1:
    st.markdown("**랜덤 포레스트**")
    rf_prob_df = pd.DataFrame(
        {
            "품종": rf_classes,
            "예측 확률 (%)": rf_probabilities * 100,
        }
    ).sort_values("예측 확률 (%)", ascending=False)

    st.dataframe(
        rf_prob_df.style.format({"예측 확률 (%)": "{:.1f}%"}),
        use_container_width=True,
        hide_index=True,
    )

with prob_col2:
    st.markdown("**서포트 벡터 머신**")
    svm_prob_df = pd.DataFrame(
        {
            "품종": svm_classes,
            "예측 확률 (%)": svm_probabilities * 100,
        }
    ).sort_values("예측 확률 (%)", ascending=False)

    st.dataframe(
        svm_prob_df.style.format({"예측 확률 (%)": "{:.1f}%"}),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 12) 산점도: 가로축 날개 길이, 세로축 부리 길이
# =========================================================
st.markdown("---")
st.subheader("📈 측정값 산점도")
st.write(
    "가로축은 날개 길이, 세로축은 부리 길이입니다. "
    "별 모양 표시는 사용자가 입력한 값입니다."
)

plot_df = df.copy()
plot_df["품종"] = plot_df["species"]

fig = px.scatter(
    plot_df,
    x="flipper_length_mm",
    y="bill_length_mm",
    color="품종",
    hover_data=["body_mass_g"],
    labels={
        "flipper_length_mm": "날개 길이 (mm)",
        "bill_length_mm": "부리 길이 (mm)",
        "body_mass_g": "몸무게 (g)",
    },
    title="펭귄 품종별 날개 길이와 부리 길이",
    template="plotly_white",
)

fig.add_scatter(
    x=[flipper_length],
    y=[bill_length],
    mode="markers",
    name="내 입력값",
    marker={
        "symbol": "star",
        "size": 19,
        "color": "#E11D48",
        "line": {"color": "#FFFFFF", "width": 2},
    },
    hovertemplate=(
        "내 입력값<br>"
        "날개 길이: %{x} mm<br>"
        "부리 길이: %{y} mm"
        "<extra></extra>"
    ),
)

fig.update_layout(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font={"color": "#172B4D", "size": 13},
    title_font={"color": "#102A43", "size": 20},
    legend_title_font={"color": "#102A43"},
    legend_font={"color": "#243B53"},
    xaxis={
        "title": "날개 길이 (mm)",
        "color": "#243B53",
        "gridcolor": "#E2E8F0",
        "zerolinecolor": "#CBD5E1",
    },
    yaxis={
        "title": "부리 길이 (mm)",
        "color": "#243B53",
        "gridcolor": "#E2E8F0",
        "zerolinecolor": "#CBD5E1",
    },
)

st.plotly_chart(fig, use_container_width=True)


# =========================================================
# 13) 모델 정확도 비교
# =========================================================
st.markdown("---")
st.subheader("⚖️ 분류 알고리즘 비교")

accuracy_df = pd.DataFrame(
    {
        "알고리즘": ["랜덤 포레스트", "서포트 벡터 머신 (SVM)"],
        "정확도 (%)": [rf_accuracy * 100, svm_accuracy * 100],
    }
)

acc_fig = px.bar(
    accuracy_df,
    x="알고리즘",
    y="정확도 (%)",
    text="정확도 (%)",
    color="알고리즘",
    color_discrete_sequence=["#2563EB", "#0F766E"],
    title="테스트 데이터 예측 정확도",
    template="plotly_white",
)

acc_fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
    cliponaxis=False,
)

acc_fig.update_layout(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font={"color": "#172B4D", "size": 13},
    title_font={"color": "#102A43", "size": 20},
    showlegend=False,
    yaxis={
        "title": "정확도 (%)",
        "range": [0, 105],
        "color": "#243B53",
        "gridcolor": "#E2E8F0",
    },
    xaxis={"title": "", "color": "#243B53"},
)

st.plotly_chart(acc_fig, use_container_width=True)

better_model = (
    "랜덤 포레스트"
    if rf_accuracy > svm_accuracy
    else "서포트 벡터 머신 (SVM)"
    if svm_accuracy > rf_accuracy
    else "두 모델의 정확도가 같습니다"
)

st.markdown(
    f"""
    <div class="info-card">
        <h3>비교 결과</h3>
        <p>
            랜덤 포레스트 정확도는 <b>{rf_accuracy * 100:.1f}%</b>,
            SVM 정확도는 <b>{svm_accuracy * 100:.1f}%</b>입니다.
            현재 테스트 데이터에서는 <b>{better_model}</b>이
            더 높은 정확도를 보였습니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 14) 알고리즘 설명
# =========================================================
st.markdown("---")
st.subheader("🧠 알고리즘 알아보기")

tab1, tab2 = st.tabs(["랜덤 포레스트", "서포트 벡터 머신 (SVM)"])

with tab1:
    st.markdown(
        """
        <div class="info-card">
            <h3>여러 개의 결정 트리를 모아 예측하는 방법</h3>
            <p>
                랜덤 포레스트는 여러 개의 결정 트리를 학습시킨 뒤,
                각 트리의 예측을 종합해 최종 품종을 결정합니다.
                여러 트리를 함께 사용하기 때문에 하나의 트리에만
                의존하는 것보다 예측이 안정적일 수 있습니다.
            </p>
            <p>
                <b>이번 프로젝트에서:</b> 날개 길이, 몸무게, 부리 길이의
                조합을 이용해 품종을 분류합니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab2:
    st.markdown(
        """
        <div class="info-card">
            <h3>품종 사이를 구분하는 경계를 찾는 방법</h3>
            <p>
                SVM은 서로 다른 품종의 데이터를 가장 잘 구분할 수 있는
                경계를 찾습니다. 이번 코드에서는 RBF 커널을 사용해
                직선만으로 나누기 어려운 관계도 학습할 수 있도록 했습니다.
            </p>
            <p>
                <b>이번 프로젝트에서:</b> 측정값의 단위와 크기가 다르므로
                StandardScaler로 값을 표준화한 뒤 분류합니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 15) 혼동 행렬
# =========================================================
st.markdown("---")
st.subheader("🧩 혼동 행렬")
st.write(
    "혼동 행렬은 실제 품종과 모델이 예측한 품종을 비교한 표입니다. "
    "대각선에 있는 값이 클수록 맞게 분류한 데이터가 많다는 뜻입니다."
)

cm_col1, cm_col2 = st.columns(2)

labels = sorted(y.unique())

with cm_col1:
    st.markdown("**랜덤 포레스트**")
    rf_cm = confusion_matrix(y_test, rf_pred, labels=labels)
    rf_cm_df = pd.DataFrame(
        rf_cm,
        index=[f"실제 {label}" for label in labels],
        columns=[f"예측 {label}" for label in labels],
    )
    st.dataframe(rf_cm_df, use_container_width=True)

with cm_col2:
    st.markdown("**서포트 벡터 머신**")
    svm_cm = confusion_matrix(y_test, svm_pred, labels=labels)
    svm_cm_df = pd.DataFrame(
        svm_cm,
        index=[f"실제 {label}" for label in labels],
        columns=[f"예측 {label}" for label in labels],
    )
    st.dataframe(svm_cm_df, use_container_width=True)


# =========================================================
# 16) 마무리 안내
# =========================================================
st.markdown("---")
st.caption(
    "참고: 모델의 정확도는 학습 데이터와 테스트 데이터 분할에 따라 달라질 수 있습니다. "
    "예측 확률은 모델이 계산한 추정값이며, 실제 정답을 보장하지 않습니다."
)
