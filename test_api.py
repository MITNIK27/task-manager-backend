"""
Quick API test script to verify all endpoints are working
Run: python test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def test(name, method, endpoint, data=None, headers=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        status = f"{GREEN}✓{RESET}" if response.status_code < 400 else f"{RED}✗{RESET}"
        print(f"{status} {name}: {response.status_code}")
        
        if response.status_code >= 400:
            print(f"  Error: {response.text[:100]}")
            return None
        
        return response.json() if response.text else None
    except Exception as e:
        print(f"{RED}✗{RESET} {name}: {str(e)}")
        return None

print(f"\n{YELLOW}=== Task Manager API Test ==={RESET}\n")

# 1. Login
print("1. Testing Authentication...")
login_result = test(
    "Login (user1/pass123)",
    "POST",
    "/auth/login",
    data={"username": "user1", "password": "pass123"}
)

if not login_result:
    print(f"{RED}Login failed! Check if backend is running.{RESET}\n")
    exit(1)

token = login_result.get("access_token")
headers = {"Authorization": f"Bearer {token}"}

print(f"\n2. Testing Task Operations...")

# 2. Get all tasks
tasks_result = test("Get all tasks", "GET", "/tasks", headers=headers)
print(f"  Found {len(tasks_result) if tasks_result else 0} tasks")

# 3. Create a task
create_result = test(
    "Create task",
    "POST",
    "/tasks/",
    data={
        "title": "API Test Task",
        "description": "This is a test task",
        "priority": "HIGH"
    },
    headers=headers
)

if not create_result:
    print(f"{RED}Task creation failed!{RESET}\n")
    exit(1)

task_id = create_result["id"]
print(f"  Created task ID: {task_id}")

# 4. Get task details
print(f"\n3. Testing Task Details Endpoints...")
test("Get task", "GET", f"/tasks/{task_id}", headers=headers)
test("Get status history", "GET", f"/tasks/{task_id}/status-history", headers=headers)
test("Get audit logs", "GET", f"/tasks/{task_id}/audit-logs", headers=headers)

# 5. Update task
print(f"\n4. Testing Task Updates...")
test(
    "Update task status",
    "PUT",
    f"/tasks/{task_id}",
    data={"status": "IN_PROGRESS"},
    headers=headers
)

# 6. Archive task
print(f"\n5. Testing Archive/Restore...")
test("Archive task", "POST", f"/tasks/{task_id}/archive", headers=headers)
test("Restore task", "POST", f"/tasks/{task_id}/restore", headers=headers)

print(f"\n{GREEN}=== All tests complete ==={RESET}\n")
print("If all tests show ✓, the API is working correctly!")
print("If you see ✗, check the error messages above.\n")
