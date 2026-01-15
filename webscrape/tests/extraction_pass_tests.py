import json
from pathlib import Path

def load_good_samples():
    """Load all good test fixtures"""
    fixtures_path = Path(__file__).parent / 'fixtures' / 'good'
    samples = []
    for file in fixtures_path.glob('*.json'):
        with open(file) as f:
            samples.append((file.name, json.load(f)))
    return samples

def test_good_data_has_description():
    """Good data should always have description field"""
    for filename, data in load_good_samples():
        assert "description" in data, f"{filename}: Missing description field"
        assert data["description"], f"{filename}: Description is empty"

def test_good_data_desc_size():
    """Good data descriptions should be substantial (>50 chars)"""
    for filename, data in load_good_samples():
        desc_len = len(data['description'])
        assert desc_len > 50, f"{filename}: Description too short ({desc_len} chars)"

def test_good_data_has_price():
    """Good data should always have price field"""
    for filename, data in load_good_samples():
        assert "price" in data, f"{filename}: Missing price field"

def test_good_data_price_is_valid():
    """Good data prices should be positive numbers in reasonable range"""
    for filename, data in load_good_samples():
        price = data['price']
        assert isinstance(price, (int, float)), f"{filename}: Price not numeric, got {type(price)}"
        assert 0 < price < 100000, f"{filename}: Price out of range: {price}"

def test_good_data_has_address():
    """Good data should always have address field"""
    for filename, data in load_good_samples():
        assert "address" in data, f"{filename}: Missing address field"
        assert data["address"], f"{filename}: Address is empty"

def test_good_data_valid_address():
    """Good data addresses should be properly formatted"""
    for filename, data in load_good_samples():
        address = data['address']
        assert len(address) > 10, f"{filename}: Address too short: '{address}'"
        assert any(c.isdigit() for c in address), f"{filename}: Address missing numbers: '{address}'"
        assert any(c.isalpha() for c in address), f"{filename}: Address missing letters: '{address}'"

if __name__ == "__main__":
    test_good_data_has_description()
    test_good_data_desc_size()
    test_good_data_has_price()
    test_good_data_price_is_valid()
    test_good_data_has_address()
    test_good_data_valid_address()