import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier


# ==========================================
# 1. 웹앱 기본 설정
# ==========================================

st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 프로그램")

st.write(
    "꽃받침과 꽃잎의 길이와 너비를 입력하면 "
    "머신러닝 알고리즘이 붓꽃의 품종을 예측합니다."
)

st.caption(
    "분류 알고리즘: 랜덤 포레스트(Random Forest)"
)


# ==========================================
# 2. CSV 파일 자동 탐색 및 불러오기
# ==========================================

FEATURES = [
    "SepalLengthCm",
    "SepalWidthCm",
    "PetalLengthCm",
    "PetalWidthCm"
]

TARGET = "Species"


def find_iris_csv():

    # app.py가 있는 폴더
    current_dir = Path(__file__).resolve().parent

    # app.py가 있는 폴더의 상위 폴더
    parent_dir = current_dir.parent

    # Streamlit이 실행되는 현재 작업 폴더
    working_dir = Path.cwd()

    # 검색할 폴더 목록
    search_dirs = [
        current_dir,
        parent_dir,
        working_dir
    ]

    # 중복 폴더 제거
    search_dirs = list(dict.fromkeys(search_dirs))

    # 파일 이름이 달라도 CSV 파일을 찾을 수 있도록 설정
    candidate_files = []

    for folder in search_dirs:

        if folder.exists():

            # 같은 폴더에 있는 CSV 파일 검색
            candidate_files.extend(folder.glob("*.csv"))

            # 자주 사용하는 파일명도 확인
            candidate_files.extend([
                folder / "iris.csv",
                folder / "Iris.csv",
                folder / "Iris (1).csv"
            ])

    # 중복 파일 경로 제거
    candidate_files = list(
        dict.fromkeys(candidate_files)
    )

    # 파일이 실제로 존재하는지 확인
    candidate_files = [
        file_path
        for file_path in candidate_files
        if file_path.is_file()
    ]

    # 파일 이름이 아니라 열 이름을 기준으로 데이터 확인
    for file_path in candidate_files:

        try:
            temp_df = pd.read_csv(
                file_path,
                encoding="utf-8-sig"
            )

            temp_df.columns = (
                temp_df.columns
                .str.strip()
            )

            # 필요한 열이 모두 존재하면 해당 파일 사용
            if all(
                col in temp_df.columns
                for col in FEATURES + [TARGET]
            ):
                return file_path

        except Exception:
            continue

    return None


@st.cache_data
def load_data(file_path):

    df = pd.read_csv(
        file_path,
        encoding="utf-8-sig"
    )

    # 열 이름의 공백 제거
    df.columns = df.columns.str.strip()

    return df


# CSV 파일 검색
csv_path = find_iris_csv()

if csv_path is None:

    st.error(
        "붓꽃 데이터 CSV 파일을 찾을 수 없습니다."
    )

    st.info(
        "GitHub 저장소에 Iris CSV 파일을 업로드해주세요. "
        "파일 이름은 Iris (1).csv 또는 iris.csv 등 "
        "어떤 이름이어도 괜찮습니다."
    )

    st.write("현재 검색한 폴더:")

    st.code(
        "\n".join([
            str(Path(__file__).resolve().parent),
            str(Path(__file__).resolve().parent.parent),
            str(Path.cwd())
        ])
    )

    st.stop()


# CSV 파일 불러오기
try:

    df = load_data(str(csv_path))

except Exception as e:

    st.error(
        f"CSV 파일을 불러오는 중 오류가 발생했습니다: {e}"
    )

    st.stop()


# ==========================================
# 3. 데이터 전처리
# ==========================================

# 필요한 열만 사용
df = df[FEATURES + [TARGET]].copy()

# 숫자형 데이터로 변환
for col in FEATURES:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# 결측치 제거
df = df.dropna(
    subset=FEATURES + [TARGET]
)

# 데이터가 비어 있는지 확인
if df.empty:

    st.error(
        "분석할 데이터가 없습니다. CSV 파일을 확인해주세요."
    )

    st.stop()


# 입력값의 최소값과 최대값
min_values = df[FEATURES].min()
max_values = df[FEATURES].max()

# 품종별 데이터 확인
species_list = sorted(
    df[TARGET].unique()
)

# 데이터 정보
st.caption(
    f"분석 데이터: {len(df)}개 / "
    f"품종: {len(species_list)}종"
)


# ==========================================
# 4. 랜덤 포레스트 모델 학습
# ==========================================

X = df[FEATURES]
y = df[TARGET]

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X, y)


