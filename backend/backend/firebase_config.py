import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import analytics

# Initialize Firebase using your project ID
#PUT EVERYTHING IN SETTINGS.PY
def initialize (): 
    firebase_admin.initialize_app({
        'projectId': 'application-e3699',
        'apiKey': "AIzaSyC-OpegqhQxdyCuRdHMgzvEMPxbilPU6zQ",
        'authDomain': "application-e3699.firebaseapp.com",
        'databaseURL': "https://application-e3699-default-rtdb.firebaseio.com",
        'projectId': "application-e3699",
        'storageBucket': "application-e3699.appspot.com",
        'messagingSenderId': "837189514724",
        'appId': "1:837189514724:web:35c79dab5963ceac16c3f1",
        'measurementId': "G-S9B36J3CVB",
    }) 

    # Get the analytics instance
    analytics_instance = analytics.default()

    # Your service account key JSON file
    cred = credentials.Certificate('backend/backend/application-e3699-firebase-adminsdk-cy15y-a5759d134e.json')

    # Initialize the app with a service account
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://application-e3699-default-rtdb.firebaseio.com'
    })

   # Replace 'your_collection' with the name of your collection
collection_ref = db.collection('your_collection')
docs = collection_ref.stream()

for doc in docs:
    print(f'{doc.id} => {doc.to_dict()}')