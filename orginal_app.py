from flask import Flask, render_template, send_file, make_response
import csv
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# Initialize Firebase Admin SDK with your service account key
cred = credentials.Certificate("perfectkey-bc35f-firebase-adminsdk-mj5eo-2d903258ae.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://perfectkey-bc35f-default-rtdb.firebaseio.com/'
})

# Get a reference to the Firebase Realtime Database
ref = db.reference()


@app.route('/')
def index():
    # Get user data from Firebase Realtime Database
    user_data = get_user_data()
    
    # Render HTML template with user data
    return render_template('index.html', user_data=user_data)


@app.route('/download')
def download_data():
    # Get all data from the Realtime Database
    all_data = ref.get()

    # Create a CSV string
    csv_data = ""
    for user_email, user_data in all_data['users'].items():
        for word_data in user_data['words'].values():
            csv_data += f"{user_email},{word_data['word']},{word_data['timestamp']}\n"

    # Create a response with the CSV data
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=firebase_data.csv"
    response.headers["Content-type"] = "text/csv"

    return response


def get_user_data():
    # Get a reference to the 'users' node
    users_ref = ref.child('users')

    # Initialize an empty list to store user data
    user_data = []

    # Get all user emails
    user_emails = users_ref.get().keys()

    # Iterate over each user email
    for email in user_emails:
        # Get a reference to the 'words' node under the user's email
        words_ref = users_ref.child(email).child('words')

        # Get all words for this user
        words_data = words_ref.get()

        # Append user data to the list
        user_data.append({
            'email': email,
            'words': words_data.values() if words_data else []
        })

    return user_data


if __name__ == '__main__':
    app.run(host='0.0.0.0')
