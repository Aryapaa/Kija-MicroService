from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

HASURA_API_URL = 'https://flying-dingo-28.hasura.app/v1/graphql'
HASURA_API_KEY = 'VMk2qKcMIReoIA5H82r0JX6XE2OGJ442lPPdyjDfHmnx6Dg3VTs8T52kxENOOKUV'

def fetch_reviews_from_hasura():
    query = '''
        query GetReviews {
            Kija1_Ulasan {
                idUlasan
                Ulasan
                idProduk
                idUser
            }
        }
    '''
    
    headers = {
        'Content-Type': 'application/json',
        'x-hasura-admin-secret': HASURA_API_KEY
    }

    response = requests.post(HASURA_API_URL, json={'query': query}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print('GraphQL Errors:', data['errors'])
            return []
        return data['data']['Kija1_Ulasan']
    else:
        print('Error fetching reviews from Hasura:', response.status_code, response.text)
        return []

def get_max_id_ulasan_from_hasura():
    query = '''
        query GetMaxIdUlasan {
            Kija1_Ulasan_aggregate {
                aggregate {
                    max {
                        idUlasan
                    }
                }
            }
        }
    '''
    
    headers = {
        'Content-Type': 'application/json',
        'x-hasura-admin-secret': HASURA_API_KEY
    }

    response = requests.post(HASURA_API_URL, json={'query': query}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print('GraphQL Errors:', data['errors'])
            return None
        return data['data']['Kija1_Ulasan_aggregate']['aggregate']['max']['idUlasan']
    else:
        print('Error fetching max idUlasan from Hasura:', response.status_code, response.text)
        return None

def submit_review_to_hasura(idProduk, ulasan, idUser):
    max_id_ulasan = get_max_id_ulasan_from_hasura()
    if max_id_ulasan is None:
        return False

    new_id_ulasan = max_id_ulasan + 1

    mutation = '''
        mutation InsertReview($idUlasan: Int!, $idProduk: Int!, $Ulasan: String!, $idUser: Int!) {
            insert_Kija1_Ulasan(objects: [{
                idUlasan: $idUlasan,
                Ulasan: $Ulasan,
                idProduk: $idProduk,
                idUser: $idUser
            }]) {
                affected_rows
            }
        }
    '''
    headers = {
        'Content-Type': 'application/json',
        'x-hasura-admin-secret': HASURA_API_KEY
    }
    variables = {
        'idUlasan': new_id_ulasan,
        'idProduk': int(idProduk),
        'Ulasan': ulasan,
        'idUser': int(idUser)
    }
    response = requests.post(HASURA_API_URL, json={'query': mutation, 'variables': variables}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print('GraphQL Errors:', data['errors'])
            return False
        return True
    else:
        print('Error submitting review to Hasura:', response.status_code, response.text)
        return False

@app.route('/reviews', methods=['GET'])
def get_reviews():
    product_reviews = fetch_reviews_from_hasura()
    return jsonify(product_reviews)

@app.route('/reviews/<int:idProduk>', methods=['GET'])
def get_review(idProduk):
    product_reviews = fetch_reviews_from_hasura()
    reviews = [review for review in product_reviews if review['idProduk'] == idProduk]

    if reviews:
        return jsonify({
            "idProduk": idProduk,
            "reviews": reviews
        })
    else:
        return jsonify({
            "message": "Product not found"
        }), 404

@app.route('/reviews/<int:idProduk>', methods=['POST'])
def add_review(idProduk):
    data = request.json
    ulasan = data.get('Ulasan')
    idUser = data.get('idUser')

    if ulasan and idUser:
        success = submit_review_to_hasura(idProduk, ulasan, idUser)
        if success:
            return jsonify({"message": "Review submitted successfully"}), 200
        else:
            return jsonify({"message": "Failed to submit review"}), 500
    else:
        return jsonify({"message": "Invalid data"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
