from flask import Flask, jsonify, request
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
    response = dns_resolver.mine_block()
    return jsonify(f"New block mined with proof {response}"), 200

@app.route('/debug/get_quota',methods=['GET'])
def get_chain_quota():
    response = dns_resolver.get_chain_quota()
    return jsonify(response),200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port, debug=True)