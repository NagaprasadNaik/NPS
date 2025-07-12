#!/usr/bin/env python3
"""
Test script to validate the Blockchain DNS Dashboard setup
"""
import requests
import time
import json

def test_api_endpoints():
    """Test all API endpoints"""
    
    base_url = "http://127.0.0.1:5001"
    
    endpoints = [
        "/debug/alive",
        "/api/stats", 
        "/api/transactions",
        "/api/dns-records",
        "/api/network-info",
        "/nodes/chain",
        "/debug/dump_buffer"
    ]
    
    print("🔍 Testing API Endpoints...")
    print("-" * 50)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            print(f"{endpoint:<25} {status}")
        except requests.exceptions.RequestException as e:
            print(f"{endpoint:<25} ❌ ERROR ({str(e)})")
    
    print("\n" + "=" * 50)

def test_dashboard_access():
    """Test dashboard page access"""
    
    print("🌐 Testing Dashboard Access...")
    print("-" * 50)
    
    try:
        response = requests.get("http://127.0.0.1:5001/dashboard", timeout=5)
        if response.status_code == 200:
            print("Dashboard page: ✅ ACCESSIBLE")
        else:
            print(f"Dashboard page: ❌ FAIL ({response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"Dashboard page: ❌ ERROR ({str(e)})")
    
    print("\n" + "=" * 50)

def test_add_sample_data():
    """Add sample DNS records for testing"""
    
    print("📝 Adding Sample Data...")
    print("-" * 50)
    
    sample_records = [
        {"hostname": "example.com", "ip": "192.168.1.100", "port": 80},
        {"hostname": "test.local", "ip": "192.168.1.101", "port": 443},
        {"hostname": "blockchain.dns", "ip": "192.168.1.102", "port": 8080}
    ]
    
    for record in sample_records:
        try:
            response = requests.post(
                "http://127.0.0.1:5001/api/add-dns-record",
                json=record,
                timeout=5
            )
            status = "✅ ADDED" if response.status_code == 201 else f"❌ FAIL ({response.status_code})"
            print(f"{record['hostname']:<20} {status}")
        except requests.exceptions.RequestException as e:
            print(f"{record['hostname']:<20} ❌ ERROR ({str(e)})")
    
    print("\n" + "=" * 50)

def display_instructions():
    """Display usage instructions"""
    
    print("🚀 Blockchain DNS Dashboard Setup Complete!")
    print("=" * 60)
    print("\n📋 HOW TO USE:")
    print("-" * 30)
    print("1. Start the ML Security API:")
    print("   python app.py")
    print("\n2. Start the Blockchain DNS Node:")
    print("   python server.py -p 5001")
    print("\n3. Access the interfaces:")
    print("   • Original Interface: http://127.0.0.1:5000/web")
    print("   • New Dashboard:      http://127.0.0.1:5001/dashboard")
    print("\n4. Test domain security:")
    print("   • Try 'google.com' (should be safe)")
    print("   • Try 'malicious-site.com' (may be flagged)")
    print("\n5. Explore dashboard features:")
    print("   • View blockchain statistics")
    print("   • Browse transaction history")
    print("   • Manage DNS records")
    print("   • Monitor network topology")
    print("   • Add new DNS records")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print("🔧 Blockchain DNS Dashboard Test Suite")
    print("=" * 60)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test dashboard access
    test_dashboard_access()
    
    # Add sample data
    test_add_sample_data()
    
    # Display instructions
    display_instructions()
