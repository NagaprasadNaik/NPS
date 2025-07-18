from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import dns
from uuid import uuid4
import threading
from blockchain import Blockchain
import uuid
import requests
from time import time

app = Flask(__name__)

# Fix CORS - Allow requests from your web interface
CORS(app, origins=["http://127.0.0.1:5000", "http://127.0.0.1:5001", "http://127.0.0.1:5002", "http://localhost:5000", "http://localhost:5001", "http://localhost:5002"])

"""
This layer takes care of DNS request and response packets
Additionally support packets adding new entries, which should require
authentication. Other routes implement methods required to maintain
integrity and consistency of the blockchain.
"""

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the DNS resolver object
dns_resolver = dns.dns_layer(node_identifier = node_identifier)

@app.route('/debug/alive',methods=['GET'])
def check_alive():
    response = 'The node is alive'
    return  jsonify(response),200

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/nodes/new',methods=['POST'])
def register_node():
    """
    Calls underlying functions to register new node in network
    """
    values = request.get_json()
    nodes = values.get('nodes')

    if nodes is None:
        response,return_code = "No node supplied",400
    else:
        for node in nodes:
            dns_resolver.register_node(node)
        
        response,return_code = {
        'message': 'New nodes have been added',
        'total_nodes': dns_resolver.get_network_size(),
        },201
    return jsonify(response),return_code

@app.route('/dns/new',methods=['POST'])
def new_transaction():
    """
    adds new entries into our resolver instance with ML security analysis
    """
    values = request.get_json()
    required = ['hostname', 'ip', 'port']
    bad_entries = []
    security_results = []

    for value in values:
        if all(k in values[value] for k in required):
            value = values[value]
            hostname = value['hostname']
            
            # 🔍 ML SECURITY ANALYSIS BEFORE STORAGE
            ml_result = get_ml_analysis(hostname)
            security_results.append({
                'hostname': hostname,
                'security': ml_result
            })
            
            # 🚫 OPTIONAL: Block malicious domains (uncomment to enable)
            # if ml_result.get('prediction') == 1:  # 1 = malicious
            #     bad_entries.append({
            #         'hostname': hostname,
            #         'reason': f"Blocked: {ml_result.get('label', 'malicious')} (confidence: {ml_result.get('confidence', 0)})"
            #     })
            #     continue
            
            # ✅ Store DNS record
            dns_resolver.new_entry(hostname, value['ip'], value['port'])
            
            # 📝 Store security analysis on blockchain
            store_security_analysis(hostname, ml_result)
            
        else:
            bad_entries.append(value)

    if bad_entries:
        return jsonify({
            'error': 'Some entries failed',
            'bad_entries': bad_entries,
            'security_analysis': security_results
        }), 400
    else:
        response = {
            'message': 'New DNS entry added with security analysis',
            'security_analysis': security_results
        }
        return jsonify(response), 201

@app.route('/dns/request',methods=['POST'])
def dns_lookup():
    """
    Enhanced DNS lookup with ML security analysis
    """
    values = request.get_json()
    required = ['hostname']
    if not all(k in values for k in required):
        return 'Missing values', 400

    hostname = values['hostname']
    
    # Get ML security analysis (for display only, don't store again)
    ml_result = get_ml_analysis(hostname)
    
    # NOTE: Removed duplicate store_security_analysis call
    # Security analysis should only be stored once when domain is first added
    
    try:
        host, port = dns_resolver.lookup(hostname)
        response = {
            'ip': host,
            'port': port,
            'security': ml_result  # Include security analysis
        }
        return_code = 200
    except LookupError:
        response = {
            'error': 'No existing entry',
            'security': ml_result  # Still include security info
        }
        return_code = 401

    return jsonify(response), return_code

def get_ml_analysis(hostname):
    """Call ML service for domain analysis"""
    try:
        ml_response = requests.post('http://127.0.0.1:5000/predict', 
                                  json={'domain': hostname}, 
                                  timeout=5)
        if ml_response.status_code == 200:
            return ml_response.json()
        else:
            return {'error': 'ML service error', 'label': 'unknown', 'confidence': 0.0}
    except Exception as e:
        return {'error': f'ML service unavailable: {str(e)}', 'label': 'unknown', 'confidence': 0.0}

def store_security_analysis(hostname, ml_result):
    """Store security analysis on blockchain"""
    try:
        security_transaction = {
            'type': 'security_analysis',
            'hostname': hostname,
            'ml_prediction': ml_result.get('prediction', 0),
            'ml_label': ml_result.get('label', 'unknown'),
            'confidence': ml_result.get('confidence', 0.0),
            'timestamp': time(),
            'analyzer_node': node_identifier
        }
        dns_resolver.blockchain.new_transaction(security_transaction)
    except Exception as e:
        print(f"Error storing security analysis: {e}")

