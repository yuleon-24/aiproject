import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score


# --------------------------------------------------
# 1. 페이지 설정 및 글자 색상
# --------------------------------------------------

st.set_page_config(
    page_title="펭귄 품종 예측",
    page_icon="🐧",
    layout="wide"
)

# 배경은 흰색, 글씨는 어두운 색으로 설정
st.markdown("""
<style>
/* 전체 배경과 기본 글자 */
.stApp {
    background-color: #FFFFFF !important;
    color: #1A1A1A !important;
}

/* 일반 글자 */
.stApp p,
.stApp label,
.stApp span,
.stApp li,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4 {
    color: #1A1A1A !important;
}

/* 입력창 */
.stApp input,
.stApp textarea,
.stApp [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #1A1A1A !important;
}

/* 입력창 안의 글자 */
.stApp input::placeholder {
    color: #666666 !important;
}

/* 버튼 */
.stApp button {
    background-color: #145DA0 !important;
    color: #FFFFFF !important;
    border: 1px solid #145DA0 !important;
}

/* 버튼 안의 글자 */
.stApp button p,
.stApp button span {
    color: #FFFFFF !important;
}

/* 정보 상자 */
.stAlert {
    background-color: #F0F6FF !important;
}

/* 표 */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 2. 제목
# --------------------------------------------------

st.title("🐧 펭귄 품종 예측 프로그램")
st.write("펭귄의 날개 길이, 몸무게, 부리 길이를 입력하면 품종을 예측합니다.")

st.divider()


# --------------------------------------------------
# 3. 데이터 불러오기
# --------------------------------------------------

@st.cache_data
def load_data():
    data = pd.read_csv("penguins.csv")

    # 예측에 필요한 열만 사용
    data = data[
        [
            "species",
            "flipper_length_mm",
            "body_mass_g",
            "bill_length_mm"
        ]
    ]

    # 비어 있는 데이터 제거
    data = data.dropna()

    return data


try:
    df = load_data()

except Exception:
    st.error(
        "penguins.csv 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 penguins.csv 파일을 넣어주세요."
    )
    st.stop()


# --------------------------------------------------
# 4. 학습 데이터 준비
# --------------------------------------------------

X = df[
    [
        "flipper_length_mm",
        "body_mass_g",
        "bill_length_mm"
    ]
]

y = df["species"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# --------------------------------------------------
# 5. 알고리즘 학습
# --------------------------------------------------

# 알고리즘 1: 랜덤 포레스트
model_rf = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model_rf.fit(X_train, y_train)


# 알고리즘 2: K-최근접 이웃
# KNN은 데이터의 거리로 품종을 예측하는 알고리즘입니다.
model_knn = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier(n_neighbors=5)
)

model_knn.fit(X_train, y_train)


# 두 알고리즘의 정확도 계산
rf_accuracy = accuracy_score(
    y_test,
    model_rf.predict(X_test)
)

knn_accuracy = accuracy_score(
    y_test,
    model_knn.predict(X_test)
)


# --------------------------------------------------
# 6. 입력 범위 안내
# --------------------------------------------------

st.header("1. 펭귄 정보 입력")

st.info(
    "아래 입력 범위는 penguins.csv 데이터에 들어 있는 "
    "최솟값과 최댓값을 기준으로 합니다."
)

col1, col2, col3 = st.columns(3)

# 실제 데이터의 최솟값과 최댓값
wing_min = int(df["flipper_length_mm"].min())
wing_max = int(df["flipper_length_mm"].max())

weight_min = int(df["body_mass_g"].min())
weight_max = int(df["body_mass_g"].max())

bill_min = float(df["bill_length_mm"].min())
bill_max = float(df["bill_length_mm"].max())


with col1:
    st.write(f"날개 길이 범위: {wing_min}~{wing_max} mm")

    wing_length = st.number_input(
        "날개 길이 (mm)",
        min_value=float(wing_min),
        max_value=float(wing_max),
        value=float(df["flipper_length_mm"].median()),
        step=1.0
    )


with col2:
    st.write(f"몸무게 범위: {weight_min}~{weight_max} g")

    body_mass = st.number_input(
        "몸무게 (g)",
        min_value=float(weight_min),
        max_value=float(weight_max),
        value=float(df["body_mass_g"].median()),
        step=50.0
    )


with col3:
    st.write(f"부리 길이 범위: {bill_min:.1f}~{bill_max:.1f} mm")

    bill_length = st.number_input(
        "부리 길이 (mm)",
        min_value=float(bill_min),
        max_value=float(bill_max),
        value=float(df["bill_length_mm"].median()),
        step=0.1
    )


# 사용자가 입력한 값을 표로 만들기
input_data = pd.DataFrame(
    [[wing_length, body_mass, bill_length]],
    columns=[
        "flipper_length_mm",
        "body_mass_g",
        "bill_length_mm"
    ]
)


# --------------------------------------------------
# 7. 품종 예측
# --------------------------------------------------

st.header("2. 예측 결과")

if st.button("펭귄 품종 예측하기", use_container_width=True):

    # 랜덤 포레스트로 예측
    prediction = model_rf.predict(input_data)[0]

    # 품종 이름을 보기 좋게 표시
    species_names = {
        "Adelie": "아델리 펭귄",
        "Chinstrap": "턱끈 펭귄",
        "Gentoo": "젠투 펭귄"
    }
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score


# ==================================================
# 1. 페이지 설정
# ==================================================

st.set_page_config(
    page_title="펭귄 품종 예측",
    page_icon="🐧",
    layout="wide"
)


# ==================================================
# 2. 화면 디자인
# ==================================================

st.markdown("""
<style>
/* 전체 배경과 기본 글자 */
.stApp {
    background-color: #FFFFFF !important;
    color: #172B4D !important;
}

/* 제목과 일반 글자 */
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp p,
.stApp label,
.stApp li,
.stApp span {
    color: #172B4D !important;
}

/* 입력창 */
.stApp input,
.stApp textarea {
    background-color: #FFFFFF !important;
    color: #172B4D !important;
    border: 1px solid #A6B5C5 !important;
}

/* 선택 상자 */
.stApp [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #172B4D !important;
}

/* 버튼 */
.stApp button {
    background-color: #145DA0 !important;
    color: #FFFFFF !important;
    border: 1px solid #145DA0 !important;
    border-radius: 8px !important;
}

/* 버튼 내부 글자 */
.stApp button p,
.stApp button span {
    color: #FFFFFF !important;
}

/* 정보 상자 */
.stAlert {
    background-color: #EAF3FF !important;
}

/* 표 배경 */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF !important;
}

