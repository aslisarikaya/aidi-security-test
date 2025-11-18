import pytest
import json
import tempfile
import os
import time
from unittest.mock import patch, mock_open
import sys
sys.path.append('../src')

from server import app, get_price

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test the main route returns JSON"""
    with patch('server.get_price') as mock_price:
        mock_price.return_value = {'bitcoin': {'usd': 50000}}
        response = client.get('/')
        assert response.status_code == 200
        assert response.is_json
        data = response.get_json()
        assert 'bitcoin' in data

def test_get_price_with_fresh_cache():
    """Test price retrieval with fresh cache"""
    test_data = {'bitcoin': {'usd': 50000}}
    
    with patch('os.path.exists') as mock_exists, \
         patch('os.path.getmtime') as mock_mtime, \
         patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
        
        mock_exists.return_value = True
        mock_mtime.return_value = time.time() - 30  # 30 seconds old
        
        result = get_price()
        assert result == test_data

def test_get_price_api_call():
    """Test price retrieval when API is called"""
    test_data = {'bitcoin': {'usd': 50000}}
    
    with patch('os.path.exists') as mock_exists, \
         patch('requests.get') as mock_get, \
         patch('builtins.open', mock_open()) as mock_file:
        
        mock_exists.return_value = False
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        
        result = get_price()
        assert result == test_data