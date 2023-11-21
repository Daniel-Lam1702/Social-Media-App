# users/management/commands/populate_data.py

from django.core.management.base import BaseCommand
from google.cloud import firestore
import os
from dotenv import load_dotenv  # Add this line
import json
from datetime import datetime
from django.conf import settings  # Import the settings module


# Load environment variables from .env
load_dotenv()

class Command(BaseCommand):
    help = 'Populate data in Firestore from hardcoded JSON'

    def handle(self, *args, **options):
        # Use the credentials from settings.py
        credentials = settings.FIREBASE_CREDENTIALS

        # Initialize Firestore client with service account credentials
        db = firestore.Client.from_service_account_info(credentials)
           

        # Load JSON data from file
        with open('/Users/abrahamwestleyguan/Projects/Social-Media-App-Backend/backend/files/data.json') as json_file:
            data = json.load(json_file)

        # Iterate over Users
        for user_id, user_data in data['Users'].items():
            user_profile = {
                'email': user_data['email'],
                'password': user_data['password'],
                'username': user_data['username'],
                'profile_picture': user_data['profile_picture'],
                'description': user_data['description'],
                # Add other user-related fields
            }

            # Create User Profile document
            user_ref = db.collection('user_profiles').document(user_id)
            user_ref.set(user_profile)

            # Iterate over User Events
            for event_id, event_data in user_data['schedule'].items():
                start_time = datetime.fromisoformat(event_data['start_time'])
                end_time = datetime.fromisoformat(event_data['end_time'])

                user_event = {
                    'user': user_ref,
                    'start_time': start_time,
                    'end_time': end_time,
                    'class_name': event_data['class'],
                    'description': event_data['description'],
                }

                # Create User Event document
                event_ref = db.collection('user_events').document(event_id)
                event_ref.set(user_event)

        self.stdout.write(self.style.SUCCESS('Data added successfully'))
