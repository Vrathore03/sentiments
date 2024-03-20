
import sys
sys.path.append('src')
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import firebase_admin
from firebase_admin import credentials, auth, db
from train import main as train_model
from predict import predict_moods
from utils import setup_logging, log_exception
from models import MoodClassifier
from src.datasets import MoodDataset
import torch


app = Flask(__name__)
# setup_logging()

# Initialize Firebase Admin SDK
cred = credentials.Certificate("perfectkey-bc35f-firebase-adminsdk-mj5eo-2d903258ae.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://perfectkey-bc35f-default-rtdb.firebaseio.com/'
})
# Get a reference to the Firebase Realtime Database
ref = db.reference()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            # Authenticate user using Firebase Admin SDK
            user = auth.get_user_by_email(email)
            # Redirect to typed_words page if login is successful
            return redirect(url_for('typed_words', email=email))
        except firebase_admin.auth.UserNotFoundError:
            return "User not found"
        except Exception as e :
            print('login---- \n' , e)
    return render_template('login.html')

@app.route('/train', methods=['POST'])
def train():
    try:
        train_model()
        return "Model trained successfully!"
    except Exception as e:
        # log_exception(e)
        return "An error occurred while training the model.", 500

@app.route('/typed_words', methods=['GET'])
def typed_words():
    try:
        users_ref = ref.child('users')

        # Initialize an empty list to store user data
        all_user_data = []

        # Get all user emails
        all_user_emails = users_ref.get().keys()

        for user_email in all_user_emails:
            words_ref = users_ref.child(user_email).child('words')
            
            # Get all words for this user
            words_data = words_ref.get()
            
            # Append user data to the list
            all_user_data.append({
                'email': user_email,
                'words': words_data.values() if words_data else []
            })

        a_u_d = pd.DataFrame(all_user_data)
        email = request.args.get('email')
        email = email.replace('.', '_')  # Get email from query parameters
        row = a_u_d[a_u_d['email'] == email]
        word = pd.DataFrame(row['words'].iloc[0])
        print(word)

        # Convert word lists to the required format
        word_lists = word['word'].to_list()
        print('word_lists -----> ' , word_lists)


        data = pd.read_csv('dataset/hinglish_emotion_dataset.csv')
        dataset = MoodDataset(data)
        # Instantiate the model
        vocab_size = len(dataset.word_to_idx)
        output_dim = len(dataset.mood_to_idx)

        # Load the model
        model = MoodClassifier(vocab_size = vocab_size, embedding_dim=100, hidden_dim=128, output_dim = output_dim)
        model.load_state_dict(torch.load('models/mood_classifier.pth'))
  

        # Perform prediction
        output = predict_moods(model, dataset, word_lists)

        # Render the template with necessary data
        return render_template('mood_analysis.html', email=email.replace('_', '.'), output = output)

    except Exception as e:
        # log_exception(e)
        return "An error occurred. Please try again later.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
