import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier


# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide",
)

st.title("🌸 붓꽃 품종 예측 프로그램")
st.write(
    "꽃받침과 꽃잎의 길이·너비를 입력하면 "
    "세 가지 분류 알고리즘으로 붓꽃 품종을 예측합니다."
)


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
iris = load_iris()

feature_names = [
    "꽃받침 길이",
    "꽃받침 너비",
    "꽃잎 길이",
    "꽃잎 너비",
]

# 데이터셋의 실제 열 이름
X = pd.DataFrame(
    iris.data,
    columns=feature_names,
)

y = iris.target

# 그래프에 사용할 영어 품종명
english_species_names = [
    "Setosa",
    "Versicolor",
    "Virginica",
]

# 화면에 표시할 한국어 품종명
korean_species_names = [
    "세토사",
    "버시컬러",
    "버지니카",
]


# --------------------------------------------------
# 학습 데이터와 테스트 데이터 분리
# --------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)


# --------------------------------------------------
# 세 가지 분류 알고리즘
# --------------------------------------------------
models = {
    "랜덤 포레스트": RandomForestClassifier(
        n_estimators=200,
        random_state=42,
    ),

    "서포트 벡터 머신(SVM)": make_pipeline(
        StandardScaler(),
        SVC(
            kernel="rbf",
            probability=True,
            random_state=42,
        ),
    ),

    "K-최근접 이웃(KNN)": make_pipeline(
        StandardScaler(),
        KNeighborsClassifier(n_neighbors=5),
    ),
}


# --------------------------------------------------
# 모델 학습 및 정확도 계산
# --------------------------------------------------
test_accuracies = {}

for model_name, model in models.items():
    model.fit(X_train, y_train)

    test_predictions = model.predict(X_test)

    test_accuracies[model_name] = accuracy_score(
        y_test,
        test_predictions,
    )


# --------------------------------------------------
# 입력 범위 안내
# --------------------------------------------------
st.subheader("1. 꽃의 측정값 입력")

st.info(
    "입력 범위는 붓꽃 데이터셋에 포함된 각 측정값의 "
    "최솟값과 최댓값을 기준으로 설정했습니다. 단위는 cm입니다."
)

range_col1, range_col2, range_col3, range_col4 = st.columns(4)

with range_col1:
    st.metric("꽃받침 길이", "4.3 ~ 7.9 cm")

with range_col2:
    st.metric("꽃받침 너비", "2.0 ~ 4.4 cm")

with range_col3:
    st.metric("꽃잎 길이", "1.0 ~ 6.9 cm")

with range_col4:
    st.metric("꽃잎 너비", "0.1 ~ 2.5 cm")


# --------------------------------------------------
# 사용자 입력
# --------------------------------------------------
st.sidebar.header("꽃의 측정값")

sepal_length = st.sidebar.slider(
    "꽃받침 길이 (cm)",
    min_value=4.3,
    max_value=7.9,
    value=5.8,
    step=0.1,
)

sepal_width = st.sidebar.slider(
    "꽃받침 너비 (cm)",
    min_value=2.0,
    max_value=4.4,
    value=3.0,
    step=0.1,
)

petal_length = st.sidebar.slider(
    "꽃잎 길이 (cm)",
    min_value=1.0,
    max_value=6.9,
    value=4.0,
    step=0.1,
)

petal_width = st.sidebar.slider(
    "꽃잎 너비 (cm)",
    min_value=0.1,
    max_value=2.5,
    value=1.2,
    step=0.1,
)

input_data = pd.DataFrame(
    [[sepal_length, sepal_width, petal_length, petal_width]],
    columns=feature_names,
)


# --------------------------------------------------
# 세 모델의 예측 결과
# --------------------------------------------------
st.divider()
st.subheader("2. 알고리즘별 예측 결과")

results = []

for model_name, model in models.items():
    predicted_class = int(model.predict(input_data)[0])

    probabilities = model.predict_proba(input_data)[0]
    confidence = float(probabilities[predicted_class]) * 100

    results.append(
        {
            "알고리즘": model_name,
            "예측 품종": korean_species_names[predicted_class],
            "예측 확률": confidence,
            "테스트 정확도": test_accuracies[model_name] * 100,
        }
    )

results_df = pd.DataFrame(results)

display_results = results_df.copy()
display_results["예측 확률"] = display_results["예측 확률"].map(
    lambda value: f"{value:.1f}%"
)
display_results["테스트 정확도"] = display_results["테스트 정확도"].map(
    lambda value: f"{value:.1f}%"
)

st.dataframe(
    display_results,
    hide_index=True,
    use_container_width=True,
)

# 대표 모델: 랜덤 포레스트
main_model = models["랜덤 포레스트"]
main_prediction = int(main_model.predict(input_data)[0])
main_probability = main_model.predict_proba(input_data)[0][main_prediction] * 100

st.success(
    f"대표 모델인 랜덤 포레스트의 예측 품종은 "
    f"**{korean_species_names[main_prediction]}**입니다. "
    f"예측 확률은 **{main_probability:.1f}%**입니다."
)


# --------------------------------------------------
# 입력값 표시
# --------------------------------------------------
st.subheader("입력한 측정값")

input_col1, input_col2, input_col3, input_col4 = st.columns(4)

with input_col1:
    st.metric("꽃받침 길이", f"{sepal_length:.1f} cm")

