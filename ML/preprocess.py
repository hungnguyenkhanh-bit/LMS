import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor

MODEL_PATH = "..\\BE\\app\\models\\student_prediction_model.pkl"
df = pd.read_csv("data/student_gpa_dataset_new.csv")

dropped_columns = ["student_id"]
df = df.drop(columns=dropped_columns)

features = [col for col in df.columns if col not in ["gpa"]]
df.dropna(subset=features, inplace=True)
df.dropna(subset=["gpa"], inplace=True)

# le = LabelEncoder()
# df["GPA"] = le.fit_transform(df["GPA"])

print(df.head())

X = df[features]
y = df["gpa"]

# One-hot encode the categorical features


# scaler = StandardScaler()
# X = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(X_train)

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
)

model.fit(X_train, y_train)
predictions = model.predict([[90, 90, 90, 90]])
print("predictions", predictions)
print(model.score(X_test, y_test))
print(model.feature_importances_)

# Save model and scaler together with metadata
# model_data = {"model": model, "scaler": scaler, "feature_names": features}

filename = "..\\BE\\app\\models\\student_prediction_model.pkl"
with open(filename, "wb") as file:
    pickle.dump(model, file)

filename = "..\\BE\\app\\models\\student_prediction_model.pkl"
with open(filename, "rb") as file:
    model = pickle.load(file)

predictions = model.predict([[93.5, 70.6, 85.1, 31.6]])
print("predictions", predictions)

print(f"Model and scaler saved to {filename}")
print(f"Feature names: {features}")


