from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from firebase_admin import auth, firestore
from .authentication import *
import os
os.chdir('../')
from firebase_functions import delete_document, get_field_value, is_value_unique, get_uid_from_field, query_composite_filter, verifyToken
#Verify username exists
class UsernameExists(APIView):
    """
    Checks if a username already exists in the app
    Type of HTTP Request: GET
    Parameters: 
    """
    def get(self, request, *args, **kwargs):
        username = kwargs.get('username')
        if username == None: #No username was provided in the url
            return Response({'status': False, 'message': "username is not in the link"}, status = status.HTTP_400_BAD_REQUEST)
        is_unique = is_value_unique('username', username, 'users')
        if is_unique: #username is unique
            return Response({'status': True, 'message': 'username is unique'}, status = status.HTTP_200_OK)
        elif is_unique == False: #username is not unique
            return Response({'status': False, 'message': 'username is not unique'}, status = status.HTTP_200_OK)
        else: #Couldn't process the request from firestore
            return Response({'status': False, 'message': 'Database error'}, status = status.HTTP_404_NOT_FOUND)
#User sign up
class SignUp(APIView):
    """
    What's about:
    Parameters:
    """
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
            college = get_college_from_email(email)
            if college == None:
                return Response({'status': False, 'message': 'Could not find a college associated to the email provided'}, status = status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'status': False, 'message': 'Provide an email'}, status = status.HTTP_400_BAD_REQUEST)
        if query_composite_filter('username', username, 'college', college, 'users') != None and not username_match_email(username, email): 
        #verify again that the username is unique#The username can be not unique if the username matches the email of the user in the database with the same email.
            return Response({'status': False, 'message': 'Provide a unique username'}, status = status.HTTP_409_CONFLICT)
        #Check if the password is strong
        is_password_strong, message = check_password_strength(password)
        if not is_password_strong:
            return Response({'status': False, 'message': 'Provide a stronger password', 'feedback': message}, status = status.HTTP_409_CONFLICT)
        #Verify if the email is already verified, which means it is taken already.
        if check_email_verification_status(email): 
            return Response({'status': False, 'message': 'The email provided is already verified'}, status = status.HTTP_409_CONFLICT)
        #Email is not verified but is stored in the database
        elif check_email_verification_status(email) == False: 
            #Get the uid
            result, uid = get_uid_from_field('email', email, 'users')
            #Get the user with the uid from firebase authentication
            user = auth.get_user(uid)
            #Change the username in firestore
            user_ref = settings.FIRESTORE_DB.collection('users').document(uid)
            user_ref.update({'username': username})
            #Change the password in firebase authentication
            auth.update_user(
                uid,
                password = password,
            )
            #Send another verification email
            link = auth.generate_email_verification_link(email)
            subject = 'Verify your email for DoorC App'
            message = f'''<p>Hello {user},</p>
                <p>Follow this link to verify your email address.</p>
                <a href="{link}" style="text-decoration: none; cursor: pointer !important;">
                    <button style="padding: 10px 20px; font-size: 16px; color:white; background-color:#66399D; border: none; border-radius: 5px; cursor: pointer !important;">
                        Verify Account
                    </button>
                </a>
                <p>If you didn’t ask to verify this address, you can ignore this email.</p>
                <p>Thanks,</p>
                <p>Your DoorC team</p>'''
            send_email(message, email, subject)
            return Response({'status': True, 'message': 'User sign up information has been modified'}, status = status.HTTP_202_ACCEPTED)
        #verify the email is a college email, and not registered yet.
        if not is_college_email(email):
            return Response({'status': False, 'message': 'Provide a valid college email'}, status = status.HTTP_409_CONFLICT)
        #Sign up the user on firebase authentication when the user does not exist in the database
        try:

            #Does the firebase authentication sign up:
            user = auth.create_user(
                email=email,
                password=password,
                email_verified=False,
            )
            #generating email verification link and sending the email
            link = auth.generate_email_verification_link(email)
            subject = 'Verify your email for DoorC App'
            message = f'''<p>Hello {user},</p>
                <p>Follow this link to verify your email address.</p>
                <a href="{link}" style="text-decoration: none; cursor: pointer !important;">
                    <button style="padding: 10px 20px; font-size: 16px; color:white; background-color:#66399D; border: none; border-radius: 5px; cursor: pointer !important;">
                        Verify Account
                    </button>
                </a>
                <p>If you didn’t ask to verify this address, you can ignore this email.</p>
                <p>Thanks,</p>
                <p>Your DoorC team</p>'''
            send_email(message, email, subject)
            #User data updloaded on firestore
            user_data = {
                "username": username,
                "email": email,
                "college": college,
                "forums": []
            }
            # Add user data to Firestore with UID as the document ID
            user_ref = settings.FIRESTORE_DB.collection("users").document(user.uid)
            user_ref.set(user_data)
            return Response({"status": True, "message": "User signed up successfully"}, status=status.HTTP_201_CREATED)
        except auth.EmailAlreadyExistsError:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        #Add the username to firestore as a document

