import streamlit as st
import pandas as pd
import plotly.express as px

from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score


# -----------------------------
# 1. 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="AI 펭귄 품종 예측",
    page_icon="🐧",
    layout="wide"
)

st.title("🐧 AI 펭귄 품종 예측 시스템")
st.write(
    "펭귄의 신체 특징을 입력하면 "
    "3가지 머신러닝 알고리즘이 품종을 예측합니다."
)


# -----------------------------
# 2. 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    data = pd.read_csv("penguins.csv")

    # 예측에 필요한 변수만 사용
    features = [
        "flipper_length_mm",
        "body_mass_g",
        "bill_length_mm"
    ]

    data = data.dropna(
        subset=features + ["species"]
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


# -----------------------------
# 3. 학습 데이터와 정답 분리
# -----------------------------
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


# -----------------------------
# 4. 분류 알고리즘 3개 선정
# -----------------------------
models = {
    "랜덤 포레스트": RandomForestClassifier(
        n_estimators=200,
        random_state=42
    ),

    "K-최근접 이웃": make_pipeline(
        StandardScaler(),
        KNeighborsClassifier(n_neighbors=5)
    ),

    "서포트 벡터 머신": make_pipeline(
        StandardScaler(),
        SVC(kernel="rbf")
    )
}


# -----------------------------
# 5. 모델 학습 및 평가
# -----------------------------
@st.cache_resource
def train_models():
    trained_models = {}
    results = []

    for name, model in models.items():
        model.fit(X_train, y_train)

        prediction = model.predict(X_test)

        accuracy = accuracy_score(
            y_test,
            prediction
        )

        trained_models[name] = model

        results.append({
            "알고리즘": name,
            "정확도": accuracy
        })

    return trained_models, pd.DataFrame(results)


trained_models, results = train_models()


# -----------------------------
# 6. 입력값 범위 안내
# -----------------------------
st.subheader("1. 펭귄의 신체 정보 입력")

st.info(
    "입력 범위는 실제 데이터의 최솟값과 최댓값을 기준으로 합니다.\n\n"
    "- 날개 길이: 172~231 mm\n"
    "- 몸무게: 2,700~6,300 g\n"
    "- 부리 길이: 32.1~59.6 mm"
)


# -----------------------------
# 7. 사용자 입력
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    flipper_length = st.slider(
        "날개 길이 (mm)",
        min_value=172,
        max_value=231,
        value=200
    )

with col2:
    body_mass = st.slider(
        "몸무게 (g)",
        min_value=2700,
        max_value=6300,
        value=4000,
        step=100
    )

with col3:
    bill_length = st.slider(
        "부리 길이 (mm)",
        min_value=32.1,
        max_value=59.6,
        value=45.0,
        step=0.1
    )


# 입력값을 모델에 맞는 형태로 변환
user_data = pd.DataFrame(
    [[flipper_length, body_mass, bill_length]],
    columns=[
        "flipper_length_mm",
        "body_mass_g",
        "bill_length_mm"
    ]
)


# -----------------------------
# 8. 세 알고리즘의 예측 결과
# -----------------------------
st.subheader("2. AI 품종 예측 결과")

prediction_results = []

for name, model in trained_models.items():
    predicted_species = model.predict(user_data)[0]

    prediction_results.append({
        "알고리즘": name,
        "예측 품종": predicted_species
    })

prediction_df = pd.DataFrame(prediction_results)

# 랜덤 포레스트를 대표 예측 모델로 선정
main_prediction = trained_models[
    "랜덤 포레스트"
].predict(user_data)[0]

st.success(
    f"랜덤 포레스트의 예측 결과: {main_prediction}"
)

st.write("### 알고리즘별 예측 비교")

st.dataframe(
    prediction_df,
    hide_index=True,
    use_container_width=True
)


# -----------------------------
# 9. 알고리즘별 정확도 비교
# -----------------------------
st.subheader("3. 분류 알고리즘 정확도 비교")

results["정확도(%)"] = (
    results["정확도"] * 100
).round(2)

st.dataframe(
    results[["알고리즘", "정확도(%)"]],
    hide_index=True,
    use_container_width=True
)

fig_accuracy = px.bar(
    results,
    x="알고리즘",
    y="정확도(%)",
    color="알고리즘",
    text="정확도(%)",
    title="3가지 알고리즘의 예측 정확도 비교",
    labels={
        "알고리즘": "분류 알고리즘",
        "정확도(%)": "정확도 (%)"
    }
)

fig_accuracy.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig_accuracy.update_layout(
    yaxis_range=[0, 100],
    showlegend=False
)

st.plotly_chart(
    fig_accuracy,
    use_container_width=True
)


# -----------------------------
# 10. 입력한 펭귄의 위치 시각화
# -----------------------------
st.subheader("4. 펭귄의 신체 특징 그래프")

st.write(
    "가로축은 날개 길이(mm), "
    "세로축은 부리 길이(mm)입니다. "
    "색상은 실제 품종을 나타내며, 빨간 별은 사용자가 입력한 펭귄입니다."
)

fig = px.scatter(
    df,
    x="flipper_length_mm",
    y="bill_length_mm",
    color="species",
    hover_data=["body_mass_g"],
    labels={
        "flipper_length_mm": "날개 길이 (mm)",
        "bill_length_mm": "부리 길이 (mm)",
        "species": "실제 품종",
        "body_mass_g": "몸무게 (g)"
    },
    title="펭귄의 날개 길이와 부리 길이 분포"
)

fig.add_scatter(
    x=[flipper_length],
    y=[bill_length],
    mode="markers",
    marker=dict(
        symbol="star",
        size=20,
        color="red",
        line=dict(width=2, color="black")
    ),
    name="입력한 펭귄",
    hovertemplate=(
        "입력한 펭귄<br>"
        "날개 길이: %{x} mm<br>"
        "부리 길이: %{y} mm"
        "<extra></extra>"
    )
)

fig.update_layout(
    xaxis_title="날개 길이 (mm)",
    yaxis_title="부리 길이 (mm)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------
# 11. 모델 작동 원리
# -----------------------------
st.subheader("5. 분류 알고리즘 작동 원리")

with st.expander("랜덤 포레스트"):
    st.write(
        "여러 개의 의사결정나무를 만들어 각각 예측한 뒤, "
        "가장 많이 선택된 품종을 최종 결과로 결정합니다. "
        "여러 나무의 결과를 종합하므로 한 개의 나무보다 "
        "안정적인 예측을 할 수 있습니다."
    )

with st.expander("K-최근접 이웃"):
    st.write(
        "새로운 펭귄과 신체 특징이 비슷한 기존 펭귄 5마리를 찾습니다. "
        "그중 가장 많이 나타나는 품종을 예측 결과로 선택합니다. "
        "이 알고리즘은 입력값의 크기에 영향을 받으므로 "
        "표준화를 적용했습니다."
    )

with st.expander("서포트 벡터 머신"):
    st.write(
        "품종을 가장 잘 구분할 수 있는 경계선을 찾습니다. "
        "RBF 커널을 사용하여 직선으로 구분하기 어려운 "
        "복잡한 데이터도 구분할 수 있습니다. "
        "입력값의 크기에 영향을 받으므로 표준화를 적용했습니다."
    )


# -----------------------------
# 12. 최종 안내
# -----------------------------
st.caption(
    "본 프로그램은 학습 데이터의 특징을 바탕으로 품종을 예측합니다. "
    "예측 결과는 실제 품종과 다를 수 있습니다."
)