# ==========================================
# 5. 데이터 입력 범위 안내
# ==========================================

st.subheader("📊 데이터 입력 범위")

st.write(
    "아래는 업로드한 붓꽃 데이터에 실제로 포함된 "
    "각 항목의 최솟값과 최댓값입니다."
)

range_df = pd.DataFrame({

    "항목": [
        "꽃받침 길이",
        "꽃받침 너비",
        "꽃잎 길이",
        "꽃잎 너비"
    ],

    "최솟값(cm)": [
        min_values[col]
        for col in FEATURES
    ],

    "최댓값(cm)": [
        max_values[col]
        for col in FEATURES
    ]

})

st.dataframe(
    range_df.round(2),
    use_container_width=True,
    hide_index=True
)

st.caption(
    "입력값은 위 범위 안에서 선택할 수 있습니다. "
    "범위 밖의 값은 입력할 수 없습니다."
)


# ==========================================
# 6. 사용자 입력
# ==========================================

st.subheader("✏️ 붓꽃 크기 입력")

col1, col2 = st.columns(2)

with col1:

    st.markdown("#### 꽃받침")

    sepal_length = st.number_input(
        "꽃받침 길이 (cm)",
        min_value=float(min_values["SepalLengthCm"]),
        max_value=float(max_values["SepalLengthCm"]),
        value=float(df["SepalLengthCm"].median()),
        step=0.1,
        format="%.2f"
    )

    sepal_width = st.number_input(
        "꽃받침 너비 (cm)",
        min_value=float(min_values["SepalWidthCm"]),
        max_value=float(max_values["SepalWidthCm"]),
        value=float(df["SepalWidthCm"].median()),
        step=0.1,
        format="%.2f"
    )


with col2:

    st.markdown("#### 꽃잎")

    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=float(min_values["PetalLengthCm"]),
        max_value=float(max_values["PetalLengthCm"]),
        value=float(df["PetalLengthCm"].median()),
        step=0.1,
        format="%.2f"
    )

    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=float(min_values["PetalWidthCm"]),
        max_value=float(max_values["PetalWidthCm"]),
        value=float(df["PetalWidthCm"].median()),
        step=0.1,
        format="%.2f"
    )


# ==========================================
# 7. 품종 예측
# ==========================================

input_data = pd.DataFrame(
    [[
        sepal_length,
        sepal_width,
        petal_length,
        petal_width
    ]],
    columns=FEATURES
)

# 품종 예측
prediction = model.predict(input_data)[0]

# 품종별 예측 확률
probabilities = model.predict_proba(input_data)[0]

# 가장 높은 예측 확률
confidence = max(probabilities) * 100


# ==========================================
# 8. 예측 결과 표시
# ==========================================

st.divider()

st.subheader("🔍 예측 결과")

result_col1, result_col2 = st.columns(2)

with result_col1:

    st.success(
        f"예측된 품종: {prediction}"
    )

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
    "예측 확률은 모델의 판단을 나타내며, "
    "실제 품종일 확률을 보장하지는 않습니다."
)


# ==========================================
# 9. 꽃잎 길이와 너비 그래프
# ==========================================

st.subheader("📈 꽃잎 크기 분포")

st.write(
    "가로축은 꽃잎 길이, 세로축은 꽃잎 너비입니다. "
    "빨간색 별표는 사용자가 입력한 꽃잎의 위치입니다."
)

fig, ax = plt.subplots(
    figsize=(9, 6)
)

# 품종별 데이터 표시
for species in species_list:

    species_data = df[
        df[TARGET] == species
    ]

    ax.scatter(
        species_data["PetalLengthCm"],
        species_data["PetalWidthCm"],
        label=species,
        alpha=0.7,
        s=55
    )


# 사용자가 입력한 위치 표시
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


# 입력 위치에 값 표시
ax.annotate(
    f"입력값\n({petal_length:.2f}, {petal_width:.2f})",
    xy=(petal_length, petal_width),
    xytext=(10, 10),
    textcoords="offset points",
    fontsize=10,
    color="red"
)


# 그래프 제목과 축 설정
ax.set_xlabel("Petal Length (cm)")
ax.set_ylabel("Petal Width (cm)")

ax.set_title(
    "Iris Petal Length and Width"
)

ax.legend()
ax.grid(alpha=0.3)

st.pyplot(fig)

plt.close(fig)


# ==========================================
# 10. 입력 데이터 확인
# ==========================================

with st.expander("입력한 데이터 확인하기"):

    st.dataframe(
        input_data,
        use_container_width=True,
        hide_index=True
    )