/* 구분선 */
hr {
    border-color: #D6E0EA !important;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# 3. 제목과 안내
# ==================================================

st.title("🐧 펭귄 품종 예측 프로그램")

st.markdown("""
날개 길이, 몸무게, 부리 길이를 입력하면 펭귄의 품종을 예측합니다.

**사용 알고리즘:** 랜덤 포레스트와 K-최근접 이웃(KNN)
""")

st.divider()


# ==================================================
# 4. 데이터 불러오기
# ==================================================

@st.cache_data
def load_data():
    data = pd.read_csv("penguins.csv")

    needed_columns = [
        "species",
        "flipper_length_mm",
        "body_mass_g",
        "bill_length_mm"
    ]

    data = data[needed_columns].dropna()

    return data


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "penguins.csv 파일을 찾을 수 없습니다.\n\n"
        "app.py와 penguins.csv가 같은 폴더에 있는지 확인해주세요."
    )
    st.stop()

except Exception as error:
    st.error(f"데이터를 불러오는 중 문제가 발생했습니다: {error}")
    st.stop()


# ==================================================
# 5. 학습 데이터 준비
# ==================================================

feature_columns = [
    "flipper_length_mm",
    "body_mass_g",
    "bill_length_mm"
]

X = df[feature_columns]
y = df["species"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ==================================================
# 6. 알고리즘 학습
# ==================================================

# 랜덤 포레스트
model_rf = RandomForestClassifier(
    n_estimators=150,
    random_state=42
)

model_rf.fit(X_train, y_train)


# K-최근접 이웃
# KNN은 입력값과 가까운 데이터 5개의 품종을 참고합니다.
model_knn = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier(n_neighbors=5)
)

model_knn.fit(X_train, y_train)


# 정확도 계산
rf_accuracy = accuracy_score(
    y_test,
    model_rf.predict(X_test)
)

knn_accuracy = accuracy_score(
    y_test,
    model_knn.predict(X_test)
)


# ==================================================
# 7. 입력 범위 계산
# ==================================================

wing_min = int(df["flipper_length_mm"].min())
wing_max = int(df["flipper_length_mm"].max())

weight_min = int(df["body_mass_g"].min())
weight_max = int(df["body_mass_g"].max())

bill_min = float(df["bill_length_mm"].min())
bill_max = float(df["bill_length_mm"].max())


# ==================================================
# 8. 사용자 입력
# ==================================================

st.header("1. 펭귄 정보 입력")

