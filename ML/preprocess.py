import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv("data/synth.csv")

print(df.head())
dropped_columns = ["Student_ID", "Final_Score"]
df = df.drop(columns=dropped_columns)

features = [col for col in df.columns if col not in ["Pass_Fail"]]
df.dropna(subset=features, inplace=True)
df.dropna(subset=["Pass_Fail"], inplace=True)

le = LabelEncoder()
df["Pass_Fail"] = le.fit_transform(df["Pass_Fail"])

print(df.head())

X = df[features]
y = df["Pass_Fail"]

# One-hot encode the categorical features


scaler = StandardScaler()
X = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LogisticRegression()
model.fit(X_train, y_train)

# Save model and scaler together with metadata
model_data = {"model": model, "scaler": scaler, "feature_names": features}

filename = "..\\BE\\app\\models\\student_prediction_model.pkl"
with open(filename, "wb") as file:
    pickle.dump(model_data, file)

print(f"Model and scaler saved to {filename}")
print(f"Feature names: {features}")
