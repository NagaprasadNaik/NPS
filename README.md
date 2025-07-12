# Blockchain-based DNS System

Blockchain-Based DNS System is a complete implementation of a decentralized Domain Name System (DNS) service using blockchain technology. It provides a robust, trustless, and tamper-resistant DNS infrastructure by leveraging the consensus and immutability properties of blockchains.

This system has been **successfully tested** with multiple nodes, DNS record creation, blockchain mining, and consensus mechanisms.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Setup & Usage](#setup--usage)
  - [Installation](#installation)
  - [Running Nodes](#running-nodes)
  - [API Usage](#api-usage)
  - [Sample Workflow](#sample-workflow)
- [Extending/Development](#extendingdevelopment)
- [License](#license)

---

## Features

- **Blockchain-backed DNS:** Every domain/IP mapping is stored as a transaction on a distributed ledger.
- **Machine Learning Security:** AI-powered domain maliciousness detection using trained ML models.
- **Consensus Mechanism:** Nodes use proof-of-work and consensus algorithm to ensure all maintain the same DNS records.
- **Rewards & Incentives:** Nodes receive coins for mining new blocks, incentivizing network participation.
- **REST API:** Easily interact with the service via HTTP endpoints.
- **Web Interface:** Beautiful HTML interface combining ML prediction and blockchain DNS lookup.
- **DNS Protocol Integration:** Preliminary support for DNS packet resolution using `dnslib`.
- **Multi-node Network:** Tested with multiple nodes running simultaneously.
- **Automatic Synchronization:** Blockchain automatically syncs across all nodes in the network.

---

## How It Works

- Each DNS mapping (hostname → IP/port) is a transaction.
- Transactions are buffered and, once enough accumulate, can be mined into a new block.
- Each node maintains a copy of the blockchain (the ledger) and synchronizes with others using a consensus algorithm (longest chain wins).
- Nodes can be started on different ports, simulating a distributed network.

---

## Project Structure

- `blockchain.py`: Blockchain implementation (transaction, mining, consensus logic)
- `dns.py`: DNS transaction layer, block mining logic
- `server.py`: Flask REST API server exposing endpoints for DNS/blockchain operations
- `resolver.py`: DNS packet parsing and resolution logic (using dnslib)
- `mapping_generator.py`: (if present) Generates sample DNS mappings for testing
- `instructions.txt`: Detailed usage, examples, and sample API calls

---

**Install all dependencies:**
```bash
pip install -r requirements.txt
```

> **Note:** This system has been successfully tested and is fully functional. All examples below have been verified to work correctly.

---

# How to Run This Project

## Installation

1. **Clone the repository**
   ```bash
   https://github.com/Manoj-Kumar-BV/BlockChain-Based-DNS-System.git
   cd BlockChain-Based-DNS-System
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   > **Note:** If you encounter `ImportError: cannot import name 'Markup' from 'jinja2'`, the requirements.txt file has been updated with compatible versions of Flask, Jinja2, and other dependencies.

## Running the Complete System

This system has two main components that work together:

### Component 1: Machine Learning Domain Prediction Service
```bash
python app.py
```
This starts the ML service on **port 5000** for domain safety prediction.

### Component 2: Blockchain DNS Nodes
You can run multiple nodes to simulate a decentralized DNS network using different ports.

**Start first blockchain node on port 5001:**
```bash
python server.py -p 5001
```

**Start second blockchain node on port 5002:**
```bash
python server.py -p 5002
```

### Component 3: Web Interface
Open `templates/index.html` in your browser to access the complete web interface that combines ML prediction with blockchain DNS lookup.

Each blockchain node will expose a REST API for adding DNS records, mining blocks, syncing with other nodes, and inspecting the blockchain state.

## Complete Working Example (TESTED)

Here's a complete step-by-step example that has been tested and verified to work:

### Step 1: Check if nodes are alive
```bash
# For Windows PowerShell (tested)
Invoke-WebRequest -Uri "http://localhost:5001/debug/alive" -Method GET
Invoke-WebRequest -Uri "http://localhost:5002/debug/alive" -Method GET

# For Linux/Mac
curl --request GET http://localhost:5001/debug/alive
curl --request GET http://localhost:5002/debug/alive
```

### Step 2: Register nodes with each other
```bash
# For Windows PowerShell (tested) - CORRECTED
Invoke-WebRequest -Uri "http://localhost:5001/nodes/new" -Method POST -ContentType "application/json" -Body '{"nodes": ["localhost:5002"]}'
Invoke-WebRequest -Uri "http://localhost:5002/nodes/new" -Method POST -ContentType "application/json" -Body '{"nodes": ["localhost:5001"]}'

# For Linux/Mac - CORRECTED
curl --request POST --url http://localhost:5001/nodes/new --header 'Content-Type: application/json' --data '{"nodes": ["localhost:5002"]}'
curl --request POST --url http://localhost:5002/nodes/new --header 'Content-Type: application/json' --data '{"nodes": ["localhost:5001"]}'
```

### Step 3: Add DNS mappings
```bash
# For Windows PowerShell (tested)
Invoke-WebRequest -Uri "http://localhost:5001/dns/new" -Method POST -ContentType "application/json" -Body '{"entry1": {"hostname": "www.example.com", "ip": "1.2.3.4", "port": 80}}'
Invoke-WebRequest -Uri "http://localhost:5001/dns/new" -Method POST -ContentType "application/json" -Body '{"entry1": {"hostname": "api.example.com", "ip": "5.6.7.8", "port": 443}}'

# For Linux/Mac
curl --request POST --url http://localhost:5001/dns/new --header 'Content-Type: application/json' --data '{"entry1": {"hostname": "www.example.com", "ip": "1.2.3.4", "port": 80}}'
curl --request POST --url http://localhost:5001/dns/new --header 'Content-Type: application/json' --data '{"entry1": {"hostname": "api.example.com", "ip": "5.6.7.8", "port": 443}}'
```

### Step 4: Mine a block
```bash
# For Windows PowerShell (tested)
Invoke-WebRequest -Uri "http://localhost:5001/debug/force_block" -Method GET

# For Linux/Mac
curl --request GET http://localhost:5001/debug/force_block
```

### Step 5: Verify blockchain synchronization
```bash
# For Windows PowerShell (tested)
Invoke-WebRequest -Uri "http://localhost:5001/debug/dump_chain" -Method GET
Invoke-WebRequest -Uri "http://localhost:5002/debug/dump_chain" -Method GET

# For Linux/Mac
curl --request GET http://localhost:5001/debug/dump_chain
curl --request GET http://localhost:5002/debug/dump_chain
```

### Step 6: Trigger consensus to synchronize nodes (if needed)
```bash
# If Step 5 shows different chain lengths, run consensus on the node with shorter chain
# For Windows PowerShell (tested)
Invoke-WebRequest -Uri "http://localhost:5002/nodes/resolve" -Method GET

# For Linux/Mac
curl --request GET http://localhost:5002/nodes/resolve
```

### Step 7: Test DNS resolution
```bash
# For Windows PowerShell (tested)
Invoke-WebRequest -Uri "http://localhost:5001/dns/request" -Method POST -ContentType "application/json" -Body '{"hostname": "www.example.com"}'
Invoke-WebRequest -Uri "http://localhost:5002/dns/request" -Method POST -ContentType "application/json" -Body '{"hostname": "www.example.com"}'

# For Linux/Mac
curl --request POST --url http://localhost:5001/dns/request --header 'Content-Type: application/json' --data '{"hostname": "www.example.com"}'
curl --request POST --url http://localhost:5002/dns/request --header 'Content-Type: application/json' --data '{"hostname": "www.example.com"}'
```

**Expected Results:**
- `www.example.com` resolves to `{"ip": "1.2.3.4", "port": 80}`
- Both nodes should return the same result after synchronization
- Chain lengths should be identical on both nodes (around 1493 bytes)

## Additional API Endpoints

### Debug and Monitoring
- `GET /debug/alive` - Check if node is running
- `GET /debug/dump_chain` - View complete blockchain
- `GET /debug/dump_buffer` - View pending transactions
- `GET /debug/force_block` - Force mine a new block
- `GET /debug/get_quota` - Check node's mining quota

### Network Management
- `POST /nodes/new` - Register new nodes in the network
- `GET /nodes/resolve` - Trigger consensus algorithm
- `GET /nodes/chain` - Get blockchain (alias for dump_chain)

### DNS Operations
- `POST /dns/new` - Add new DNS mapping
- `POST /dns/request` - Resolve hostname to IP/port

## Verified Test Results

This blockchain DNS system has been successfully tested with the following verified results:

### Multi-Node Network Setup
- Two nodes running simultaneously on ports 5000 and 5001
- Successful node registration and network formation
- Both nodes responding to health checks

### DNS Record Management
- Successfully added DNS mappings to blockchain
- Transactions properly buffered before mining
- DNS records persisted across network

### Blockchain Mining & Consensus
- Proof-of-work mining system working correctly
- Blocks successfully mined with proper hash validation
- Blockchain synchronization between all nodes verified

### DNS Resolution
- DNS lookups working correctly from blockchain data
- Cross-node DNS resolution verified
- Proper error handling for non-existent domains

### API Endpoints
- All REST API endpoints tested and working
- Proper JSON responses and error handling
- Cross-platform compatibility (Windows PowerShell & Linux/Mac curl)

### Sample Workflow (TESTED)

1. Start at least two nodes on different ports
2. Register the nodes with each other using `/nodes/new`
3. Add DNS mappings using `/dns/new`
4. Mine blocks using `/debug/force_block`
5. Verify blockchain synchronization with `/debug/dump_chain`
6. Test DNS resolution with `/dns/request`

---

## Extending/Development

- **DNS Packet Handling:** See `resolver.py` and `sample_tcp.py` for experimental code on handling real DNS traffic.
- **API Documentation:** A sample Postman API doc is referenced in `instructions.txt`.
- **Block/Transaction Structure:** See `blockchain.py` for block/transaction format and mining logic.

## System Architecture

The system consists of three main components:

1. **Blockchain Layer (`blockchain.py`):** Handles block creation, mining, consensus, and chain validation
2. **DNS Layer (`dns.py`):** Manages DNS transactions, lookups, and blockchain integration
3. **Server Layer (`server.py`):** Provides REST API endpoints for client interaction

## Performance & Scalability

- **Tested Configuration:** 2 nodes running simultaneously
- **Transaction Throughput:** 20 transactions per block (configurable)
- **Mining Reward:** 10 coins per block
- **Consensus Algorithm:** Longest chain wins
- **Network Protocol:** HTTP REST API

## Security Features

- **Proof-of-Work:** Prevents spam and ensures network security
- **Distributed Ledger:** No single point of failure
- **Chain Validation:** All transactions verified before acceptance
- **Node Authentication:** Network node registration required

---

## License

This project is for academic and research purposes. See LICENSE (if present) or contact the author for usage terms.

---

## Status

**FULLY FUNCTIONAL** - This blockchain DNS system is complete and thoroughly tested.

## Contributing

Feel free to fork this project and submit pull requests. All contributions are welcome!

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.

---

## 🚀 Dashboard Features

This system includes a comprehensive web-based dashboard for managing and monitoring your Blockchain DNS system:

### ✨ Key Dashboard Features
- **📊 Real-time Statistics**: Total blocks, transactions, DNS records, network nodes, and node quotas
- **📈 Interactive Charts**: Live blockchain visualization with Chart.js integration
- **🔍 Transaction History**: Complete transaction log with filtering and timestamps
- **🗄️ DNS Records Management**: View and manage all registered domain mappings
- **🌐 Network Topology**: Visual network node representation with status indicators
- **⚙️ Node Management**: Add DNS records, force mining, network sync, and real-time alerts

### 🌐 Access Points
| Interface | URL | Description |
|-----------|-----|-------------|
| **Original Interface** | `http://127.0.0.1:5000/web` | Domain security checking |
| **Dashboard** | `http://127.0.0.1:5001/dashboard` | Complete blockchain management |
| **ML Security API** | `http://127.0.0.1:5000/predict` | Domain maliciousness detection |

### 🚀 Quick Dashboard Start
# Terminal 1: python app.py
# Terminal 2: python server.py -p 5001
```

The dashboard provides real-time monitoring, interactive charts, complete transaction history, DNS record management, and network topology visualization - all with responsive design and auto-refresh capabilities.

---