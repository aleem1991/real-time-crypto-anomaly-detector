# Real-Time Cryptocurrency Trade Anomaly Detection

A live, end-to-end data application that detects and visualizes anomalous cryptocurrency trades in real-time. This project showcases skills in data engineering, machine learning, cloud deployment, and business intelligence.

### Key Features

*   **Real-Time Data Ingestion:** Connects directly to the Binance WebSocket API to stream live trade data for multiple cryptocurrencies.
*   **Machine Learning Model:** Utilizes an Isolation Forest algorithm from Scikit-learn to score each trade for anomalies in real-time based on its price and quantity.
*   **Cloud-Based Architecture:** The Python data pipeline is deployed on a PythonAnywhere cloud server, making it a true, scalable web application.
*   **Live BI Dashboard:** Pushes the processed data to the Power BI REST API to populate an interactive, self-updating dashboard that visualizes anomalies as they happen.

### Tech Stack

*   **Data Source:** Binance WebSocket API
*   **Data Processing/ML:** Python (Pandas, Scikit-learn)
*   **Cloud Deployment:** PythonAnywhere
*   **Data Visualization:** Microsoft Power BI
*   **Version Control:** Git / GitHub

### Architecture

This project follows a decoupled, cloud-based architecture:

1.  **Data Source:** The Binance API streams raw trade data.
2.  **Processing Engine (PythonAnywhere):** A Python script running 24/7 on a PythonAnywhere server consumes the data stream. For each trade, it:
    *   Parses the incoming JSON data.
    *   Applies the pre-trained Isolation Forest model to generate an anomaly score.
    *   Batches the results (timestamp, symbol, price, quantity, score, anomaly flag).
3.  **BI & Visualization (Power BI):** The Python script pushes the data batches to a Power BI Streaming Dataset via its REST API. A Power BI report connected to this dataset updates in real-time to reflect the live data.

### How to Run Locally

1.  Clone the repository: `git clone [your-repo-link]`
2.  Install dependencies: `pip install -r requirements.txt`
3.  Create a Power BI Streaming Dataset and get the Push URL.
4.  Paste the Push URL into the `POWER_BI_PUSH_URL` variable in `crypto_monitor.py`.
5.  Run the script: `python crypto_monitor.py`
