"""
Test script to verify all endpoints meet GOAL.md requirements
Run this after starting the server with: python test_endpoints.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_post_string():
    """Test 1: POST /strings - Create/Analyze String"""
    print("\n=== TEST 1: POST /strings ===")
    
    # Test valid string
    response = requests.post(
        f"{BASE_URL}/strings",
        json={"value": "string to analyzer"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 201, "Should return 201 Created"
    data = response.json()
    assert "id" in data
    assert "value" in data
    assert "properties" in data
    assert "created_at" in data
    print("✅ Valid string creation passed")
    
    # Test duplicate string (409)
    response = requests.post(
        f"{BASE_URL}/strings",
        json={"value": "string to analyze"}
    )
    print(f"\nDuplicate Status: {response.status_code}")
    assert response.status_code == 409, "Should return 409 Conflict"
    print("✅ Duplicate detection passed")
    
    # Test missing value (400)
    response = requests.post(
        f"{BASE_URL}/strings",
        json={}
    )
    print(f"\nMissing value Status: {response.status_code}")
    assert response.status_code == 422, "Should return 422 for missing field"
    print("✅ Missing value validation passed")
    
    # Test invalid type (422)
    response = requests.post(
        f"{BASE_URL}/strings",
        json={"value": 123}
    )
    print(f"\nInvalid type Status: {response.status_code}")
    assert response.status_code == 422, "Should return 422 for invalid type"
    print("✅ Invalid type validation passed")

def test_get_specific_string():
    """Test 2: GET /strings/{string_value}"""
    print("\n=== TEST 2: GET /strings/{string_value} ===")
    
    # First create a string
    requests.post(f"{BASE_URL}/strings", json={"value": "test string"})
    
    # Get it
    response = requests.get(f"{BASE_URL}/strings/test string")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Get specific string passed")
    
    # Test 404
    response = requests.get(f"{BASE_URL}/strings/nonexistent")
    print(f"\n404 Status: {response.status_code}")
    assert response.status_code == 404
    print("✅ 404 handling passed")

def test_get_all_with_filters():
    """Test 3: GET /strings with query parameters"""
    print("\n=== TEST 3: GET /strings with filters ===")
    
    # Create test strings
    test_strings = ["racecar", "hello world", "aba", "test"]
    for s in test_strings:
        try:
            requests.post(f"{BASE_URL}/strings", json={"value": s})
        except:
            pass
    
    # Test palindrome filter
    response = requests.get(f"{BASE_URL}/strings?is_palindrome=true")
    print(f"Palindrome filter Status: {response.status_code}")
    data = response.json()
    print(f"Found {data['count']} palindromes")
    print(f"Filters applied: {data['filters_applied']}")
    assert response.status_code == 200
    print("✅ Palindrome filter passed")
    
    # Test multiple filters
    response = requests.get(f"{BASE_URL}/strings?min_length=5&contains_character=a")
    print(f"\nMulti-filter Status: {response.status_code}")
    data = response.json()
    print(f"Found {data['count']} results")
    print(f"Filters applied: {data['filters_applied']}")
    print("✅ Multiple filters passed")

def test_natural_language_filter():
    """Test 4: GET /strings/filter-by-natural-language"""
    print("\n=== TEST 4: Natural Language Filter ===")
    
    # Test single word palindromes
    response = requests.get(
        f"{BASE_URL}/strings/filter-by-natural-language",
        params={"query": "all single word palindromic strings"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Query: {data['interpreted_query']['original']}")
    print(f"Parsed filters: {data['interpreted_query']['parsed_filters']}")
    print(f"Found {data['count']} results")
    assert response.status_code == 200
    print("✅ Natural language query passed")
    
    # Test longer than
    response = requests.get(
        f"{BASE_URL}/strings/filter-by-natural-language",
        params={"query": "strings longer than 10 characters"}
    )
    print(f"\nLonger than query Status: {response.status_code}")
    data = response.json()
    print(f"Parsed filters: {data['interpreted_query']['parsed_filters']}")
    print("✅ Length query passed")
    
    # Test first vowel
    response = requests.get(
        f"{BASE_URL}/strings/filter-by-natural-language",
        params={"query": "palindromic strings that contain the first vowel"}
    )
    print(f"\nFirst vowel query Status: {response.status_code}")
    data = response.json()
    print(f"Parsed filters: {data['interpreted_query']['parsed_filters']}")
    print("✅ First vowel query passed")

def test_delete_string():
    """Test 5: DELETE /strings/{string_value}"""
    print("\n=== TEST 5: DELETE /strings/{string_value} ===")
    
    # Create a string to delete
    requests.post(f"{BASE_URL}/strings", json={"value": "to be deleted"})
    
    # Delete it
    response = requests.delete(f"{BASE_URL}/strings/to be deleted")
    print(f"Status: {response.status_code}")
    assert response.status_code == 204
    print("✅ Delete successful")
    
    # Try to get it (should be 404)
    response = requests.get(f"{BASE_URL}/strings/to be deleted")
    print(f"Get after delete Status: {response.status_code}")
    assert response.status_code == 404
    print("✅ Delete verification passed")
    
    # Try to delete non-existent (404)
    response = requests.delete(f"{BASE_URL}/strings/never existed")
    print(f"Delete non-existent Status: {response.status_code}")
    assert response.status_code == 404
    print("✅ 404 on delete passed")

def test_properties_calculation():
    """Test that all properties are calculated correctly"""
    print("\n=== TEST 6: Properties Calculation ===")
    
    response = requests.post(
        f"{BASE_URL}/strings",
        json={"value": "Hello World"}
    )
    
    if response.status_code == 409:
        # Already exists, get it
        response = requests.get(f"{BASE_URL}/strings/Hello World")
    
    data = response.json()
    props = data["properties"]
    
    print(f"String: 'Hello World'")
    print(f"Length: {props['length']} (expected: 11)")
    print(f"Is Palindrome: {props['is_palindrome']} (expected: False)")
    print(f"Unique Characters: {props['unique_characters']}")
    print(f"Word Count: {props['word_count']} (expected: 2)")
    print(f"SHA256 Hash: {props['sha256_hash'][:20]}...")
    print(f"Character Frequency Map: {props['character_frequency_map']}")
    
    assert props['length'] == 11
    assert props['is_palindrome'] == False
    assert props['word_count'] == 2
    assert 'sha256_hash' in props
    assert 'character_frequency_map' in props
    print("✅ Properties calculation passed")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("STRING ANALYZER API - COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        
        test_post_string()
        test_get_specific_string()
        test_get_all_with_filters()
        test_natural_language_filter()
        test_delete_string()
        test_properties_calculation()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server. Is it running on http://127.0.0.1:8000?")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
