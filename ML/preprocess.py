import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv("data/student_gpa_dataset.csv")

dropped_columns = ["Student_ID", "Letter_Grade"]
df = df.drop(columns=dropped_columns)

features = [col for col in df.columns if col not in ["GPA"]]
df.dropna(subset=features, inplace=True)
df.dropna(subset=["GPA"], inplace=True)

# le = LabelEncoder()
# df["GPA"] = le.fit_transform(df["GPA"])

print(df.head())

X = df[features]
y = df["GPA"]

# One-hot encode the categorical features


scaler = StandardScaler()
X = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
)

model.fit(X_train, y_train)
predictions = model.predict(X_test)
print(predictions)
print(model.score(X_test, y_test))

# Save model and scaler together with metadata
model_data = {"model": model, "scaler": scaler, "feature_names": features}

filename = "..\\BE\\app\\models\\student_prediction_model.pkl"
with open(filename, "wb") as file:
    pickle.dump(model_data, file)

print(f"Model and scaler saved to {filename}")
print(f"Feature names: {features}")


