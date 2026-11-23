import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier

# ----------------------------------
# 1. 웹앱 기본 설정
# ----------------------------------

st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 프로그램")

st.write(
    "꽃받침과 꽃잎의 크기를 입력하면 "
    "머신러닝 알고리즘이 붓꽃의 품종을 예측합니다."
)

st.caption(
    "분류 알고리즘: 랜덤 포레스트(Random Forest)"
)

# ----------------------------------
# 2. 데이터 불러오기
# ----------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("iris.csv")

    # 열 이름 앞뒤의 공백 제거
    df.columns = df.columns.str.strip()

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "iris.csv 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 CSV 파일을 넣어주세요."
    )
    st.stop()


# ----------------------------------
# 3. 데이터 전처리
# ----------------------------------

features = [
    "SepalLengthCm",
    "SepalWidthCm",
    "PetalLengthCm",
    "PetalWidthCm"
]

target = "Species"

# 필요한 열이 있는지 확인
if not all(col in df.columns for col in features + [target]):
    st.error(
        "CSV 파일의 열 이름이 예상한 형식과 다릅니다. "
        "Iris 데이터의 열 이름을 확인해주세요."
    )
    st.write("현재 CSV 열 이름:", df.columns.tolist())
    st.stop()

# 분석에 필요한 데이터만 사용
df = df[features + [target]].copy()

# 숫자형 데이터로 변환
for col in features:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# 결측치 제거
df = df.dropna()

if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()

X = df[features]
y = df[target]

# ----------------------------------
# 4. 랜덤 포레스트 모델 생성
# ----------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X, y)

# ----------------------------------
# 5. 데이터 범위 확인
# ----------------------------------

st.subheader("📊 데이터 입력 범위")

st.write(
    "아래 범위는 업로드한 붓꽃 데이터에 실제로 "
    "포함된 최솟값과 최댓값입니다."
)

range_df = pd.DataFrame({
    "항목": [
        "꽃받침 길이",
        "꽃받침 너비",
        "꽃잎 길이",
        "꽃잎 너비"
    ],
    "최솟값(cm)": [
        X[col].min() for col in features
    ],
    "최댓값(cm)": [
        X[col].max() for col in features
    ]
})

st.dataframe(
    range_df.round(2),
    use_container_width=True,
    hide_index=True
)

st.caption(
    "입력값은 위 범위 안에서 선택할 수 있습니다. "
    "범위 밖의 값은 예측에 사용하지 않습니다."
)

# ----------------------------------
# 6. 사용자 입력
# ----------------------------------

st.subheader("✏️ 붓꽃 크기 입력")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 꽃받침")

    sepal_length = st.number_input(
        "꽃받침 길이 (cm)",
        min_value=float(X["SepalLengthCm"].min()),
        max_value=float(X["SepalLengthCm"].max()),
        value=float(X["SepalLengthCm"].median()),
        step=0.1,
        format="%.2f"
    )

    sepal_width = st.number_input(
        "꽃받침 너비 (cm)",
        min_value=float(X["SepalWidthCm"].min()),
        max_value=float(X["SepalWidthCm"].max()),
        value=float(X["SepalWidthCm"].median()),
        step=0.1,
        format="%.2f"
    )

with col2:
    st.markdown("#### 꽃잎")

    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=float(X["PetalLengthCm"].min()),
        max_value=float(X["PetalLengthCm"].max()),
        value=float(X["PetalLengthCm"].median()),
        step=0.1,
        format="%.2f"
    )

    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=float(X["PetalWidthCm"].min()),
        max_value=float(X["PetalWidthCm"].max()),
        value=float(X["PetalWidthCm"].median()),
        step=0.1,
        format="%.2f"
    )

# ----------------------------------
# 7. 품종 예측
# ----------------------------------

input_data = pd.DataFrame(
    [[
        sepal_length,
        sepal_width,
        petal_length,
        petal_width
    ]],
    columns=features
)

prediction = model.predict(input_data)[0]

probabilities = model.predict_proba(input_data)[0]

confidence = max(probabilities) * 100

st.divider()

st.subheader("🔍 예측 결과")

result_col1, result_col2 = st.columns(2)

with result_col1:
    st.success(f"예측된 품종: {prediction}")

    st.metric(
        label="모델의 예측 확률",
        value=f"{confidence:.1f}%"
    )

with result_col2:
    st.markdown("#### 품종별 예측 확률")

    probability_df = pd.DataFrame({
        "품종": model.classes_,
        "예측 확률(%)": probabilities * 100
    })

    probability_df = probability_df.sort_values(
        "예측 확률(%)",
        ascending=False
    )

    st.dataframe(
        probability_df.round(2),
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "예측 확률은 학습된 모델의 판단을 나타내며, "
    "실제 품종일 확률을 보장하지는 않습니다."
)

# ----------------------------------
# 8. 꽃잎 길이와 너비 그래프
# ----------------------------------

st.subheader("📈 꽃잎 크기 분포")

st.write(
    "가로축은 꽃잎 길이, 세로축은 꽃잎 너비입니다. "
    "별표는 사용자가 입력한 꽃잎의 위치를 나타냅니다."
)

fig, ax = plt.subplots(figsize=(9, 6))

# 품종별 색상으로 기존 데이터 표시
for species in df[target].unique():

    species_data = df[df[target] == species]

    ax.scatter(
        species_data["PetalLengthCm"],
        species_data["PetalWidthCm"],
        label=species,
        alpha=0.7,
        s=55
    )

# 사용자 입력값 표시
ax.scatter(
    petal_length,
    petal_width,
    marker="*",
    s=350,
    color="red",
    edgecolors="black",
    linewidths=1.2,
    label="Your Input",
    zorder=5
)

# 입력 위치에 설명 표시
ax.annotate(
    f"입력값\n({petal_length:.2f}, {petal_width:.2f})",
    xy=(petal_length, petal_width),
    xytext=(10, 10),
    textcoords="offset points",
    fontsize=10,
    color="red"
)

ax.set_xlabel("Petal Length (cm)")
ax.set_ylabel("Petal Width (cm)")
ax.set_title("Iris Petal Length and Width")

ax.legend()
ax.grid(alpha=0.3)

st.pyplot(fig)

# ----------------------------------
# 9. 입력 데이터 확인
# ----------------------------------

with st.expander("입력한 데이터 확인하기"):

    st.dataframe(
        input_data,
        use_container_width=True,
        hide_index=True
    )