st.info(
    "각 항목의 입력 범위는 데이터에 기록된 최솟값과 최댓값입니다."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**날개 길이**")
    st.caption(f"입력 범위: {wing_min}~{wing_max} mm")

    wing_length = st.number_input(
        "날개 길이 (mm)",
        min_value=float(wing_min),
        max_value=float(wing_max),
        value=float(df["flipper_length_mm"].median()),
        step=1.0,
        key="wing"
    )

with col2:
    st.markdown("**몸무게**")
    st.caption(f"입력 범위: {weight_min}~{weight_max} g")

    body_mass = st.number_input(
        "몸무게 (g)",
        min_value=float(weight_min),
        max_value=float(weight_max),
        value=float(df["body_mass_g"].median()),
        step=50.0,
        key="weight"
    )

with col3:
    st.markdown("**부리 길이**")
    st.caption(f"입력 범위: {bill_min:.1f}~{bill_max:.1f} mm")

    bill_length = st.number_input(
        "부리 길이 (mm)",
        min_value=float(bill_min),
        max_value=float(bill_max),
        value=float(df["bill_length_mm"].median()),
        step=0.1,
        key="bill"
    )


input_data = pd.DataFrame(
    [[wing_length, body_mass, bill_length]],
    columns=feature_columns
)


# ==================================================
# 9. 품종 예측
# ==================================================

st.header("2. 예측 결과")

if st.button("품종 예측하기", type="primary", use_container_width=True):

    prediction = model_rf.predict(input_data)[0]

    species_names = {
        "Adelie": "아델리 펭귄",
        "Chinstrap": "턱끈 펭귄",
        "Gentoo": "젠투 펭귄"
    }

    st.success(
        f"예측 결과: {species_names.get(prediction, prediction)}"
    )

    st.caption(
        "예측 결과는 입력한 값과 학습 데이터에 따라 달라질 수 있습니다."
    )

    st.write("입력한 정보")

    result_table = pd.DataFrame({
        "항목": ["날개 길이", "몸무게", "부리 길이"],
        "입력값": [
            f"{wing_length:.1f} mm",
            f"{body_mass:.0f} g",
            f"{bill_length:.1f} mm"
        ]
    })

    st.dataframe(
        result_table,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# 10. 알고리즘 정확도 비교
# ==================================================

st.header("3. 알고리즘 정확도 비교")

st.write(
    "같은 테스트 데이터에 두 알고리즘을 적용해 정확도를 비교합니다."
)

accuracy_table = pd.DataFrame({
    "알고리즘": ["랜덤 포레스트", "K-최근접 이웃"],
    "정확도 (%)": [
        rf_accuracy * 100,
        knn_accuracy * 100
    ]
})

st.bar_chart(
    accuracy_table,
    x="알고리즘",
    y="정확도 (%)"
)

accuracy_col1, accuracy_col2 = st.columns(2)

with accuracy_col1:
    st.metric(
        "랜덤 포레스트",
        f"{rf_accuracy * 100:.1f}%"
    )

with accuracy_col2:
    st.metric(
        "K-최근접 이웃",
        f"{knn_accuracy * 100:.1f}%"
    )


# ==================================================
# 11. 알고리즘 설명
# ==================================================

st.header("4. 알고리즘 알아보기")

with st.expander("랜덤 포레스트란?"):
    st.write("""
    여러 개의 의사결정나무를 만들고, 각 나무의 예측을 모아
    최종 품종을 결정하는 알고리즘입니다.

    여러 나무의 의견을 종합하기 때문에 하나의 나무만 사용하는 것보다
    안정적인 예측을 할 수 있습니다.
    """)

with st.expander("K-최근접 이웃(KNN)이란?"):
    st.write("""
    입력한 펭귄과 특징이 비슷한 펭귄 5마리를 찾고,
    그중 가장 많이 나타난 품종을 예측하는 알고리즘입니다.

    비슷한 특징을 가진 데이터는 같은 품종일 가능성이 높다는
    원리를 사용합니다.
    """)


# ==================================================
# 12. 산점도 그래프
# ==================================================

st.header("5. 펭귄 데이터 그래프")

st.write(
    "가로축은 날개 길이, 세로축은 부리 길이입니다. "
    "빨간 별표는 입력한 펭귄의 위치입니다."
)

fig, ax = plt.subplots(figsize=(9, 5))

# 품종별 데이터 표시
for species in df["species"].unique():

    species_data = df[df["species"] == species]

    ax.scatter(
        species_data["flipper_length_mm"],
        species_data["bill_length_mm"],
        label=species,
        s=55,
        alpha=0.75
    )


# 입력한 펭귄 표시
ax.scatter(
    wing_length,
    bill_length,
    color="#E53935",
    marker="*",
    s=350,
    edgecolors="black",
    linewidths=1.2,
    label="입력한 펭귄",
    zorder=5
)


# 그래프 글자와 배경
ax.set_title(
    "Penguin Species",
    fontsize=16,
    color="#172B4D"
)

ax.set_xlabel(
    "Flipper Length (mm)",
    fontsize=12,
    color="#172B4D"
)

ax.set_ylabel(
    "Bill Length (mm)",
    fontsize=12,
    color="#172B4D"
)

ax.tick_params(axis="both", colors="#172B4D")

ax.set_facecolor("#FFFFFF")
fig.patch.set_facecolor("#FFFFFF")

ax.grid(True, alpha=0.25)
ax.legend()

st.pyplot(fig)


# ==================================================
# 13. 데이터 확인
# ==================================================

with st.expander("사용한 데이터 확인하기"):
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

st.caption("데이터 출처: penguins.csv")
    st.success(
        f"예측된 품종: {species_names.get(prediction, prediction)}"
    )

    st.write("예측에 사용한 정보")

    st.dataframe(
        input_data.rename(
            columns={
                "flipper_length_mm": "날개 길이 (mm)",
                "body_mass_g": "몸무게 (g)",
                "bill_length_mm": "부리 길이 (mm)"
            }
        ),
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# 8. 알고리즘 정확도 비교
# --------------------------------------------------

st.header("3. 알고리즘 정확도 비교")

accuracy_data = pd.DataFrame({
    "알고리즘": ["랜덤 포레스트", "K-최근접 이웃"],
    "정확도 (%)": [rf_accuracy * 100, knn_accuracy * 100]
})

st.bar_chart(
    accuracy_data.set_index("알고리즘"),
    y="정확도 (%)"
)

st.write(
    f"랜덤 포레스트 정확도: **{rf_accuracy * 100:.2f}%**"
)

st.write(
    f"K-최근접 이웃 정확도: **{knn_accuracy * 100:.2f}%**"
)


# --------------------------------------------------
# 9. 알고리즘 설명
# --------------------------------------------------

st.header("4. 알고리즘 설명")

with st.expander("랜덤 포레스트란?"):
    st.write(
        "여러 개의 의사결정나무를 만들고, "
        "각 나무의 예측 결과를 모아 최종 품종을 결정하는 알고리즘입니다. "
        "여러 나무의 의견을 종합하기 때문에 하나의 나무보다 "
        "안정적인 예측을 할 수 있습니다."
    )

with st.expander("K-최근접 이웃(KNN)이란?"):
    st.write(
        "입력한 펭귄과 특징이 비슷한 펭귄 5마리를 찾고, "
        "그중 가장 많이 나타난 품종을 예측하는 알고리즘입니다. "
        "비슷한 데이터끼리는 같은 품종일 가능성이 높다는 원리를 사용합니다."
    )


# --------------------------------------------------
# 10. 산점도 그래프
# --------------------------------------------------

st.header("5. 날개 길이와 부리 길이 그래프")

st.write(
    "가로축은 날개 길이, 세로축은 부리 길이입니다. "
    "빨간 별표는 입력한 펭귄의 위치입니다."
)

fig, ax = plt.subplots(figsize=(9, 5))

# 품종별 데이터 표시
for species in df["species"].unique():

    species_data = df[df["species"] == species]

    ax.scatter(
        species_data["flipper_length_mm"],
        species_data["bill_length_mm"],
        label=species,
        s=45,
        alpha=0.75
    )


# 사용자가 입력한 값 표시
ax.scatter(
    wing_length,
    bill_length,
    color="red",
    marker="*",
    s=350,
    edgecolors="black",
    linewidths=1.2,
    label="입력한 펭귄"
)


# 그래프 제목과 축
ax.set_title(
    "Penguin Species",
    fontsize=16,
    color="#1A1A1A"
)

ax.set_xlabel(
    "Flipper Length (mm)",
    fontsize=12,
    color="#1A1A1A"
)

ax.set_ylabel(
    "Bill Length (mm)",
    fontsize=12,
    color="#1A1A1A"
)

# 글자와 배경색을 명확하게 설정
ax.tick_params(axis="both", colors="#1A1A1A")
ax.set_facecolor("#FFFFFF")
fig.patch.set_facecolor("#FFFFFF")

ax.grid(True, alpha=0.25)
ax.legend()

st.pyplot(fig)


# --------------------------------------------------
# 11. 데이터 미리보기
# --------------------------------------------------

with st.expander("사용한 데이터 확인하기"):
    st.dataframe(df, use_container_width=True)
