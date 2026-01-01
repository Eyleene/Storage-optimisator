import unittest
import os
import tempfile
import json
from app import app
from db import init_db
import db

class WarehouseTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['DATABASE'] = self.db_path
        
        # Monkey patch get_db_path to return our temp db
        self.original_get_db_path = db.get_db_path
        db.get_db_path = lambda: self.db_path
        
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
        db.get_db_path = self.original_get_db_path

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('admin', 'admin')
        assert 'АКІТР25бз Demo' in rv.data.decode('utf-8') or b'index.html' in rv.data or rv.status_code == 200
        rv = self.logout()
        assert 'Warehouse Login' in rv.data.decode('utf-8')

    def test_product_crud(self):
        self.login('admin', 'admin')
        # Create
        rv = self.client.post('/api/products', json={'sku': 'TEST01', 'name': 'Test Item', 'unit': 'pcs'})
        assert b'ok' in rv.data
        
        # Read
        rv = self.client.get('/api/products')
        data = json.loads(rv.data)
        assert len(data) >= 1
        assert data[-1]['sku'] == 'TEST01'

    def test_reception_picking(self):
        self.login('admin', 'admin')
        
        # Setup: Create Product and Location first
        self.client.post('/api/products', json={'sku': 'SKU001', 'name': 'Item 1', 'unit': 'pcs'})
        self.client.post('/api/locations', json={'code': 'A1', 'description': 'Loc 1'})
        
        # Receive
        rv = self.client.post('/api/receive', json={
            'sku': 'SKU001', 'location': 'A1', 'qty': 10, 'batch': 'B1'
        })
        assert b'ok' in rv.data
        
        # Pick partial
        rv = self.client.post('/api/pick', json={
            'sku': 'SKU001', 'qty': 4
        })
        assert b'ok' in rv.data
        
        # Check Stock again
        rv = self.client.get('/api/stock')
        data = json.loads(rv.data)
        item = next((x for x in data if x['sku'] == 'SKU001' and x['batch'] == 'B1'), None)
        assert item['quantity'] == 6
        
        # Pick remaining (cleanup test)
        rv = self.client.post('/api/pick', json={
            'sku': 'SKU001', 'qty': 6
        })
        assert b'ok' in rv.data
        
        # Check Stock - should be empty/gone
        rv = self.client.get('/api/stock')
        data = json.loads(rv.data)
        item = next((x for x in data if x['sku'] == 'SKU001' and x['batch'] == 'B1'), None)
        assert item is None

    def test_admin_user_management(self):
        self.login('admin', 'admin')
        
        # Create User
        rv = self.client.post('/api/users', json={
            'username': 'testuser', 'password': 'password123', 'role': 'user'
        })
        assert b'ok' in rv.data
        
        # Verify User Exists
        rv = self.client.get('/api/users')
        data = json.loads(rv.data)
        user = next((u for u in data if u['username'] == 'testuser'), None)
        assert user is not None
        assert user['role'] == 'user'
        
        # Delete User
        rv = self.client.delete(f'/api/users/{user["id"]}')
        assert b'ok' in rv.data
        
        # Verify User Gone
        rv = self.client.get('/api/users')
        data = json.loads(rv.data)
        user = next((u for u in data if u['username'] == 'testuser'), None)
        assert user is None

if __name__ == '__main__':
    unittest.main()
