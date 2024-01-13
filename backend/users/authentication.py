from firebase_admin import auth
from google.cloud.firestore_v1.base_query import FieldFilter, BaseCompositeFilter
from google.cloud.firestore_v1.types import StructuredQuery
import resend
import json
import http.client
from django.conf import settings
from password_strength import PasswordPolicy

def username_match_email(username, email):
    #Checking if the username has the same email

    try:
        # Making a composite_filter that requires a user with the same email and username
        composite_filter = BaseCompositeFilter(
            # If you use StructuredQuery.CompositeFilter.Operator.AND here it gives the same effect as chaining "where" functions
            operator=StructuredQuery.CompositeFilter.Operator.AND,
            filters=[
                FieldFilter("username", "==", username),
                FieldFilter("email", "==", email)
            ]
        )
        # Query the Firestore collection to check if any user has the given username
        user_query = settings.FIRESTORE_DB.collection("users").where(filter=composite_filter).limit(1)
        existing_user = user_query.stream()
        # If existing_user has 1 user, the username has the same email
        return any(existing_user)
    except Exception as e:
        # Handle Firestore query errors
        print(f"Error querying Firestore: {e}")
        return None
    
def is_college_email(email):
    conn = http.client.HTTPSConnection("api.apyhub.com")

    payload = "{\n    \"email\":\" " + email + "\"\n}"

    headers = {
        'apy-token': settings.APYHUB_KEY,
        'Content-Type': "application/json"
        }

    conn.request("POST", "/validate/email/academic", payload, headers)

    res = conn.getresponse()
    data = res.read()

    # Convert the JSON string to a Python dictionary
    result_dict = json.loads(data.decode("utf-8"))
    if 'error' in result_dict:
        return False
    return result_dict['data']
def get_college_from_email(email):
    try:
        domain = email.split("@")[1]
        return settings.UNIVERSITY_DATA[domain]
    except KeyError as e:
        return None
def send_email(message, recipient, subject): 
    #Sends an email with the link to the user:
    params = {
        "from": "noreply@doorsee.com",
        "to" : recipient,
        "subject": subject,
        "html": message,
    }
    resend.api_key = settings.RESEND_KEY
    email = resend.Emails.send(params)
    return email

def check_email_verification_status(email):
    #Checks if the email is already verified
    try:
        user = auth.get_user_by_email(email)
        return user.email_verified
    except auth.UserNotFoundError:
        return None  # Handle the case where the user does not exist

def check_password_strength(password):
    # Define a password policy
    policy = PasswordPolicy.from_names(
        length=12,      # minimum length: 12 characters
        uppercase=1,   # need min. 1 uppercase letters
        numbers=1,     # need min. 1 digits
        special=1,     # need min. 1 special characters
    )

    # Test the password against the policy
    result = policy.test(password)
    # Check if the password is valid
    if len(result) == 0:
        return True, "Password is strong."
    else:
        # Password is not valid, provide feedback and suggestions
        return False, (str(obj) for obj in result)

