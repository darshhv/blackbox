"""
Sample Data Generator for BLACKBOX
Simulates realistic incident scenarios for testing
"""

import requests
import time
from datetime import datetime, timedelta
import random

API_URL = "http://localhost:8000"

def create_event(service, environment, level, message, request_id=None):
    """Create a single event"""
    event = {
        "service": service,
        "environment": environment,
        "level": level,
        "message": message,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    response = requests.post(f"{API_URL}/events", json=event)
    if response.status_code == 201:
        print(f"✓ Created {level} event: {service} - {message}")
    else:
        print(f"✗ Failed to create event: {response.text}")
    
    return response


def scenario_database_timeout():
    """Simulate a database timeout incident"""
    print("\n=== Scenario: Database Timeout Incident ===\n")
    
    # Initial warning signs
    create_event("payments", "prod", "warning", "Database connection pool at 80%")
    time.sleep(1)
    
    # Cascade of errors
    request_ids = [f"req_{i}" for i in range(1, 8)]
    for req_id in request_ids:
        create_event("payments", "prod", "error", "Database timeout after 30s", req_id)
        time.sleep(0.5)
    
    # Related service failures
    create_event("orders", "prod", "error", "Payment service unreachable", request_ids[0])
    time.sleep(0.5)
    create_event("notifications", "prod", "warning", "Failed to send payment confirmation")
    
    print("\n✓ Database timeout incident created (should trigger incident detection)")


def scenario_deployment_failure():
    """Simulate a bad deployment"""
    print("\n=== Scenario: Deployment Failure ===\n")
    
    # Deployment event
    create_event("api-gateway", "prod", "info", "Deployment v2.3.1 started")
    time.sleep(1)
    
    # Immediate errors
    for i in range(6):
        create_event("api-gateway", "prod", "error", 
                    f"Failed to load config: missing REDIS_URL", f"deploy_{i}")
        time.sleep(0.3)
    
    # Rollback
    create_event("api-gateway", "prod", "warning", "Initiating rollback to v2.3.0")
    
    print("\n✓ Deployment failure incident created")


def scenario_cascading_failure():
    """Simulate a cascading failure across services"""
    print("\n=== Scenario: Cascading Service Failure ===\n")
    
    base_req_id = f"cascade_{random.randint(1000, 9999)}"
    
    # Start with auth service
    create_event("auth-service", "prod", "error", 
                "Redis connection refused", f"{base_req_id}_1")
    time.sleep(0.5)
    
    # Cascade to API gateway
    for i in range(4):
        create_event("api-gateway", "prod", "error", 
                    "Auth validation timeout", f"{base_req_id}_2")
        time.sleep(0.3)
    
    # Cascade to user-facing services
    create_event("web-app", "prod", "error", 
                "Failed to authenticate user", f"{base_req_id}_3")
    create_event("mobile-api", "prod", "error", 
                "401 Unauthorized from gateway", f"{base_req_id}_4")
    
    # More auth errors
    for i in range(3):
        create_event("auth-service", "prod", "error", 
                    "Redis connection pool exhausted", f"{base_req_id}_5")
        time.sleep(0.2)
    
    print("\n✓ Cascading failure incident created")


def scenario_mixed_environments():
    """Create events across different environments"""
    print("\n=== Scenario: Multi-Environment Events ===\n")
    
    # Staging issues (should not trigger production incident)
    for i in range(3):
        create_event("payments", "staging", "error", 
                    "Test database connection failed")
        time.sleep(0.2)
    
    # Production errors (should trigger separate incident)
    for i in range(6):
        create_event("payments", "prod", "error", 
                    "Payment processing timeout", f"prod_req_{i}")
        time.sleep(0.3)
    
    print("\n✓ Multi-environment scenario created")


def main():
    """Run all scenarios"""
    print("BLACKBOX Sample Data Generator")
    print("=" * 50)
    
    scenarios = [
        ("1", "Database Timeout", scenario_database_timeout),
        ("2", "Deployment Failure", scenario_deployment_failure),
        ("3", "Cascading Failure", scenario_cascading_failure),
        ("4", "Mixed Environments", scenario_mixed_environments),
        ("5", "All Scenarios", None),
    ]
    
    print("\nAvailable scenarios:")
    for num, name, _ in scenarios:
        print(f"  {num}. {name}")
    
    choice = input("\nSelect scenario (1-5): ").strip()
    
    if choice == "5":
        for _, name, func in scenarios[:-1]:
            func()
            time.sleep(2)
    else:
        for num, name, func in scenarios:
            if num == choice and func:
                func()
                break
    
    print("\n" + "=" * 50)
    print("✓ Sample data generation complete!")
    print("\nView incidents at: http://localhost:3000")
    print("API docs at: http://localhost:8000/docs")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to BLACKBOX API at", API_URL)
        print("Make sure the backend is running (docker-compose up or python main.py)")
