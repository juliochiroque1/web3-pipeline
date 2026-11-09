#  Ethereum Whale Alert & Data Pipeline (v1.0)

An automated, containerized ETL pipeline deployed on AWS EC2 that monitors the Ethereum Mainnet in real time, persists high-value whale transactions into PostgreSQL, and dispatches instant alerts via the Telegram Bot API.

##  Architecture & Tech Stack

* Cloud Infrastructure: AWS EC2 (Linux)
* Containerization:  Docker & Docker Compose
* Backend / ETL: Python 3 (`requests`, `psycopg2`)
* Blockchain RPC: Alchemy API (Ethereum JSON-RPC `eth_blockNumber` & `eth_getBlockByNumber`)
* Database: PostgreSQL 15
* Alerting: Telegram Bot API

## ⚙️ How It Works (ETL Flow)

1. Extract (Dynamic Discovery): Queries the Ethereum Mainnet every 12 seconds via Alchemy JSON-RPC to fetch the latest block and its full transaction payload.
2. Transform (Hexadecimal & Wei Conversion): Parses raw hexadecimal values, converts transaction amounts from Wei to ETH ($10^{18}$), and filters for whale movements:
   * Database Storage Threshold: Transactions > 30 ETH.
   * Real-Time Alert Threshold: Mega-whale transactions > 1,000 ETH.
3. Load (Persistence & Notification): Inserts filtered records into the PostgreSQL `eth_whales` table (`DECIMAL(38,18)` precision) and exports block snapshots to JSON.

## Database Schema (`ETH.sql`)

```sql
CREATE TABLE eth_whales (
    hash VARCHAR(80) PRIMARY KEY,
    DE VARCHAR(50),
    para VARCHAR(50),
    monto_real DECIMAL(38,18)
);