"""ResetPassword:
    - Receive the email address.
    - Send a link that lasts for 15 minutes to the email 
    - The user will click the link and will be prompted to type a new password
    - Change the password
    - The user receives a confirmation email indicating that their password has been successfully changed.
"""
class SendEmailToResetPassword(APIView):
    def post(self, request):
        try:
            email = request.data['email']
        except:
            return Response({"status": False, "message": "Provide an email"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            link = auth.generate_password_reset_link(email)
        except auth.EmailNotFoundError:
            return Response({"status": False, "message": "Email provided is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"status": False, "message": "Error happened"}, status=status.HTTP_400_BAD_REQUEST)
        is_valid_uid, document_id = get_uid_from_field('email', email, 'users')
        if not is_valid_uid:
            return Response({"status": False, "message": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)
        username = get_field_value('users', document_id, 'username')
        try:
            subject = 'Password Reset'
            message = f'''
                <p>Dear {username},</p>
                <p>Follow this link to reset your password.</p>
                <a href="{link}" style="text-decoration: none; cursor: pointer !important;">
                    <button style="padding: 10px 20px; font-size: 16px; color:white; background-color:#66399D; border: none; border-radius: 5px; cursor: pointer !important;">
                        Reset Password
                    </button>
                </a>
                <p>If you didn’t ask to reset the password for your account, you can ignore this email.</p>
                <p>Thanks,</p>
                <p>Your DoorC team</p>'''
            send_email(message, email, subject)
            return Response({"status": True, "message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
        except:
            return Response({"status": False, "message": "Unable to send an email"}, status=status.HTTP_400_BAD_REQUEST)

class DeleteUser(APIView):
    def delete(self, request):
        authorization_header = request.headers.get('Authorization', '')
        token = authorization_header
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        valid_uid, uid = verifyToken(token)
        if not valid_uid:
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        #Delete from firestore
        if not delete_document('users', uid):
            return Response({'status': False, 'message': 'User could not be deleted in Firestore'}, status=status.HTTP_417_EXPECTATION_FAILED)
        #Delete from Firebase Auth
        try:
            auth.delete_user(uid)
        except:
            return Response({'status': False, 'message': 'User could not be deleted from Firebase auth'}, status=status.HTTP_417_EXPECTATION_FAILED)
        #Future: Send an email letting the user know that the account has been deleted
        return Response({'status': True, 'message': 'User successfully deleted'}, status=status.HTTP_200_OK)

class AddForum(APIView):
    """
        Adds a forum reference to the user's forums list
    """
    def patch(self, request):
        """
            1. Token
            2. user id
            3. college
            4. get the forum id followed by the user
            5. Add it to the 'forums':[]
        """
        pass       

class GetForums(APIView):
    """
        Get forums followed by the user
    """
    def get(self, request):
        """
            1. Token
            2. user id
            3. College
            4. Get the [] from 'forums'
        """
        pass

class UnfollowForum(APIView):
    """
        Unfollow a forum
    """
    def patch(self, request):
        """
            1. Token
            2. user id
            3. college
            4. get the forum id followed by the user
            5. delete that forum from the [] in 'forums'
        """
        pass