import json
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

print(str(Path(__file__).parent.parent))

from src.seed_database import TargetListing

def test_target_listing_initialization():
    """Test that TargetListing initializes correctly"""
    config = {
        "site": "domain",
        "from_script": "true",
        "script_name": "test-script",
        "global_tags": ["data"],
        "fields": {
            "id": {"keys": ["id"]},
            "price": {"keys": ["price"]},
            "description": {"keys": ["description"]}
        }
    }
    
    listing = TargetListing(config)
    
    assert listing.config == config
    assert listing.fields == {"id": None, "price": None, "description": None}
    assert listing.final_data is None
    assert listing.job_url is None
    print("✓ TargetListing initialization works")

def test_transform_extracts_state_and_postcode():
    """Test that transform correctly extracts state and postcode from address"""
    config = {
        "site": "domain",
        "from_script": "true",
        "fields": {
            "id": {"keys": ["id"]},
            "price": {"keys": ["price"]},
            "description": {"keys": ["description"]},
            "address": {"keys": ["address"]},
            "bedrooms": {"keys": ["bedrooms"]},
            "bathrooms": {"keys": ["bathrooms"]},
            "carspaces": {"keys": ["carspaces"]},
            "property_type": {"keys": ["property_type"]}
        }
    }
    
    listing = TargetListing(config)
    listing.job_url = "http://test.com"
    
    # Manually set fields as if scraped
    listing.fields = {
        "id": "test123",
        "price": 500,
        "description": "Nice apartment with great views",
        "address": "123 George Street, Sydney NSW 2000",
        "bedrooms": 2,
        "bathrooms": 1,
        "carspaces": 1,
        "property_type": "Apartment / Unit / Flat"
    }
    
    result = listing.transform()
    
    assert result["property_data"]["state"] == "NSW"
    assert result["property_data"]["postcode"] == "2000"
    assert result["property_data"]["property_type"] == "apartment unit flat"
    assert "scraped_at" in result
    assert result["job_url"] == "http://test.com"
    print("✓ Transform extracts state/postcode correctly")

def test_transform_handles_missing_values():
    """Test that transform handles missing/null values gracefully"""
    config = {
        "site": "domain",
        "from_script": "true",
        "fields": {
            "id": {"keys": ["id"]},
            "price": {"keys": ["price"]},
            "description": {"keys": ["description"]},
            "address": {"keys": ["address"]},
            "bedrooms": {"keys": ["bedrooms"]},
            "bathrooms": {"keys": ["bathrooms"]},
            "carspaces": {"keys": ["carspaces"]},
            "property_type": {"keys": ["property_type"]}
        }
    }
    
    listing = TargetListing(config)
    listing.job_url = "http://test.com"
    
    # Set fields with None values
    listing.fields = {
        "id": "test456",
        "price": None,
        "description": None,
        "address": "Invalid Address",
        "bedrooms": None,
        "bathrooms": None,
        "carspaces": None,
        "property_type": None
    }
    
    result = listing.transform()
    
    assert result["property_data"]["price"] == 0.0
    assert result["property_data"]["description"] == ""
    assert result["property_data"]["bedrooms"] == 0
    assert result["property_data"]["state"] == ""
    assert result["property_data"]["postcode"] == ""
    print("✓ Transform handles missing values")

if __name__ == "__main__":
    test_target_listing_initialization()
    test_transform_extracts_state_and_postcode()
    test_transform_handles_missing_values()
    print("\n✓✓✓ All TargetListing tests passed")