@app.route('/nodes/resolve',methods=['GET'])
def consensus():
    """
    triggers the blockchain to check chain against other neighbors'
    chain, and uses the longest chain to achieve consensus
    """
    t = threading.Thread(target=dns_resolver.blockchain.resolve_conflicts)
    t.start()

    return jsonify(None), 200

@app.route('/debug/dump_chain',methods=['GET'])
@app.route('/nodes/chain',methods=['GET'])
def dump_chain():
    response = dns_resolver.dump_chain()
    return jsonify(response), 200

@app.route('/debug/dump_buffer',methods=['GET'])
def dump_buffer():
    response = dns_resolver.dump_buffer()
    return jsonify(response), 200

@app.route('/debug/force_block',methods=['GET'])
def force_block():
    # Check if there are pending transactions before mining
    buffer = dns_resolver.dump_buffer()
    if not buffer:
        return jsonify({
            "error": "No pending transactions to mine. Add DNS records first.",
            "pending_transactions": 0
        }), 400
    
    response = dns_resolver.mine_block()
    return jsonify({
        "message": f"New block mined with proof {response}",
        "transactions_included": len(buffer)
    }), 200

@app.route('/debug/get_quota',methods=['GET'])
def get_chain_quota():
    response = dns_resolver.get_chain_quota()
    return jsonify(response),200

