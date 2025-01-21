import requests

def test_health():
    try:
        response = requests.get("http://localhost:8001/health")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Headers: {response.headers}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_health()