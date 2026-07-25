import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from app.ml.features import fetch_stock_data, calculate_technical_indicators

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")


def train_model(ticker: str = "AAPL") -> dict:
    """Fetches historical market data, trains a Random Forest model, and saves model weights."""
    print(f"Fetching market training data for {ticker}...")
    df = fetch_stock_data(ticker, period="2y")
    df = calculate_technical_indicators(df)

    feature_cols = ["SMA_Signal", "RSI_14", "Volatility_20"]
    X = df[feature_cols]
    y = df["Target"]

    # Time-series aware split (no random shuffling to prevent look-ahead bias)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)

    # Save trained model to disk
    joblib.dump(clf, MODEL_PATH)
    print(f"Model successfully trained with accuracy: {acc:.2f} and saved to {MODEL_PATH}")

    return {"accuracy": float(acc), "samples": len(df)}


if __name__ == "__main__":
    train_model()