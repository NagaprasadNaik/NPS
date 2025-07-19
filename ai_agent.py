"""
Offline AI Agent for Blockchain DNS System
Uses Ollama for local AI inference without internet dependency
"""

import requests
import json
from flask import jsonify
import time

class BlockchainDNSAgent:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        # Use llama as primary model
        self.model = "llama3.2:1b"  # Primary model
        self.fallback_model = "qwen2.5:0.5b"  # Backup model if needed
        self.system_context = """
You are an expert AI assistant for a Blockchain-based DNS System. You help users understand:

1. **Blockchain DNS Technology**: How decentralized DNS works, consensus mechanisms, mining
2. **Security Features**: AI-powered malicious domain detection, threat analysis
3. **Dashboard Analytics**: Explaining statistics, charts, and real-time data
4. **System Operations**: How to add DNS records, mine blocks, manage nodes
5. **Technical Concepts**: Proof of work, transactions, blockchain structure

Key System Features:
- Blockchain-backed DNS records with immutable storage
- AI security analysis for domain threats
- Multi-node consensus network
- Real-time analytics dashboard
- REST API for system interaction

Always provide clear, helpful explanations. When explaining dashboard data, be specific about what the numbers mean and their significance.
"""

    def is_ollama_available(self):
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                # Try primary model first, then fallback
                primary_available = any(model['name'].startswith(self.model.split(':')[0]) for model in models)
                fallback_available = any(model['name'].startswith(self.fallback_model.split(':')[0]) for model in models)
                
                if primary_available:
                    return True
                elif fallback_available:
                    print(f"Using fallback model: {self.fallback_model}")
                    self.model = self.fallback_model
                    return True
                return False
            return False
        except:
            return False

    def pull_model(self):
        """Pull the AI model if not available"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": self.model},
                timeout=300
            )
            return response.status_code == 200
        except:
            return False

    def get_system_stats(self):
        """Get all real-time dashboard statistics from all /api/* endpoints"""
        try:
            stats = {}
            import requests
            # Main API endpoints (update ports as needed for your deployment)
            api_ports = [5001, 5002]
            # Fetch from main node (5001) for global stats
            try:
                stats_response = requests.get("http://localhost:5001/api/stats", timeout=3)
                if stats_response.status_code == 200:
                    stats['stats'] = stats_response.json()
            except:
                stats['stats'] = {"error": "Stats data unavailable"}

            try:
                transactions_response = requests.get("http://localhost:5001/api/transactions", timeout=3)
                if transactions_response.status_code == 200:
                    stats['transactions'] = transactions_response.json()
            except:
                stats['transactions'] = {"error": "Transactions data unavailable"}

            try:
                dns_records_response = requests.get("http://localhost:5001/api/dns-records", timeout=3)
                if dns_records_response.status_code == 200:
                    stats['dns_records'] = dns_records_response.json()
            except:
                stats['dns_records'] = {"error": "DNS records data unavailable"}

            try:
                network_info_response = requests.get("http://localhost:5001/api/network-info", timeout=3)
                if network_info_response.status_code == 200:
                    stats['network'] = network_info_response.json()
            except:
                stats['network'] = {"error": "Network info unavailable"}

            try:
                threat_stats_response = requests.get("http://localhost:5001/api/threat-stats", timeout=3)
                if threat_stats_response.status_code == 200:
                    stats['threat_stats'] = threat_stats_response.json()
            except:
                stats['threat_stats'] = {"error": "Threat stats unavailable"}

            try:
                ml_integration_response = requests.get("http://localhost:5001/api/ml-blockchain-integration", timeout=3)
                if ml_integration_response.status_code == 200:
                    stats['ml_blockchain_integration'] = ml_integration_response.json()
            except:
                stats['ml_blockchain_integration'] = {"error": "ML-Blockchain integration data unavailable"}

            try:
                pending_transactions_response = requests.get("http://localhost:5001/api/pending-transactions", timeout=3)
                if pending_transactions_response.status_code == 200:
                    stats['pending_transactions'] = pending_transactions_response.json()
            except:
                stats['pending_transactions'] = {"error": "Pending transactions data unavailable"}

            # Also fetch security analytics and threat feed from ML service (5000)
            try:
                security_response = requests.get("http://localhost:5000/security-analytics", timeout=2)
                if security_response.status_code == 200:
                    stats['security'] = security_response.json()
            except:
                stats['security'] = {"error": "Security data unavailable"}

            try:
                threat_feed_response = requests.get("http://localhost:5000/threat-feed", timeout=2)
                if threat_feed_response.status_code == 200:
                    stats['threats'] = threat_feed_response.json()
            except:
                stats['threats'] = {"error": "Threat feed data unavailable"}

            # Optionally, fetch from all nodes for redundancy/network view
            stats['blockchain_nodes'] = {}
            for port in api_ports:
                try:
                    node_stats = requests.get(f"http://localhost:{port}/api/stats", timeout=2)
                    if node_stats.status_code == 200:
                        stats['blockchain_nodes'][f'node_{port}'] = node_stats.json()
                except:
                    stats['blockchain_nodes'][f'node_{port}'] = {"error": "Node unreachable"}

            # Add timestamp for real-time context
            stats['timestamp'] = time.time()
            stats['readable_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
            return stats
        except Exception as e:
            return {"error": f"Failed to get system stats: {str(e)}", "timestamp": time.time()}

    def chat(self, user_message, include_system_data=True):
        """Send message to AI agent and get response"""
        if not self.is_ollama_available():
            return {
                "error": "Offline AI agent not available. Please install Ollama and pull the model.",
                "setup_instructions": "Run: 'ollama pull llama3.2:1b' to install the AI model"
            }

        try:
            # Get LIVE system data for real-time context
            live_stats = self.get_system_stats()
            
            # Build dynamic context with actual data
            context = self.system_context
            
            if include_system_data and live_stats:
                context += f"\n\n=== LIVE SYSTEM DATA (Real-time) ===\n"
                context += f"Data captured at: {live_stats.get('readable_time', 'Unknown')}\n\n"
                
                # Security data
                if 'security' in live_stats and 'error' not in live_stats['security']:
                    sec = live_stats['security']
                    context += f"SECURITY ANALYTICS (ACTUAL LIVE DATA):\n"
                    context += f"- Total domains analyzed: {sec.get('total_analyzed', 0)}\n"
                    context += f"- Malicious domains detected: {sec.get('malicious_domains', 0)}\n"
                    context += f"- Safe domains: {sec.get('safe_domains', 0)}\n"
                    context += f"- Threat percentage: {sec.get('threat_percentage', 0):.1f}%\n"
                    
                    if 'recent_predictions' in sec and sec['recent_predictions']:
                        context += f"- Recent predictions: {len(sec['recent_predictions'])} entries\n"
                        recent_malicious = sum(1 for p in sec['recent_predictions'] if p.get('prediction') == 1)
                        context += f"- Recent threat rate: {recent_malicious}/{len(sec['recent_predictions'])}\n"
                    else:
                        context += f"- Recent predictions: 0 entries (no domains have been analyzed yet)\n"
                else:
                    context += f"SECURITY ANALYTICS: ERROR - {live_stats.get('security', {}).get('error', 'Data unavailable')}\n"
                
                # Threat feed
                if 'threats' in live_stats and 'error' not in live_stats['threats']:
                    threats = live_stats['threats']
                    if threats and len(threats) > 0:
                        context += f"\nRECENT THREATS (ACTUAL LIVE DATA):\n"
                        context += f"- Latest threats detected: {len(threats)}\n"
                        for i, threat in enumerate(threats[:3]):  # Show top 3 threats
                            context += f"  {i+1}. {threat.get('domain', 'Unknown')} (confidence: {threat.get('confidence', 0):.2f})\n"
                    else:
                        context += f"\nRECENT THREATS: No threats detected - system is clean\n"
                else:
                    context += f"\nRECENT THREATS: ERROR - {live_stats.get('threats', {}).get('error', 'Data unavailable')}\n"
                
                # Blockchain data
                if 'blockchain' in live_stats and 'error' not in live_stats['blockchain']:
                    bc = live_stats['blockchain']
                    context += f"\nBLOCKCHAIN NETWORK STATUS:\n"
                    
                    # Count active nodes
                    active_nodes = []
                    total_blocks = 0
                    total_pending = 0
                    
                    for node_key, node_data in bc.items():
                        if isinstance(node_data, dict) and node_data.get('status') == 'active':
                            active_nodes.append(node_data.get('port', 'unknown'))
                            total_blocks = max(total_blocks, node_data.get('total_blocks', 0))
                            total_pending += node_data.get('pending_transactions', 0)
                    
                    context += f"- Network nodes detected: {len(active_nodes)} active nodes on ports {active_nodes}\n"
                    context += f"- Blockchain length: {total_blocks} blocks\n"
                    context += f"- Total pending transactions across network: {total_pending}\n"
                    
                    # Show per-node details
                    for node_key, node_data in bc.items():
                        if isinstance(node_data, dict):
                            port = node_data.get('port', 'unknown')
                            status = node_data.get('status', 'unknown')
                            blocks = node_data.get('total_blocks', 0)
                            pending = node_data.get('pending_transactions', 0)
                            context += f"  Node {port}: {status}, {blocks} blocks, {pending} pending\n"
                
                # Network data
                if 'network' in live_stats and 'error' not in live_stats['network']:
                    net = live_stats['network']
                    context += f"\nNETWORK STATUS:\n"
                    context += f"- Connected nodes: {net.get('connected_nodes', 0)}\n"
                    # context += f"- Network health: {net.get('health_status', 'Unknown')}\n"
                
                context += f"\n=== END LIVE DATA ===\n\n"
                # ⬇️⬇️⬇️ THIS IS THE UPDATED PART ⬇️⬇️⬇️
                context += """
CRITICAL INSTRUCTIONS: Your response MUST be based **strictly and exclusively** on the `=== LIVE SYSTEM DATA ===` provided above.
- If the data for a query is zero, empty, or unavailable (e.g., `total_blocks: 0` or `recent_threats: []`), you must state that fact directly **and then stop.**
- **Under no circumstances** should you provide examples, tutorials, hypothetical scenarios, or explanations of what the data *might* look like if it existed.
- If the user asks for the number of blocks and the data shows 0, your entire answer should simply be: "According to the live data, there are currently 0 blocks in the blockchain."
- Your sole purpose is to be a factual reporter of the live data. **Do not add any extra, illustrative, or educational information** unless it is directly supported by the live data provided.
"""

            # Prepare the chat request with live context
            messages = [
                {"role": "system", "content": context},
                {"role": "user", "content": user_message}
            ]

            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.2, # Lower temperature for more factual responses
                        "top_p": 0.9,
                        "num_ctx": 4096 # Increased context window
                    }
                },
                timeout=60  # Increased timeout for better reliability
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "response": result['message']['content'],
                    "timestamp": time.time(),
                    "model": self.model,
                    "live_data_included": True,
                    "data_timestamp": live_stats.get('readable_time', 'Unknown')
                }
            else:
                return {"error": "Failed to get AI response"}

        except Exception as e:
            return {"error": f"AI agent error: {str(e)}"}

    def get_contextual_help(self, section):
        """Get help for specific dashboard sections"""
        help_prompts = {
            "overview": "Based on the current live data, explain what the overview dashboard shows and what each statistic means for blockchain DNS performance.",
            "security": "Looking at the current security analytics data, explain what the threat detection rates, malicious domains, and confidence scores mean.",
            "blockchain": "Based on the live blockchain data, explain the current blocks, transactions, mining status, and consensus state.",
            "network": "Using current network data, explain the node connectivity, synchronization status, and network health.",
            "dns_records": "Explain how DNS records work in blockchain and the current state of records in the system.",
            "mining": "Based on current blockchain status, explain the mining process, pending transactions, and mining opportunities."
        }
        
        prompt = help_prompts.get(section, f"Based on current live data, explain the {section} section of the blockchain DNS dashboard.")
        return self.chat(prompt)

    def analyze_current_trends(self):
        """Analyze current system trends and provide insights"""
        stats = self.get_system_stats()
        
        if not stats or 'error' in stats:
            return {"error": "Cannot analyze trends - system data unavailable"}
        
        prompt = """
        Analyze the current system state and provide insights about:
        1. Security trends and threat levels
        2. Blockchain performance and activity
        3. Network health and connectivity
        4. Any recommendations for optimization
        
        Be specific about the numbers and what they indicate.
        """
        
        return self.chat(prompt)

    def get_smart_dashboard_summary(self):
        """Get an intelligent summary of current dashboard state"""
        prompt = """
        Provide a concise but comprehensive summary of the current system state.
        Include key metrics, any concerning trends, and overall system health.
        Make it suitable for a quick dashboard overview.
        """
        
        return self.chat(prompt)

# Global agent instance
dns_agent = BlockchainDNSAgent()