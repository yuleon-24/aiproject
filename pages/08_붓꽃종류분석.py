import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier


# --------------------------------------------------
# Page settings
# --------------------------------------------------
st.set_page_config(
    page_title="Iris Species Predictor",
    page_icon="🌸",
    layout="wide",
)


# --------------------------------------------------
# Styling
# --------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: #0b1120;
        color: #f3f4f6;
    }

    .main-title {
        font-size: 2.45rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: #f9fafb;
        margin-bottom: 0.25rem;
    }

    .main-subtitle {
        color: #9ca3af;
        font-size: 1rem;
        margin-bottom: 1.8rem;
    }

    .section-label {
        color: #818cf8;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }

    .section-title {
        color: #f9fafb;
        font-size: 1.45rem;
        font-weight: 750;
        margin-bottom: 0.3rem;
    }

    .section-description {
        color: #9ca3af;
        font-size: 0.92rem;
        margin-bottom: 1rem;
    }

    div[data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #263244;
        padding: 1rem;
        border-radius: 14px;
    }

    div[data-testid="stMetricLabel"] {
        color: #9ca3af;
    }

    div[data-testid="stMetricValue"] {
        color: #f9fafb;
    }

    div[data-testid="stSidebar"] {
        background: #111827;
    }

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Dataset loading
# --------------------------------------------------
FEATURES = [
    "SepalLengthCm",
    "SepalWidthCm",
    "PetalLengthCm",
    "PetalWidthCm",
]

FEATURE_LABELS = {
    "SepalLengthCm": "Sepal Length (cm)",
    "SepalWidthCm": "Sepal Width (cm)",
    "PetalLengthCm": "Petal Length (cm)",
    "PetalWidthCm": "Petal Width (cm)",
}

TARGET = "Species"


def normalize_column_name(name):
    """Remove spaces and symbols to make column matching easier."""
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def standardize_columns(dataframe):
    """Convert common Iris CSV column names to standard names."""
    aliases = {
        "sepallengthcm": "SepalLengthCm",
        "sepallength": "SepalLengthCm",
        "sepal_length": "SepalLengthCm",
        "sepalwidthcm": "SepalWidthCm",
        "sepalwidth": "SepalWidthCm",
        "sepal_width": "SepalWidthCm",
        "petallengthcm": "PetalLengthCm",
        "petallength": "PetalLengthCm",
        "petal_length": "PetalLengthCm",
        "petalwidthcm": "PetalWidthCm",
        "petalwidth": "PetalWidthCm",
        "petal_width": "PetalWidthCm",
        "species": "Species",
        "class": "Species",
        "target": "Species",
        "variety": "Species",
    }

    renamed = {}

    for column in dataframe.columns:
        normalized = normalize_column_name(column)
        if normalized in aliases:
            renamed[column] = aliases[normalized]

    dataframe = dataframe.rename(columns=renamed)

    missing = [column for column in FEATURES + [TARGET] if column not in dataframe.columns]
    if missing:
        raise ValueError(
            "The CSV does not contain the required Iris columns: "
            + ", ".join(missing)
        )

    dataframe = dataframe[FEATURES + [TARGET]].copy()

    for column in FEATURES:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    dataframe = dataframe.dropna(subset=FEATURES + [TARGET])
    dataframe[TARGET] = dataframe[TARGET].astype(str)

    return dataframe


def find_iris_csv():
    """Look for a suitable Iris CSV in common project folders."""
    current_folder = Path.cwd()

    search_folders = [
        current_folder,
        current_folder / "data",
        current_folder.parent,
        current_folder.parent / "data",
    ]

    preferred_names = [
        "iris.csv",
        "Iris.csv",
        "iris (1).csv",
        "Iris (1).csv",
    ]

    checked_paths = []

    for folder in search_folders:
        if not folder.exists():
            continue

        for filename in preferred_names:
            path = folder / filename
            if path.exists() and path not in checked_paths:
                checked_paths.append(path)

        for path in folder.glob("*.csv"):
            if path not in checked_paths:
                checked_paths.append(path)

    for path in checked_paths:
        try:
            for encoding in ["utf-8", "utf-8-sig", "cp949", "latin1"]:
                try:
                    raw_data = pd.read_csv(path, encoding=encoding)
                    standardized = standardize_columns(raw_data)
                    if len(standardized) > 0:
                        return standardized, path.name
                except (UnicodeDecodeError, ValueError, pd.errors.ParserError):
                    continue
        except Exception:
            continue

    raise FileNotFoundError(
        "No suitable Iris CSV file was found. "
        "Place iris.csv in the same folder as app.py or in a data folder."
    )


@st.cache_data
def load_dataset():
    return find_iris_csv()


try:
    df, dataset_filename = load_dataset()
except FileNotFoundError as error:
    st.error(str(error))
    st.info(
        "Upload your Iris CSV to the same folder as app.py, "
        "or place it in a folder named data."
    )
    st.stop()


# --------------------------------------------------
# Train model
# --------------------------------------------------
X = df[FEATURES]
y = df[TARGET]

model = RandomForestClassifier(
    n_estimators=250,
    random_state=42,
    class_weight="balanced",
)

model.fit(X, y)

species_list = sorted(y.unique().tolist())


# --------------------------------------------------
# English labels for charts and prediction results
# --------------------------------------------------
def get_english_species_label(species, index=0):
    """
    Return an English display label.
    This prevents Korean text in CSV species names from appearing in charts.
    """
    value = str(species).strip().lower()

    english_names = {
        "iris-setosa": "Setosa",
        "setosa": "Setosa",
        "iris-versicolor": "Versicolor",
        "versicolor": "Versicolor",
        "iris-virginica": "Virginica",
        "virginica": "Virginica",
    }

    if value in english_names:
        return english_names[value]

    return f"Class {index + 1}"


species_display_names = {
    species: get_english_species_label(species, index)
    for index, species in enumerate(species_list)
}


# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(
    '<div class="main-title">Iris Species Predictor</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="main-subtitle">
        Predict an Iris flower species using four measurements.
        Explore the dataset and compare your input with the original samples.
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Sidebar: input measurements
# --------------------------------------------------
st.sidebar.markdown("## Flower Measurements")
st.sidebar.caption("Adjust the four measurements below.")

input_values = {}

for feature in FEATURES:
    minimum = float(df[feature].min())
    maximum = float(df[feature].max())

    # Add a small margin so the slider is not restricted to the dataset range.
    margin = max((maximum - minimum) * 0.05, 0.1)
    slider_min = max(0.0, minimum - margin)
    slider_max = maximum + margin

    default_value = float(df[feature].median())

    input_values[feature] = st.sidebar.slider(
        FEATURE_LABELS[feature],
        min_value=float(slider_min),
        max_value=float(slider_max),
        value=float(default_value),
        step=0.1,
    )

predict_button = st.sidebar.button(
    "Predict Species",
    type="primary",
)


# --------------------------------------------------
# Prediction
# --------------------------------------------------
input_df = pd.DataFrame([input_values], columns=FEATURES)

prediction = model.predict(input_df)[0]
probabilities = model.predict_proba(input_df)[0]

predicted_index = species_list.index(prediction)
predicted_label = species_display_names[prediction]
confidence = float(probabilities[predicted_index]) * 100


# --------------------------------------------------
# Prediction summary
# --------------------------------------------------
st.markdown(
    '<div class="section-label">Prediction Result</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Predicted flower species</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    'The model uses a Random Forest classifier trained on the loaded Iris dataset.'
    '</div>',
    unsafe_allow_html=True,
)

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.metric("Predicted Species", predicted_label)

with metric_col2:
    st.metric("Model Confidence", f"{confidence:.1f}%")

with metric_col3:
    st.metric("Dataset Samples", f"{len(df):,}")


# --------------------------------------------------
# Input summary
# --------------------------------------------------
st.markdown("### Your Measurements")

measurement_columns = st.columns(4)

for column, feature in zip(measurement_columns, FEATURES):
    with column:
        st.metric(
            FEATURE_LABELS[feature],
            f"{input_values[feature]:.1f}",
        )


# --------------------------------------------------
# Probability chart
# --------------------------------------------------
st.markdown("---")

st.markdown(
    '<div class="section-label">Model Analysis</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Prediction probabilities</div>',
    unsafe_allow_html=True,
)

probability_data = pd.DataFrame(
    {
        "Species": [
            species_display_names[species]
            for species in model.classes_
        ],
        "Probability": probabilities * 100,
    }
).sort_values("Probability", ascending=False)

st.bar_chart(
    probability_data.set_index("Species"),
    y="Probability",
    color="#818cf8",
)

st.caption(
    "Probabilities show how strongly the model associates the measurements "
    "with each species. They are not a guarantee of the actual species."
)


# --------------------------------------------------
# English-only graph
# --------------------------------------------------
st.markdown("---")

st.markdown(
    '<div class="section-label">Data Visualization</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Petal measurement map</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    'Compare your flower with the original dataset. '
    'The red star marks your selected measurements.'
    '</div>',
    unsafe_allow_html=True,
)

# Use an English font and English-only text in the graph.
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor("#111827")
ax.set_facecolor("#111827")

colors = ["#818cf8", "#34d399", "#fbbf24"]

for index, species in enumerate(species_list):
    species_data = df[df[TARGET] == species]

    # Use the English display name instead of the original CSV label.
    english_label = species_display_names[species]

    ax.scatter(
        species_data["PetalLengthCm"],
        species_data["PetalWidthCm"],
        label=english_label,
        color=colors[index % len(colors)],
        s=65,
        alpha=0.8,
        edgecolors="none",
    )

ax.scatter(
    input_values["PetalLengthCm"],
    input_values["PetalWidthCm"],
    marker="*",
    s=450,
    color="#f87171",
    edgecolors="white",
    linewidths=1.5,
    label="Your Input",
    zorder=10,
)

ax.annotate(
    (
        "Your Input\n"
        f"({input_values['PetalLengthCm']:.2f}, "
        f"{input_values['PetalWidthCm']:.2f})"
    ),
    (
        input_values["PetalLengthCm"],
        input_values["PetalWidthCm"],
    ),
    xytext=(12, 12),
    textcoords="offset points",
    color="white",
    fontsize=10,
    fontweight="bold",
)

ax.set_xlabel(
    "Petal Length (cm)",
    color="#e5e7eb",
    fontsize=11,
)

ax.set_ylabel(
    "Petal Width (cm)",
    color="#e5e7eb",
    fontsize=11,
)

ax.set_title(
    "Iris Petal Distribution",
    color="#f9fafb",
    fontsize=15,
    fontweight="bold",
    pad=15,
)

ax.tick_params(colors="#d1d5db")
ax.grid(color="#374151", alpha=0.45, linestyle="--")

for spine in ax.spines.values():
    spine.set_color("#4b5563")

legend = ax.legend(
    facecolor="#1f2937",
    edgecolor="#374151",
    labelcolor="white",
)

for text in legend.get_texts():
    text.set_fontsize(10)

fig.tight_layout()
st.pyplot(fig, use_container_width=True)
plt.close(fig)


# --------------------------------------------------
# Feature importance
# --------------------------------------------------
st.markdown("---")

st.markdown(
    '<div class="section-title">Feature importance</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    'This chart shows how much each measurement contributed to the trained model.'
    '</div>',
    unsafe_allow_html=True,
)

importance_data = pd.DataFrame(
    {
        "Feature": [FEATURE_LABELS[feature] for feature in FEATURES],
        "Importance": model.feature_importances_,
    }
).sort_values("Importance", ascending=False)

st.bar_chart(
    importance_data.set_index("Feature"),
    y="Importance",
    color="#34d399",
)


# --------------------------------------------------
# Dataset preview
# --------------------------------------------------
with st.expander("View dataset preview"):
    st.caption(f"Loaded file: {dataset_filename}")
    st.dataframe(df.head(20), use_container_width=True)

    st.caption("Dataset summary")
    st.dataframe(
        df[FEATURES].describe().round(2),
        use_container_width=True,
    )
