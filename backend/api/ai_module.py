import pandas as pd 
from sklearn.ensemble import IsolationForest
import joblib
from django.utils import timezone
from .models import Transaction

def prepare_data(transactions):
    df = pd.DataFrame(transactions)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['day'] = df['timestamp'].dt.day
    df['month'] = df['timestamp'].dt.month
    df['amount']= df['amount'].astype(float)
    return df[['amount', 'hour', 'day', 'month']]

def train_model():
    transactions = list(Transaction.objects.all().values())
    if not transactions:
        print("No transactions found.Cannot train model")
        return
    data = prepare_data(transactions)
    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42
    )
    model.fit(data)
    joblib.dump(model, "api/isolation_forest.pk1")
    print("Model trained successfully")

def detect_anomaly(transaction):
    model=joblib.load("api/isolation_forest.pk1")

    df = prepare_data([transaction])
    pred = model.predict(df)[0]
    score = model.decision_function(df)[0]
    return {
        "is_anomaly": pred == -1,
        "risk_score": float(score)
    }