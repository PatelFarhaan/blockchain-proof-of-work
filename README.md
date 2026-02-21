# Smart Chain Supply with Blockchain

A blockchain-based supply chain management system that tracks cargo shipments with tamper detection. Built with Python and Flask, this application implements a custom blockchain with proof-of-work consensus, RSA-signed transactions, and real-time email alerts when data integrity violations are detected.

## Tech Stack

- **Backend:** Python 3, Flask
- **Database:** MongoDB (via MongoEngine)
- **Cryptography:** PyCrypto (RSA key pairs, SHA-256 hashing)
- **Email Alerts:** Flask-Mail (SMTP)
- **Frontend:** HTML/JavaScript (minimal UI)

## Features

- Custom blockchain implementation with proof-of-work consensus
- RSA public/private key wallet generation and management
- Digitally signed transactions with verification
- Peer-to-peer node network with conflict resolution
- Cargo tracking with position, temperature, and weight monitoring
- Automated tamper detection with email alerts when blockchain data is modified
- REST API for all blockchain operations
- Web-based UI for node management and network visualization

## Prerequisites

- Python 3.7+
- MongoDB 4.0+
- pip

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/<username>/Smart-Chain-Suppy-with-Blockchain.git
   cd Smart-Chain-Suppy-with-Blockchain
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start MongoDB**
   ```bash
   mongod --dbpath /path/to/data
   ```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/admin` |
| `FLASK_DEBUG` | Enable Flask debug mode | `false` |
| `MAIL_SERVER` | SMTP server for email alerts | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP server port | `587` |
| `MAIL_USERNAME` | SMTP email username | - |
| `MAIL_PASSWORD` | SMTP email password | - |
| `ALERT_RECIPIENT_EMAIL` | Email to receive tamper alerts | `admin@example.com` |

## How to Run

```bash
python node.py
```

The application starts on `http://0.0.0.0:80` by default.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Node management UI |
| `GET` | `/network` | Network visualization UI |
| `POST` | `/wallet` | Create a new wallet (key pair) |
| `GET` | `/wallet` | Load existing wallet |
| `GET` | `/balance` | Get wallet balance |
| `POST` | `/transaction` | Create a new transaction |
| `GET` | `/transactions` | Get open (pending) transactions |
| `POST` | `/mine` | Mine a new block with cargo data |
| `GET` | `/chain` | Get the full blockchain |
| `GET` | `/all-transactions` | Get all stored transactions from DB |
| `POST` | `/broadcast-transaction` | Broadcast transaction to peers |
| `POST` | `/broadcast-block` | Broadcast mined block to peers |
| `POST` | `/resolve-conflicts` | Resolve blockchain conflicts across nodes |
| `POST` | `/node` | Add a peer node |
| `DELETE` | `/node/<node_url>` | Remove a peer node |
| `GET` | `/nodes` | List all peer nodes |

## Project Structure

```
Smart-Chain-Suppy-with-Blockchain/
├── node.py                  # Flask application and API routes
├── blockchain.py            # Blockchain core logic
├── block.py                 # Block data structure
├── transaction.py           # Transaction data structure
├── wallet.py                # RSA wallet (key generation, signing)
├── requirements.txt         # Python dependencies
├── compiled_files_cleanup.sh # Cleanup script for .pyc files
├── ui/
│   ├── node.html            # Node management frontend
│   └── network.html         # Network visualization frontend
└── utility/
    ├── __init__.py
    ├── hash_util.py          # SHA-256 hashing utilities
    ├── printable.py          # Base class for string representation
    └── verification.py       # Proof-of-work and chain verification
```

## License

This project is licensed under the MIT License.
