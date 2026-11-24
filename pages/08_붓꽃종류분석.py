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
# Page settings and style
# --------------------------------------------------
st.set_page_config(
    page_title="Iris Species Predictor",
    page_icon="🌸",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b1120;
        color: #f3f4f6;
    }
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #f9fafb;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #9ca3af;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #263244;
        padding: 1rem;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Load Iris dataset
# --------------------------------------------------
iris = load_iris()

X = pd.DataFrame(
    iris.data,
    columns=[
        "Sepal Length",
        "Sepal Width",
        "Petal Length",
        "Petal Width",
    ],
)

y = iris.target
species_names = iris.target_names

# English-only names for chart labels
chart_species_names = ["Setosa", "Versicolor", "Virginica"]


# --------------------------------------------------
# Train/test split for model accuracy comparison
# --------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)


# --------------------------------------------------
# Three classification algorithms
# --------------------------------------------------
models = {
    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        random_state=42,
    ),
    "Support Vector Machine (SVM)": make_pipeline(
        StandardScaler(),
        SVC(
            kernel="rbf",
            probability=True,
            random_state=42,
        ),
    ),
    "K-Nearest Neighbors (KNN)": make_pipeline(
        StandardScaler(),
        KNeighborsClassifier(n_neighbors=5),
    ),
}

# Train each model and calculate test accuracy
test_accuracies = {}

for model_name, model in models.items():
    model.fit(X_train, y_train)
    test_prediction = model.predict(X_test)
    test_accuracies[model_name] = accuracy_score(
        y_test,
        test_prediction,
    )


# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(
    '<div class="main-title">Iris Species Predictor</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Enter four flower measurements and compare predictions from three
    classification algorithms.
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Input controls
# --------------------------------------------------
st.sidebar.header("Flower Measurements")
st.sidebar.caption(
    "The input ranges are based on the minimum and maximum values "
    "in the Iris dataset."
)

measurement_ranges = {
    "Sepal Length": (4.3, 7.9),
    "Sepal Width": (2.0, 4.4),
    "Petal Length": (1.0, 6.9),
    "Petal Width": (0.1, 2.5),
}

st.sidebar.markdown("**Input ranges**")
for feature, (minimum, maximum) in measurement_ranges.items():
    st.sidebar.write(
        f"{feature}: {minimum}–{maximum} cm"
    )

st.sidebar.divider()

sepal_length = st.sidebar.slider(
    "Sepal Length (cm)",
    min_value=4.3,
    max_value=7.9,
    value=5.8,
    step=0.1,
)

sepal_width = st.sidebar.slider(
    "Sepal Width (cm)",
    min_value=2.0,
    max_value=4.4,
    value=3.0,
    step=0.1,
)

petal_length = st.sidebar.slider(
    "Petal Length (cm)",
    min_value=1.0,
    max_value=6.9,
    value=4.0,
    step=0.1,
)

petal_width = st.sidebar.slider(
    "Petal Width (cm)",
    min_value=0.1,
    max_value=2.5,
    value=1.2,
    step=0.1,
)

input_data = pd.DataFrame(
    [[sepal_length, sepal_width, petal_length, petal_width]],
    columns=X.columns,
)


# --------------------------------------------------
# Predict with all three algorithms
# --------------------------------------------------
st.subheader("Prediction Comparison")

results = []

for model_name, model in models.items():
    predicted_class = int(model.predict(input_data)[0])
    probabilities = model.predict_proba(input_data)[0]
    confidence = float(probabilities[predicted_class]) * 100

    results.append(
        {
            "Algorithm": model_name,
            "Predicted Species": species_names[predicted_class].title(),
            "Confidence": confidence,
            "Test Accuracy": test_accuracies[model_name] * 100,
        }
    )

results_df = pd.DataFrame(results)

