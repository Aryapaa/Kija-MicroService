from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'kijanibos'

def getProducts():
    response = requests.get('http://localhost:5000/products')
    return response.json()

def getProduct(idProduk):
    response = requests.get(f'http://localhost:5000/products/{idProduk}')
    return response.json()

def getCart(idUser):
    response = requests.get(f'http://localhost:5001/cart/{idUser}')
    return response.json()

def getReview(idProduk):
    response = requests.get(f'http://localhost:5003/reviews/{idProduk}')
    return response.json()

def submitReview(idProduk, ulasan, idUser):
    response = requests.post(f'http://localhost:5003/reviews/{idProduk}', json={'Ulasan': ulasan, 'idUser': idUser})
    if response.status_code == 200:
        return True
    else:
        return False

def verify_credentials(email, password):
    response = requests.get('http://localhost:5002/users')
    if response.status_code == 200:
        users = response.json()
        for user in users:
            if user['email'] == email and user['password'] == password:
                return user
    return None

def get_user_by_id(idUser):
    response = requests.get(f'http://localhost:5002/user/{idUser}')
    if response.status_code == 200:
        return response.json()
    else:
        return None

@app.route('/')
def getViewProducts():
    data = getProducts()
    return render_template('products.html', data=data, user=session.get('user'))

@app.route('/product/<int:idProduk>')
def getProductInfo(idProduk):
    product_info = getProduct(idProduk)
    cart_info = getCart(idProduk)
    product_review = getReview(idProduk)
    user = session.get('user')
    return render_template('product.html', info=product_info, cart=cart_info, reviews=product_review, user=user)

@app.route('/submit_review', methods=['POST'])
def handle_review():
    idProduk = request.form.get('idProduk')
    ulasan = request.form.get('Ulasan')
    idUser = request.form.get('idUser')

    if idProduk and ulasan and idUser:
        success = submitReview(int(idProduk), ulasan, int(idUser))
        if success:
            return redirect(url_for('getProductInfo', idProduk=idProduk))
        else:
            return "Failed to submit review", 500
    else:
        return "Failed to submit review due to missing data", 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = verify_credentials(email, password)
        if user:
            session['user'] = {'id': user['idUser'], 'email': user['email'], 'nama': user['nama']}
            return redirect(url_for('getViewProducts'))
        else:
            return "Invalid email or password", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/cart')
def viewCart():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    user_id = user['id']
    cart_info = getCart(user_id)
    if cart_info:
        for item in cart_info:
            product = getProduct(item['idProduk'])
            if product:
                item['product_name'] = product['namaProduk']
            else:
                item['product_name'] = 'Unknown Product'

    return render_template('cart.html', cart=cart_info, user=user)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if request.method == 'POST':
        idUser = request.form.get('idUser')
        idProduk = request.form.get('idProduk')

        print(f"Adding product to cart: idUser={idUser}, idProduk={idProduk}")

        if idUser and idProduk:
            response = requests.post('http://localhost:5001/add_to_cart', data={'idUser': idUser, 'idProduk': idProduk})

            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")

            if response.status_code == 200:
                return redirect(url_for('viewCart'))
            else:
                return "Failed to add product to cart", 500
        else:
            return "Invalid request data", 400
        
@app.route('/cart/delete', methods=['POST'])
def delete_from_cart():
    idKeranjang = request.form.get('idKeranjang')

    if idKeranjang:
        response = requests.post('http://localhost:5001/cart/delete', data={'idKeranjang': idKeranjang})
        if response.status_code == 200:
            return redirect(url_for('viewCart'))
        else:
            return "Failed to delete product from cart", 500
    else:
        return "Invalid request data", 400

if __name__ == "__main__":
    app.run(debug=True, port=5004)