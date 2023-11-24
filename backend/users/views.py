from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from firebase_admin import auth, firestore
from .authentication import *
#Verify username exists
class UsernameExists(APIView):
    def get(self, request, *args, **kwargs):
        username = kwargs.get('username')
        if username == None: #No username was provided in the url
            return Response({'status': False, 'message': "username is not in the link"}, status = status.HTTP_400_BAD_REQUEST)
        is_unique = is_username_unique(username)
        if is_unique: #username is unique
            return Response({'status': True, 'message': 'username is unique'}, status = status.HTTP_200_OK)
        elif is_unique == False: #username is not unique
            return Response({'status': False, 'message': 'username is not unique'}, status = status.HTTP_200_OK)
        else: #Couldn't process the request from firestore
            return Response({'status': False, 'message': 'Database error'}, status = status.HTTP_404_NOT_FOUND)
#User sign up
class SignUp(APIView):
    def post(self, request):
        #Verify that the data provided has username, password, and email
        data = request.data
        if 'username' not in data and 'password' not in data and 'email' not in data:
            return Response({'status': False, 'message': 'Incomplete data'}, status = status.HTTP_400_BAD_REQUEST)
        try:
            username = data['username']
        except:
            return Response({'status': False, 'message': 'Provide a username'}, status = status.HTTP_400_BAD_REQUEST)
        try:
            password = data['password']
        except:
            return Response({'status': False, 'message': 'Provide a password'}, status = status.HTTP_400_BAD_REQUEST)
        try:
            email = data['email']
        except:
            return Response({'status': False, 'message': 'Provide an email'}, status = status.HTTP_400_BAD_REQUEST)
        #verify again that the username is unique
        if not is_username_unique(username): #The username can be not unique if the username matches the email of the user in the database with the same email.
            return Response({'status': False, 'message': 'Provide a unique username'}, status = status.HTTP_409_CONFLICT)
        #Check if the password is strong
        is_password_strong, message = check_password_strength(password)
        if not is_password_strong:
            return Response({'status': False, 'message': 'Provide a stronger password', 'feedback': message}, status = status.HTTP_409_CONFLICT)
        #Verify if the email is already verified, which means it is taken already.
        if check_email_verification_status(email):
            return Response({'status': False, 'message': 'The email provided is already verified'}, status = status.HTTP_409_CONFLICT)
        #verify the email is a college email, and not registered yet.
        if not is_college_email(email):
            return Response({'status': False, 'message': 'Provide a valid college email'}, status = status.HTTP_409_CONFLICT)
        #Sign up the user on firebase authentication
        try:
            #Does the firebase authentication sign up:
            user = auth.create_user(
                email=email,
                password=password,
                email_verified=False,
            )
            #generating email verification link
            link = auth.generate_email_verification_link(email)
            send_email(link, email, username)

            #Stores the user in firestore
            firestore_db = firestore.client()

            user_data = {
                "username": username,
                "email": email
            }
            # Add user data to Firestore with UID as the document ID
            user_ref = firestore_db.collection("users").document(user.uid)
            user_ref.set(user_data)
            return Response({"success": True, "message": "User signed up successfully"}, status=status.HTTP_201_CREATED)
        except auth.EmailAlreadyExistsError:
            # Email is in the database, but it never got verified. Therefore,
            # replace the username in the database and the password in firebase authentication
            # resend an email verification link
            return Response({'success': False, 'message': 'Email is already registered'}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        #Add the username to firestore as a document