import pytest
from app import app
import os



@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def login(client, email, password):
    return client.post('/login', data=dict(
        email=email,
        tp_password=password
    ), follow_redirects=True)

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Experience the captivating blend of Fragrance.' in response.data

def test_register_page(client):
    response = client.post('/register', data=dict(
        name="Test User",
        email="test_user@rapheebeuty.com",
        tp_password="test123"
    ), follow_redirects=True)
    assert response.status_code == 200
    if b'Login to RapheeBeauty' in response.data:
        assert True
    else:
        assert b'Customer already exists' in response.data


def test_login_page(client):
    response = login(client, email="test_user@rapheebeuty.com",
        password="test123")
    assert response.status_code == 200

    if b'Welcome Test User!' in response.data:
        assert True
    else:
        assert b'Invalid Credentials.' in response.data


def test_logout_page(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login to RapheeBeauty' in response.data

def test_product_page(client):
    response = client.get('/shop')
    assert response.status_code == 200
    assert b'Product' in response.data

def test_add_to_cart_page(client):
    login_response = login(client, email="test_user@rapheebeauty.com",
        password="test123")
    assert login_response.status_code == 200
    assert b'Welcome Test User!' in login_response.data
    with client.session_transaction() as session:
        session['email'] = 'test_user@rapheebeuty.com'
    response = client.post('/addToCart/152', follow_redirects=True)
    assert response.status_code == 200
    assert b'Shopping Cart' in response.data
    assert b'Lift + Firm Routine Rich' in response.data

def test_add_to_wishlist_page(client):
    login_response = login(client, email="test_user@rapheebeuty.com",
        password="test123")
    assert login_response.status_code == 200
    assert b'Welcome Test User!' in login_response.data
    with client.session_transaction() as session:
        session['email'] = 'test_user@rapheebeuty.com'
    response = client.get('/addToWishlist/152', follow_redirects=True)
    assert response.status_code == 200
    assert b'Wishlist' in response.data
    assert b'Lift + Firm Routine Rich' in response.data
                           