with input_col2:
    st.metric("꽃받침 너비", f"{sepal_width:.1f} cm")

with input_col3:
    st.metric("꽃잎 길이", f"{petal_length:.1f} cm")

with input_col4:
    st.metric("꽃잎 너비", f"{petal_width:.1f} cm")


# --------------------------------------------------
# 산점도
# X축은 길이, Y축은 너비
# 그래프 안의 문구는 영어로 표시하여 한글 깨짐 방지
# --------------------------------------------------
st.divider()
st.subheader("3. 입력값의 위치 확인")
st.write(
    "색깔별 점은 기존 붓꽃 데이터이고, "
    "빨간 별표는 사용자가 입력한 측정값입니다."
)

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.patch.set_facecolor("#111827")

# 꽃잎 길이와 너비
petal_ax = axes[0]
petal_ax.set_facecolor("#111827")

# 꽃받침 길이와 너비
sepal_ax = axes[1]
sepal_ax.set_facecolor("#111827")

colors = ["#818cf8", "#34d399", "#fbbf24"]

for class_index, species_name in enumerate(english_species_names):
    class_data = X[y == class_index]

    petal_ax.scatter(
        class_data["꽃잎 길이"],
        class_data["꽃잎 너비"],
        label=species_name,
        color=colors[class_index],
        s=55,
        alpha=0.8,
        edgecolors="none",
    )

    sepal_ax.scatter(
        class_data["꽃받침 길이"],
        class_data["꽃받침 너비"],
        label=species_name,
        color=colors[class_index],
        s=55,
        alpha=0.8,
        edgecolors="none",
    )

# 사용자가 입력한 꽃잎 측정값
petal_ax.scatter(
    petal_length,
    petal_width,
    marker="*",
    s=380,
    color="#f87171",
    edgecolors="white",
    linewidths=1.2,
    label="Your Input",
    zorder=10,
)

# 사용자가 입력한 꽃받침 측정값
sepal_ax.scatter(
    sepal_length,
    sepal_width,
    marker="*",
    s=380,
    color="#f87171",
    edgecolors="white",
    linewidths=1.2,
    label="Your Input",
    zorder=10,
)

# 그래프 제목과 축 이름은 영어로 표시
petal_ax.set_title("Petal Length vs. Petal Width", color="white")
petal_ax.set_xlabel("Petal Length (cm)", color="white")
petal_ax.set_ylabel("Petal Width (cm)", color="white")

sepal_ax.set_title("Sepal Length vs. Sepal Width", color="white")
sepal_ax.set_xlabel("Sepal Length (cm)", color="white")
sepal_ax.set_ylabel("Sepal Width (cm)", color="white")

for ax in axes:
    ax.tick_params(colors="#d1d5db")
    ax.grid(color="#374151", alpha=0.4, linestyle="--")

    for spine in ax.spines.values():
        spine.set_color("#4b5563")

    legend = ax.legend(
        facecolor="#1f2937",
        edgecolor="#374151",
        labelcolor="white",
    )

    for text in legend.get_texts():
        text.set_fontsize(9)

fig.tight_layout()
st.pyplot(fig, use_container_width=True)
plt.close(fig)


# --------------------------------------------------
# 알고리즘 작동 원리
# --------------------------------------------------
st.divider()
st.subheader("4. 분류 알고리즘의 작동 원리")

with st.expander("랜덤 포레스트"):
    st.write(
        """
        여러 개의 의사결정나무를 만들어 각각 품종을 예측하게 합니다.
        각 나무의 예측 결과를 모아 가장 많은 표를 받은 품종을 최종 결과로 선택합니다.

        **쉽게 말하면:** 여러 판단 기준의 결과를 모아 다수결로 결정하는 방식입니다.
        """
    )

with st.expander("서포트 벡터 머신(SVM)"):
    st.write(
        """
        품종별 데이터가 서로 잘 구분되도록 데이터 사이에 경계선을 찾습니다.
        이 프로그램은 직선으로 구분하기 어려운 경우에도 사용할 수 있는
        RBF 커널을 사용합니다.

        **쉽게 말하면:** 측정값을 기준으로 품종 사이의 경계선을 찾는 방식입니다.
        """
    )

with st.expander("K-최근접 이웃(KNN)"):
    st.write(
        """
        입력한 꽃과 측정값이 가장 가까운 기존 꽃 5개를 찾습니다.
        그 5개 중 가장 많이 나타난 품종을 예측 결과로 선택합니다.

        **쉽게 말하면:** 입력한 꽃과 비슷한 꽃들을 찾아 다수의 품종을 선택하는 방식입니다.
        """
    )


# --------------------------------------------------
# 정확도 비교 안내
# --------------------------------------------------
st.divider()
st.subheader("5. 결과 비교 시 참고할 점")

st.write(
    """
    - **예측 품종:** 각 알고리즘이 입력값을 보고 예측한 품종입니다.
    - **예측 확률:** 해당 알고리즘이 예측 품종에 부여한 확률입니다.
    - **테스트 정확도:** 학습에 사용하지 않은 테스트 데이터에서 맞힌 비율입니다.

    테스트 정확도는 데이터를 나누는 방식과 알고리즘 설정에 따라 달라질 수 있습니다.
    예측 확률이 높더라도 실제 품종을 반드시 맞힌다는 뜻은 아닙니다.
    """
)