@app.route('/api/stats',methods=['GET'])
def get_blockchain_stats():
    """
    Get comprehensive blockchain statistics for dashboard
    """
    try:
        chain = dns_resolver.blockchain.chain
        buffer = dns_resolver.blockchain.current_transactions
        nodes = list(dns_resolver.blockchain.nodes)
        
        # Calculate statistics
        total_blocks = len(chain)
        total_transactions = sum(len(block['transactions']) for block in chain)
        pending_transactions = len(buffer)
        network_size = len(nodes)
        latest_block = chain[-1] if chain else None
        
        # DNS record count and ML security stats
        dns_records = 0
        ml_analyzed = 0
        malicious_domains = 0
        safe_domains = 0
        
        for block in chain:
            for tx in block['transactions']:
                if 'hostname' in tx and 'ip' in tx:
                    dns_records += 1
                elif tx.get('type') == 'security_analysis':
                    ml_analyzed += 1
                    if tx['ml_prediction'] == 1:
                        malicious_domains += 1
                    else:
                        safe_domains += 1
        
        response = {
            'total_blocks': total_blocks,
            'total_transactions': total_transactions,
            'pending_transactions': pending_transactions,
            'dns_records': dns_records,
            'network_size': network_size,
            'node_quota': dns_resolver.get_chain_quota(),
            'latest_block': latest_block,
            'connected_nodes': nodes,
            # ML Security Stats
            'ml_analyzed': ml_analyzed,
            'malicious_domains': malicious_domains,
            'safe_domains': safe_domains,
            'threat_percentage': (malicious_domains / ml_analyzed * 100) if ml_analyzed > 0 else 0
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions',methods=['GET'])
def get_all_transactions():
    """
    Get all transactions from blockchain for transaction history
    """
    try:
        transactions = []
        for block in dns_resolver.blockchain.chain:
            for tx in block['transactions']:
                tx_data = tx.copy()
                tx_data['block_index'] = block['index']
                tx_data['block_timestamp'] = block['timestamp']
                tx_data['block_source'] = block['source']
                transactions.append(tx_data)
        
        # Sort by timestamp (newest first)
        transactions.sort(key=lambda x: x.get('block_timestamp', 0), reverse=True)
        
        return jsonify(transactions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dns-records',methods=['GET'])
def get_dns_records():
    """
    Get all DNS records for management interface
    """
    try:
        dns_records = []
        for block in dns_resolver.blockchain.chain:
            for tx in block['transactions']:
                if 'hostname' in tx and 'ip' in tx:
                    record = {
                        'hostname': tx['hostname'],
                        'ip': tx['ip'],
                        'port': tx['port'],
                        'block_index': block['index'],
                        'timestamp': block['timestamp']
                    }
                    dns_records.append(record)
        
        return jsonify(dns_records), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add-dns-record',methods=['POST'])
def add_dns_record():
    """
    Add a new DNS record to the blockchain with ML security analysis
    """
    try:
        data = request.get_json()
        required = ['hostname', 'ip', 'port']
        
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        hostname = data['hostname']
        
        # 🔍 ML SECURITY ANALYSIS BEFORE STORAGE
        ml_result = get_ml_analysis(hostname)
        
        # 🚫 OPTIONAL: Block malicious domains (uncomment to enable)
        # if ml_result.get('prediction') == 1:  # 1 = malicious
        #     return jsonify({
        #         'error': 'Domain blocked',
        #         'reason': f"Blocked: {ml_result.get('label', 'malicious')} (confidence: {ml_result.get('confidence', 0)})",
        #         'security_analysis': ml_result
        #     }), 403
        
        # ✅ Store DNS record
        dns_resolver.new_entry(hostname, data['ip'], int(data['port']))
        
        # 📝 Store security analysis on blockchain
        store_security_analysis(hostname, ml_result)
        
        return jsonify({
            'message': 'DNS record added successfully with security analysis',
            'security_analysis': ml_result
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/network-info',methods=['GET'])
def get_network_info():
    """
    Get network topology information
    """
    try:
        nodes = list(dns_resolver.blockchain.nodes)
        current_node = f"127.0.0.1:{request.environ.get('SERVER_PORT', '5001')}"
        
        network_info = {
            'current_node': current_node,
            'connected_nodes': nodes,
            'total_nodes': len(nodes) + 1,  # +1 for current node
            'node_id': dns_resolver.node_identifier[:8]  # First 8 chars of UUID
        }
        
        return jsonify(network_info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/security-feed', methods=['GET'])
def get_security_feed():
    """Get real-time security analysis feed from blockchain"""
    try:
        security_analyses = []
        
        # Scan blockchain for security transactions
        for block in dns_resolver.blockchain.chain:
            for tx in block['transactions']:
                if tx.get('type') == 'security_analysis':
                    security_analyses.append({
                        'hostname': tx['hostname'],
                        'prediction': tx['ml_prediction'],
                        'label': tx['ml_label'],
                        'confidence': tx['confidence'],
                        'timestamp': tx['timestamp'],
                        'block_index': block['index'],
                        'analyzer_node': tx['analyzer_node']
                    })
        
        # Sort by timestamp (newest first)
        security_analyses.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify(security_analyses[:50])  # Return last 50 analyses
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/threat-stats', methods=['GET'])
def get_threat_stats():
    """Get comprehensive threat statistics from blockchain"""
    try:
        total_analyzed = 0
        malicious_count = 0
        safe_count = 0
        recent_threats = []
        
        for block in dns_resolver.blockchain.chain:
            for tx in block['transactions']:
                if tx.get('type') == 'security_analysis':
                    total_analyzed += 1
                    if tx['ml_prediction'] == 1:
                        malicious_count += 1
                        recent_threats.append({
                            'hostname': tx['hostname'],
                            'confidence': tx['confidence'],
                            'timestamp': tx['timestamp']
                        })
                    else:
                        safe_count += 1
        
        # Sort recent threats by timestamp
        recent_threats.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'total_analyzed': total_analyzed,
            'malicious_domains': malicious_count,
            'safe_domains': safe_count,
            'threat_percentage': (malicious_count / total_analyzed * 100) if total_analyzed > 0 else 0,
            'recent_threats': recent_threats[:10],  # Last 10 threats
            'blockchain_blocks': len(dns_resolver.blockchain.chain),
            'network_nodes': len(dns_resolver.blockchain.nodes)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml-blockchain-integration', methods=['GET'])
def get_ml_blockchain_integration():
    """Get ML-Blockchain integration status and stats"""
    try:
        # Test ML service connectivity
        ml_status = "online"
        try:
            test_response = requests.get('http://127.0.0.1:5000/', timeout=3)
            if test_response.status_code != 200:
                ml_status = "offline"
        except:
            ml_status = "offline"
        
        # Count security transactions in blockchain
        security_tx_count = 0
        for block in dns_resolver.blockchain.chain:
            for tx in block['transactions']:
                if tx.get('type') == 'security_analysis':
                    security_tx_count += 1
        
        return jsonify({
            'ml_service_status': ml_status,
            'blockchain_status': 'online',
            'security_transactions': security_tx_count,
            'integration_active': ml_status == 'online',
            'last_analysis_time': time()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pending-transactions', methods=['GET'])
def get_pending_transactions():
    """
    Get all pending transactions from the buffer
    """
    try:
        buffer = dns_resolver.dump_buffer()
        pending_transactions = []
        
        for tx in buffer:
            tx_data = tx.copy()
            # Add timestamp for when the transaction was added (approximate)
            tx_data['added_time'] = time()
            pending_transactions.append(tx_data)
        
        return jsonify({
            'pending_transactions': pending_transactions,
            'total_pending': len(pending_transactions)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port, debug=True)

