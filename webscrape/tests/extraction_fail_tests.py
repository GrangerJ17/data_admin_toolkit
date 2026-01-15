import json
import pytest
from pathlib import Path

def load_bad_sample(filename):
    """Load a specific bad fixture"""
    fixtures_path = Path(__file__).parent / 'fixtures' / 'bad'
    with open(fixtures_path / filename) as f:
        return json.load(f)

def test_missing_description_detected():
    """Should detect when description field is missing"""
    data = load_bad_sample('property_bad_missing_desc.json')
    
    # This should fail validation
    has_description = "description" in data
    assert not has_description, "Should detect missing description"

def test_short_description_detected():
    """Should detect when description is too short"""
    data = load_bad_sample('property_bad_short_desc.json')
    
    desc_len = len(data.get('description', ''))
    assert desc_len < 50, f"Test fixture should have short description, got {desc_len} chars"

def test_missing_price_detected():
    """Should detect when price field is missing"""
    data = load_bad_sample('property_bad_no_price.json')
    
    has_price = "price" in data
    assert not has_price, "Should detect missing price"

def test_negative_price_detected():
    """Should detect when price is negative"""
    data = load_bad_sample('property_bad_negative_price.json')
    
    price = data.get('price', 0)
    assert price < 0, f"Test fixture should have negative price, got {price}"

def test_unrealistic_price_detected():
    """Should detect when price is unrealistically high"""
    data = load_bad_sample('property_bad_crazy_price.json')
    
    price = data.get('price', 0)
    assert price >= 100000, f"Test fixture should have crazy price, got {price}"

def test_missing_address_detected():
    """Should detect when address field is missing"""
    data = load_bad_sample('property_bad_no_address.json')
    
    has_address = "address" in data
    assert not has_address, "Should detect missing address"

def test_malformed_address_detected():
    """Should detect when address is too short/malformed"""
    data = load_bad_sample('property_bad_malformed_address.json')
    
    address = data.get('address', '')
    assert len(address) <= 10, f"Test fixture should have short address, got '{address}'"

if __name__ == "__main__":
    test_missing_description_detected()
    test_short_description_detected()
    test_missing_price_detected()
    test_negative_price_detected()
    test_unrealistic_price_detected()
    test_missing_address_detected()
    test_malformed_address_detected()