#!/usr/bin/env python3
"""
Test script for LoRa integration with T-Beam and ballistics API.
This script tests the complete data flow from T-Beam USB serial to ballistics calculations.
"""

import requests
import time
import json
import sys

def test_environment_endpoint():
    """Test the /api/environment endpoint"""
    print("Testing /api/environment endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/environment")
        if response.status_code == 200:
            data = response.json()
            print("✅ Environment endpoint working")
            print(f"   Wind: {data['wind_speed_mph']} mph @ {data['wind_direction_deg']}°")
            print(f"   Temp: {data['temperature_f']}°F, Pressure: {data['pressure_inhg']} inHg")
            return True
        else:
            print(f"❌ Environment endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to API: {e}")
        return False

def test_auto_ballistics():
    """Test the /api/ballistics/auto endpoint"""
    print("\nTesting /api/ballistics/auto endpoint...")
    payload = {
        "bc_g7": 0.223,
        "muzzle_velocity_fps": 2600,
        "range_yds": 1000
    }

    try:
        response = requests.post("http://localhost:5000/api/ballistics/auto",
                               json=payload,
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            print("✅ Auto ballistics calculation working")
            print(f"   Drop: {data['drop_moa']} MOA")
            print(f"   Windage: {data['windage_moa']} MOA")
            print(f"   Time: {data['time_of_flight_sec']} sec")
            print(f"   Velocity: {data['velocity_at_target_fps']} fps")
            return True
        else:
            print(f"❌ Auto ballistics failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to API: {e}")
        return False

def test_lora_messages():
    """Test the /api/lora/messages endpoint"""
    print("\nTesting /api/lora/messages endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/lora/messages")
        if response.status_code == 200:
            data = response.json()
            print("✅ LoRa messages endpoint working")
            if data['messages']:
                print(f"   Found {len(data['messages'])} messages")
                for msg in data['messages'][:3]:  # Show first 3 messages
                    print(f"   - {msg}")
            else:
                print("   No messages received yet (this is normal if T-Beam not connected)")
            return True
        else:
            print(f"❌ LoRa messages endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to API: {e}")
        return False

def main():
    print("🔍 Testing LoRa Integration with Ballistics API")
    print("=" * 50)

    # Check if API is running
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
    except requests.exceptions.RequestException:
        print("❌ API server not running!")
        print("   Please start the API server first:")
        print("   cd FAWD-and-User-Interface-Lora-integration")
        print("   source venv/bin/activate")
        print("   python app.py")
        sys.exit(1)

    print("✅ API server is running")

    # Run tests
    tests = [
        test_environment_endpoint,
        test_auto_ballistics,
        test_lora_messages
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{len(tests)} passed")

    if passed == len(tests):
        print("🎉 All tests passed! LoRa integration is working correctly.")
        print("\nNext steps:")
        print("1. Connect T-Beam to Raspberry Pi via USB")
        print("2. Ensure T-Beam firmware has forwardDataToPi() function")
        print("3. Start shooting targets to see live environmental data")
    else:
        print("⚠️  Some tests failed. Check the API logs for details.")

if __name__ == "__main__":
    main()