# Display results in a table
display_results = results_df.copy()
display_results["Confidence"] = display_results["Confidence"].map(
    lambda value: f"{value:.1f}%"
)
display_results["Test Accuracy"] = display_results["Test Accuracy"].map(
    lambda value: f"{value:.1f}%"
)

st.dataframe(
    display_results,
    hide_index=True,
    use_container_width=True,
)

# Highlight each model's prediction
metric_columns = st.columns(3)

for column, result in zip(metric_columns, results):
    with column:
        st.metric(
            label=result["Algorithm"],
            value=result["Predicted Species"],
            delta=f"Confidence: {result['Confidence']:.1f}%",
        )


# --------------------------------------------------
# Graphs: length on X-axis, width on Y-axis
# --------------------------------------------------
st.divider()
st.subheader("Measurement Maps")
st.caption(
    "The colored dots show the Iris dataset. "
    "The red star shows your entered measurements."
)

# English labels and font are used inside the charts.
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.patch.set_facecolor("#111827")

chart_settings = [
    {
        "ax": axes[0],
        "x_column": "Petal Length",
        "y_column": "Petal Width",
        "x_value": petal_length,
        "y_value": petal_width,
        "title": "Petal Length vs. Petal Width",
    },
    {
        "ax": axes[1],
        "x_column": "Sepal Length",
        "y_column": "Sepal Width",
        "x_value": sepal_length,
        "y_value": sepal_width,
        "title": "Sepal Length vs. Sepal Width",
    },
]

colors = ["#818cf8", "#34d399", "#fbbf24"]

for settings in chart_settings:
    ax = settings["ax"]
    ax.set_facecolor("#111827")

    for class_index, species_name in enumerate(chart_species_names):
        class_data = X[y == class_index]

        ax.scatter(
            class_data[settings["x_column"]],
            class_data[settings["y_column"]],
            label=species_name,
            color=colors[class_index],
            s=55,
            alpha=0.8,
            edgecolors="none",
        )

    ax.scatter(
        settings["x_value"],
        settings["y_value"],
        marker="*",
        s=380,
        color="#f87171",
        edgecolors="white",
        linewidths=1.2,
        label="Your Input",
        zorder=10,
    )

    ax.set_title(
        settings["title"],
        color="#f9fafb",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel(
        f"{settings['x_column']} (cm)",
        color="#e5e7eb",
    )
    ax.set_ylabel(
        f"{settings['y_column']} (cm)",
        color="#e5e7eb",
    )

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
# Algorithm explanations
# --------------------------------------------------
st.divider()
st.subheader("How the Algorithms Work")

with st.expander("1. Random Forest"):
    st.write(
        """
        Random Forest creates many decision trees using different samples
        and feature combinations from the training data.

        Each tree predicts a species. The model combines the trees' votes
        and chooses the species with the most votes.

        **Strength:** Often performs well on varied data and can model
        complex relationships.
        """
    )

with st.expander("2. Support Vector Machine (SVM)"):
    st.write(
        """
        SVM searches for a boundary that separates the species while
        keeping the margin between classes as wide as possible.

        This app uses an RBF kernel, which can create curved boundaries
        when the classes cannot be separated well by a straight line.

        **Strength:** Effective for datasets with clear class boundaries.
        """
    )

with st.expander("3. K-Nearest Neighbors (KNN)"):
    st.write(
        """
        KNN finds the five training flowers closest to the input flower
        and predicts the species that appears most often among those
        neighbors.

        The measurements are standardized first so that features with
        larger numerical values do not dominate the distance calculation.

        **Strength:** Simple to understand and bases predictions on
        nearby examples.
        """
    )


# --------------------------------------------------
# Dataset information
# --------------------------------------------------
with st.expander("About the dataset"):
    st.write(
        """
        The Iris dataset contains 150 flower samples from three species:
        Setosa, Versicolor, and Virginica. Each sample has four measurements:
        sepal length, sepal width, petal length, and petal width.

        The displayed input ranges are the minimum and maximum values
        found in this dataset.
        """
    )
