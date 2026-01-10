import pytest
from fastapi.testclient import TestClient
from main import app
from app.repositories.return_repository import ReturnRepository

client = TestClient(app)

# این متد قبل از اجرای تست‌ها دیتابیس را پاک می‌کند
def setup_function():
    ReturnRepository.clear_db()

def test_start_return_api():
    response = client.post('/api/returnTransaction', json={'saleId': 100})
    assert response.status_code == 201
    assert "returnId" in response.json()

def test_add_product_api():
    # 1. Start Transaction
    res_start = client.post('/api/returnTransaction', json={'saleId': 100})
    assert res_start.status_code == 201
    return_id = res_start.json()['returnId']
    
    # 2. Add Product
    response = client.post(f'/api/returnTransaction/{return_id}/product', json={
        'productCode': '123456789012',
        'amount': 2
    })
    assert response.status_code == 200

def test_delete_return_api():
    # 1. Start Transaction
    res_start = client.post('/api/returnTransaction', json={'saleId': 100})
    return_id = res_start.json()['returnId']
    
    # 2. Delete
    response = client.delete(f'/api/returnTransaction/{return_id}')
    assert response.status_code == 200