
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import firebase_admin
from firebase_admin import credentials, auth, db
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import csv
import io


app = Flask(__name__)
# setup_logging()

# Initialize Firebase Admin SDK
cred = credentials.Certificate("perfectkey-bc35f-firebase-adminsdk-mj5eo-2d903258ae.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://perfectkey-bc35f-default-rtdb.firebaseio.com/'
})
# Get a reference to the Firebase Realtime Database
ref = db.reference()


# Load the dataset
df = pd.read_csv('datasets/sen-mood.csv')

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['Sentence'])
y = df['Mood']

# Train the Naive Bayes model
model = MultinomialNB()
model.fit(X, y)

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
        email = request.args.get('email') # Get email from query parameters
        email = email.replace('.', '_')  
        row = a_u_d[a_u_d['email'] == email]
        word = pd.DataFrame(row['words'].iloc[0])
        print(word)
        word['word'].to_csv(f"/config/workspace/user_data/user_data_{email}.csv", index = False)
        return predict_mood(f"/config/workspace/user_data/user_data_{email}.csv")
        
    except Exception as e:
        # log_exception(e)
        print(e)
        return "An error occurred. Please try again later.", 500



def predict_mood(csv_file):
    # Read the CSV file
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        csv_input = csv.reader(f)
        
        # Extract sentences from CSV
        sentences = [row[0] for row in csv_input]

        # Vectorize the input
        input_vector = vectorizer.transform(sentences)

        # Predict the mood for each sentence
        moods = model.predict(input_vector)

        # Calculate percentages of each mood
        mood_counts = pd.Series(moods).value_counts(normalize=True)
        print(mood_counts)

        # Get overall mood
        overall_mood = mood_counts.idxmax()

        # Prepare response
        results = {
            'overall_mood': overall_mood,
            'Normal_percentage': round(mood_counts.get('Normal', 0) * 100, 2),
            'happiness_percentage': round(mood_counts.get('Happy', 0) * 100, 2),
            'sadness_percentage': round(mood_counts.get('Sad', 0) * 100, 2),
            'stress_percentage': round(mood_counts.get('Stressed', 0) * 100, 2)
        }

        return render_template('major1.html', results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000 , debug=True)