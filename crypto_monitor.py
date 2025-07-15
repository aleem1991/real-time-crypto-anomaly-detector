import websocket
import json
import pandas as pd
from sklearn.ensemble import IsolationForest
import requests
import time
import os
import threading

# --- Configuration ---
# Your specific Power BI Push URL.
POWER_BI_PUSH_URL = 'https://api.powerbi.com/beta/a6dbc183-3bd5-46bc-8f30-e30bf936be7e/datasets/a72263af-8268-47b4-981a-cbd10aeb854f/rows?experience=power-bi&key=AYj2dqfQa045LdTq9LVzK9jEP4KkQDi17eBgL2qAPJkmlDxbDGGDMO69V0rigW6KKR%2Fms%2ByXmo2oblfXQAFrPQ%3D%3D'

# --- Batching and Threading Setup ---
trade_batch = []
lock = threading.Lock()
BATCH_INTERVAL_SECONDS = 2.0

# --- Anomaly Detection Model ---
initial_training_data = {
    'price': [70000, 70100, 70050, 69900, 70200, 70150, 69800],
    'quantity': [0.1, 0.05, 0.2, 0.15, 0.08, 0.3, 0.12]
}
df_train = pd.DataFrame(initial_training_data)
model = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
model.fit(df_train[['price', 'quantity']])
print("Anomaly detection model has been trained.")

# --- Power BI Streaming Function ---
def push_batch_to_power_bi(batch):
    """Pushes a BATCH of data to the Power BI streaming dataset."""
    if not batch:
        return
    try:
        response = requests.post(POWER_BI_PUSH_URL, json=batch)
        if response.status_code != 200:
            print(f"Error pushing to Power BI: Status {response.status_code}, Response: {response.text}")
        else:
            print(f"--- Successfully pushed a batch of {len(batch)} trades to Power BI ---")
    except Exception as e:
        print(f"An exception occurred while pushing to Power BI: {e}")

# --- Background Worker for Sending Batches ---
def batch_sender_worker():
    """This function runs in a separate thread and sends data periodically."""
    global trade_batch
    while True:
        time.sleep(BATCH_INTERVAL_SECONDS)
        
        batch_to_send = []
        with lock:
            if trade_batch:
                batch_to_send = list(trade_batch)
                trade_batch.clear()
        
        push_batch_to_power_bi(batch_to_send)

# --- WebSocket Event Handlers ---
def on_message(ws, message):
    """
    Called for each message. It checks if the message is a valid trade,
    processes it, and adds it to a batch for sending.
    """
    trade = json.loads(message)

    # We only proceed if the message contains all necessary keys for a trade.
    if 'e' in trade and trade['e'] == 'trade' and 'p' in trade and 'q' in trade and 's' in trade and 'T' in trade:
        try:
            # All the processing code is now safely inside this 'if' and 'try' block
            symbol = trade.get('s')
            price = float(trade.get('p'))
            quantity = float(trade.get('q'))
            trade_time = pd.to_datetime(trade.get('T'), unit='ms').isoformat()

            trade_df = pd.DataFrame([[price, quantity]], columns=['price', 'quantity'])
            
            score = model.decision_function(trade_df)[0]
            prediction = model.predict(trade_df)[0]
            
            is_anomaly_flag = 1 if prediction == -1 else 0

            data_for_bi = {
                "timestamp": trade_time,
                "symbol": symbol,
                "price": price,
                "quantity": quantity,
                "anomaly_score": float(score),
                "is_anomaly": is_anomaly_flag
            }

            # Add the valid trade to our batch list
            with lock:
                trade_batch.append(data_for_bi)

            # Print to console for real-time feedback
            print(f"TRADE: {symbol} | Price: {price:.2f} | Qty: {quantity:.4f} | ANOMALY: {'YES' if is_anomaly_flag else 'No'}")
        
        except Exception as e:
            # This will catch any unexpected error during processing a trade
            print(f"Error processing trade message: {e} | Data: {trade}")

def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### WebSocket closed ###")

def on_open(ws):
    print("Connection opened. Subscribing to trade streams...")
    ws.send(json.dumps({
        "method": "SUBSCRIBE", "params": ["btcusdt@trade", "ethusdt@trade", "solusdt@trade"], "id": 1
    }))

if __name__ == "__main__":
    sender_thread = threading.Thread(target=batch_sender_worker)
    sender_thread.daemon = True
    sender_thread.start()
    
    print("Starting data stream... Batches will be sent to Power BI periodically.")
    
    socket_url = "wss://stream.binance.com:9443/ws"
    ws = websocket.WebSocketApp(socket_url,
                              on_open=on_open, on_message=on_message,
                              on_error=on_error, on_close=on_close)
    
    ws.run_forever()