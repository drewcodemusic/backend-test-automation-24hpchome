import pytest
from api.onsale_api import OnsaleAPI
from datetime import datetime
import re

class TestOnsaleAPI:
    @pytest.fixture(scope="class")
    def onsale_api(self, api_client, base_url):
        return OnsaleAPI(api_client, base_url)
    
    def test_onsale_response_structure(self, onsale_api):   # 注入了 onsale_api, 因為在fixture被固定到整個class範圍
        """Test the basic structure of the onsale API response"""
        response = onsale_api.get_onsale_products()
        
        # Check basic response structure
        assert isinstance(response, dict), "Response should be a dictionary"
        assert "data" in response, "Response should contain 'data' key"
        assert isinstance(response["data"], list), "Data should be a list"
        
        # Ensure we have data to test
        assert len(response["data"]) > 0, "Onsale data should not be empty"

    def test_slot_data_format(self, onsale_api):
        """Test the format of each slot in the response"""
        response = onsale_api.get_onsale_products()
        
        for slot in response["data"]:
            # Check required fields exist
            required_fields = ["slot", "date", "time", "status", "startTime", "endTime", "products"]
            for field in required_fields:
                assert field in slot, f"Slot should contain {field}"
            
            # Validate date format (YYYYMMDD)  regex
            assert re.match(r'^\d{8}$', slot["date"]), f"Invalid date format: {slot['date']}"
            
            # Validate time format (HH:MM)
            assert re.match(r'^\d{2}:\d{2}$', slot["time"]), f"Invalid time format: {slot['time']}"
            
            # Validate datetime formats
            datetime_format = "%Y-%m-%d %H:%M:%S"
            assert datetime.strptime(slot["startTime"], datetime_format)
            assert datetime.strptime(slot["endTime"], datetime_format)
            
            # Validate status is one of expected values
            assert slot["status"] in ["ready", "tomorrow", "now"], f"Invalid status: {slot['status']}"

    def test_product_data(self, onsale_api):
        """Test the product data within each slot"""
        response = onsale_api.get_onsale_products()
        
        for slot in response["data"]:
            assert isinstance(slot["products"], list), "Products should be a list"
            
            for product in slot["products"]:
                # Check required product fields
                required_fields = ["id", "name", "url", "image", "price"]
                for field in required_fields:
                    assert field in product, f"Product should contain {field}"
                
                # Validate product ID format (usually uppercase letters and numbers with hyphen)
                assert re.match(r'^[A-Z0-9-]+$', product["id"]), f"Invalid product ID format: {product['id']}"
                
                # Validate URL format
                assert product["url"].startswith("https://24h.pchome.com.tw/prod/")
                
                # Validate image URL
                assert product["image"].startswith("https://"), "Image URL should be HTTPS"
                
                # Validate price structure
                price = product["price"]
                assert "origin" in price, "Price should have origin value"
                assert "onsale" in price, "Price should have onsale value"
                assert isinstance(price["origin"], (int, float)), "Origin price should be numeric"
                assert isinstance(price["onsale"], (int, float)), "Onsale price should be numeric"
                assert float(price["onsale"]) <= float(price["origin"]), "Sale price should not exceed original price"
                
                # Validate discount calculation if present
                if "discount" in price and price["discount"] != None:
                    assert isinstance(price["discount"], (int, float)), "Discount should be numeric"
                    assert 0 <= float(price["discount"]) <= 100, "Discount should be between 0 and 100"

    def test_time_sequence(self, onsale_api):
        """Test that time slots are properly sequenced"""
        response = onsale_api.get_onsale_products()
        
        slots = response["data"]
        if len(slots) > 1:
            for i in range(len(slots) - 1):
                current_end = datetime.strptime(slots[i]["endTime"], "%Y-%m-%d %H:%M:%S")
                next_start = datetime.strptime(slots[i + 1]["startTime"], "%Y-%m-%d %H:%M:%S")
                assert current_end <= next_start, "Time slots should not overlap"

# slot 1 end: 2024-12-22 23:59:00
# slot 2 start: 2024-12-23 08:00:00