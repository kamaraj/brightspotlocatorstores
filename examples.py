"""
Example Usage Scripts for Childcare Location Intelligence API
Run these after starting the application with: python run.py
"""

import requests
import json
import time
from typing import Dict, Any


# API Base URL
BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}\n")


def print_result(result: Dict[str, Any]):
    """Pretty print API result"""
    print(json.dumps(result, indent=2))


# ============================================
# Example 1: Health Check
# ============================================

def example_health_check():
    """Check if the API is running"""
    print_section("Example 1: Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print_result(response.json())
    
    return response.status_code == 200


# ============================================
# Example 2: API Info
# ============================================

def example_api_info():
    """Get API configuration and features"""
    print_section("Example 2: API Info")
    
    response = requests.get(f"{BASE_URL}/api/v1/info")
    print_result(response.json())


# ============================================
# Example 3: Single Location Validation
# ============================================

def example_single_validation():
    """Validate a single childcare center location"""
    print_section("Example 3: Single Location Validation")
    
    payload = {
        "address": "1600 Amphitheatre Parkway, Mountain View, CA 94043",
        "additional_context": "Looking for location for infant care center, budget $500K",
        "radius_miles": 2.0
    }
    
    print(f"Analyzing: {payload['address']}")
    print("This may take 60-90 seconds...\n")
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/v1/validate",
        json=payload,
        timeout=120  # 2 minute timeout
    )
    elapsed_time = time.time() - start_time
    
    print(f"Status Code: {response.status_code}")
    print(f"Time Elapsed: {elapsed_time:.2f} seconds\n")
    
    result = response.json()
    
    if result.get("success"):
        print("✓ Analysis successful!")
        print(f"\nAddress: {result['address']}")
        print(f"\nAnalysis:\n{result['analysis']}")
        
        if result.get("metadata"):
            print(f"\nMetadata:")
            print(f"  Model: {result['metadata'].get('model')}")
            print(f"  Iterations: {result['metadata'].get('iterations')}")
            print(f"  Tool Calls: {result['metadata'].get('tool_calls')}")
    else:
        print(f"✗ Analysis failed: {result.get('error')}")
    
    return result


# ============================================
# Example 4: Streaming Validation
# ============================================

def example_streaming_validation():
    """Stream analysis results in real-time"""
    print_section("Example 4: Streaming Validation")
    
    payload = {
        "address": "1 Infinite Loop, Cupertino, CA 95014",
        "additional_context": "Preschool for ages 3-5"
    }
    
    print(f"Streaming analysis for: {payload['address']}")
    print("Results will appear as they're generated:\n")
    print("-" * 70)
    
    response = requests.post(
        f"{BASE_URL}/api/v1/validate/stream",
        json=payload,
        stream=True,
        timeout=120
    )
    
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if decoded.startswith("data: "):
                content = decoded[6:]  # Remove "data: " prefix
                if content == "[DONE]":
                    print("\n" + "-" * 70)
                    print("✓ Streaming complete!")
                    break
                elif content.startswith("[ERROR"):
                    print(f"\n✗ Error: {content}")
                    break
                else:
                    print(content, end="", flush=True)


# ============================================
# Example 5: Compare Multiple Locations
# ============================================

def example_comparison():
    """Compare multiple locations side-by-side"""
    print_section("Example 5: Multi-Location Comparison")
    
    payload = {
        "addresses": [
            "1 Market St, San Francisco, CA 94105",
            "100 Main St, Oakland, CA 94607",
            "1 El Camino Real, Palo Alto, CA 94301"
        ],
        "additional_context": "Best location for 100-child capacity center"
    }
    
    print(f"Comparing {len(payload['addresses'])} locations:")
    for i, addr in enumerate(payload['addresses'], 1):
        print(f"  {i}. {addr}")
    
    print("\nThis may take 3-5 minutes...\n")
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/v1/compare",
        json=payload,
        timeout=300  # 5 minute timeout
    )
    elapsed_time = time.time() - start_time
    
    print(f"Status Code: {response.status_code}")
    print(f"Time Elapsed: {elapsed_time:.2f} seconds\n")
    
    result = response.json()
    
    if result.get("success"):
        print("✓ Comparison successful!")
        
        # Print individual analyses
        print("\n" + "="*70)
        print(" Individual Analyses")
        print("="*70)
        
        for i, analysis in enumerate(result.get('individual_analyses', []), 1):
            print(f"\nLocation {i}: {analysis.get('address')}")
            if analysis.get('success'):
                print(f"Status: ✓ Success")
            else:
                print(f"Status: ✗ Failed - {analysis.get('error')}")
        
        # Print comparison
        if result.get('comparison'):
            print("\n" + "="*70)
            print(" Comparative Analysis")
            print("="*70)
            print(f"\n{result['comparison']}")
    else:
        print(f"✗ Comparison failed: {result.get('error')}")
    
    return result


