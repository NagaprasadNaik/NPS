from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import dns
from uuid import uuid4
import threading
from blockchain import Blockchain
import uuid

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
    adds new entries into our resolver instance
    """
    values = request.get_json()
    required = ['hostname', 'ip', 'port']
    bad_entries = []

    for value in values:
        if all(k in values[value] for k in required):
            value = values[value]
            dns_resolver.new_entry(value['hostname'],value['ip'],value['port'])
        else:
            bad_entries.append(value)

    if bad_entries:
        return jsonify(bad_entries),400
    else:
        response = 'New DNS entry added'
        return jsonify(response), 201

@app.route('/dns/request',methods=['POST'])
def dns_lookup():
    """
    receives a dns request and responses after resolving
    """
    values = request.get_json()
    required = ['hostname']
    if not all(k in values for k in required):
        return 'Missing values', 400

    try:
        host,port = dns_resolver.lookup(values['hostname'])
        response = {
        'ip':host,
        'port': port
        }
        return_code = 200
    except LookupError:
        response = "No existing entry"
        return_code = 401

    return jsonify(response), return_code

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
        
        # DNS record count
        dns_records = 0
        for block in chain:
            for tx in block['transactions']:
                if 'hostname' in tx:
                    dns_records += 1
        
        response = {
            'total_blocks': total_blocks,
            'total_transactions': total_transactions,
            'pending_transactions': pending_transactions,
            'dns_records': dns_records,
            'network_size': network_size,
            'node_quota': dns_resolver.get_chain_quota(),
            'latest_block': latest_block,
            'connected_nodes': nodes
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
    Add a new DNS record to the blockchain
    """
    try:
        data = request.get_json()
        required = ['hostname', 'ip', 'port']
        
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        dns_resolver.new_entry(data['hostname'], data['ip'], int(data['port']))
        
        return jsonify({'message': 'DNS record added successfully'}), 201
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

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port, debug=True)

