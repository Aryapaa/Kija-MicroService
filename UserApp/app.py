from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

HASURA_API_URL = 'https://flying-dingo-28.hasura.app/v1/graphql'
HASURA_API_KEY = 'VMk2qKcMIReoIA5H82r0JX6XE2OGJ442lPPdyjDfHmnx6Dg3VTs8T52kxENOOKUV'

def fetch_users_from_hasura():
    query = '''
        query GetUsers {
            Kija1_User {
                idUser
                email
                nama
                password
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
        return data['data']['Kija1_User']
    else:
        print('Error fetching users from Hasura:', response.status_code, response.text)
        return []
    
def fetch_user_from_hasura(user_id):
    query = '''
        query GetUser($userId: Int!) {
            Kija1_User(where: {idUser: {_eq: $userId}}) {
                idUser
                email
                nama
                password
            }
        }
    '''
    
    headers = {
        'Content-Type': 'application/json',
        'x-hasura-admin-secret': HASURA_API_KEY
    }

    variables = {
        'userId': user_id
    }

    response = requests.post(HASURA_API_URL, json={'query': query, 'variables': variables}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print('GraphQL Errors:', data['errors'])
            return None
        return data['data']['Kija1_User'][0] if data['data']['Kija1_User'] else None
    else:
        print('Error fetching user from Hasura:', response.status_code, response.text)
        return None
    
@app.route('/users')
def get_users():
    users = fetch_users_from_hasura()
    return jsonify(users)

@app.route('/user/<int:user_id>')
def get_user_by_id(user_id):
    user = fetch_user_from_hasura(user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5002)
