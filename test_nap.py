import requests
import time

BASE_URL = 'http://localhost:5000'

def test_nap_flow():
    # 1. Register/Login
    username = f"test_nap_{int(time.time())}"
    password = "password"
    
    print(f"Registering {username}...")
    res = requests.post(f'{BASE_URL}/api/auth/register', json={'username': username, 'password': password})
    if res.status_code != 201:
        print(f"Registration failed: {res.text}")
        return
    
    user_id = res.json()['id']
    print(f"User ID: {user_id}")
    
    # 2. Start Nap
    print("Starting nap...")
    res = requests.post(f'{BASE_URL}/api/sleep/start', json={'user_id': user_id})
    print(f"Start Status: {res.status_code}")
    print(f"Start Response: {res.json()}")
    
    if res.status_code != 200:
        print("Failed to start nap.")
        return

    # 3. Wait a bit
    time.sleep(2)
    
    # 4. End Nap (Wakeup)
    print("Waking up...")
    res = requests.post(f'{BASE_URL}/api/sleep/end', json={'user_id': user_id})
    print(f"End Status: {res.status_code}")
    print(f"End Response: {res.json()}")

if __name__ == '__main__':
    try:
        test_nap_flow()
    except Exception as e:
        print(f"Test failed: {e}")