# ============================================
# Example 6: Error Handling
# ============================================

def example_error_handling():
    """Demonstrate error handling with invalid input"""
    print_section("Example 6: Error Handling")
    
    # Invalid address
    print("Test 1: Invalid address")
    payload = {
        "address": "This is not a valid address xyz123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/validate", json=payload)
    print(f"Status: {response.status_code}")
    print_result(response.json())
    
    # Missing required field
    print("\nTest 2: Missing required field")
    payload = {
        "additional_context": "Some context without address"
    }
    response = requests.post(f"{BASE_URL}/api/v1/validate", json=payload)
    print(f"Status: {response.status_code}")
    print_result(response.json())
    
    # Invalid radius
    print("\nTest 3: Invalid radius (out of range)")
    payload = {
        "address": "123 Main St, San Francisco, CA",
        "radius_miles": 50.0  # Max is 10.0
    }
    response = requests.post(f"{BASE_URL}/api/v1/validate", json=payload)
    print(f"Status: {response.status_code}")
    print_result(response.json())


# ============================================
# Example 7: Batch Processing (Mock)
# ============================================

def example_batch_processing():
    """Process multiple locations (sequential for now)"""
    print_section("Example 7: Batch Processing (Sequential)")
    
    addresses = [
        "123 Main St, San Jose, CA 95113",
        "456 Oak Ave, Berkeley, CA 94704",
        "789 Pine St, Fremont, CA 94538"
    ]
    
    results = []
    
    for i, address in enumerate(addresses, 1):
        print(f"\nProcessing {i}/{len(addresses)}: {address}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/validate",
                json={"address": address},
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                results.append({
                    "address": address,
                    "success": result.get("success"),
                    "analysis": result.get("analysis", "")[:200] + "..."  # First 200 chars
                })
                print(f"  ✓ Success")
            else:
                print(f"  ✗ Failed: {response.status_code}")
                results.append({
                    "address": address,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                "address": address,
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "="*70)
    print(" Batch Processing Summary")
    print("="*70)
    successful = sum(1 for r in results if r.get("success"))
    print(f"Total: {len(addresses)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(addresses) - successful}")
    
    return results


# ============================================
# Main Execution
# ============================================

def main():
    """Run all examples"""
    
    print("\n" + "="*70)
    print(" Childcare Location Intelligence API - Usage Examples")
    print("="*70)
    print("\nMake sure the API is running: python run.py")
    print("Press Ctrl+C to stop at any time\n")
    
    try:
        # Check if API is running
        if not example_health_check():
            print("\n✗ API is not running. Start it with: python run.py")
            return
        
        # API Info
        example_api_info()
        
        # Wait for user input between examples
        input("\nPress Enter to run Example 3 (Single Location Validation)...")
        example_single_validation()
        
        # Uncomment to run streaming example
        # input("\nPress Enter to run Example 4 (Streaming Validation)...")
        # example_streaming_validation()
        
        # Uncomment to run comparison example (takes 3-5 minutes)
        # input("\nPress Enter to run Example 5 (Multi-Location Comparison)...")
        # example_comparison()
        
        input("\nPress Enter to run Example 6 (Error Handling)...")
        example_error_handling()
        
        # Uncomment to run batch processing (takes several minutes)
        # input("\nPress Enter to run Example 7 (Batch Processing)...")
        # example_batch_processing()
        
        print("\n" + "="*70)
        print(" All Examples Complete!")
        print("="*70)
        print("\nFor more examples, see:")
        print("  - Interactive docs: http://localhost:8000/api/docs")
        print("  - QUICKSTART.md for detailed usage")
        
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")


if __name__ == "__main__":
    main()
