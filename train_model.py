
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

df = pd.read_csv("data/bus_data.csv")
df.columns = df.columns.str.strip()

X = df[["distance_km", "speed_kmh", "hour",
        "traffic", "stops_remaining"]]
y = df["travel_time_min"]

preprocessor = ColumnTransformer([
    ("traffic", OneHotEncoder(handle_unknown="ignore"),
     ["traffic"])
], remainder="passthrough")

model = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(
        n_estimators=100, random_state=42
    ))
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)

with open("bus_eta_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model trained successfully!")
print(f"Test MAE: {mae:.2f} minutes")
print("Saved model: bus_eta_model.pkl")