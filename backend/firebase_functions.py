from firebase_admin import auth
from django.conf import settings
from google.cloud.firestore_v1.base_query import FieldFilter, BaseCompositeFilter
from google.cloud.firestore_v1.types import StructuredQuery
def get_token(auth_header):
    # Access the Firebase ID token from the request headers 
    token_prefix = 'Bearer '
    if auth_header.startswith(token_prefix):
        # Extract the token by removing the 'Bearer ' prefix
        token = auth_header[len(token_prefix):]
        return token
    else:
        # Handle the case where the Authorization header is not formatted correctly
        return False
def verifyToken(id_token):
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)

            # Access user information from the decoded token
            user_uid = decoded_token['uid']

            return (True, user_uid)
        except auth.InvalidIdTokenError as e:
            # Handle invalid token error
            return (False, )

def get_document_path(field_name, value, collection_name):
    """
    Parameters: field_name (The name of the field), value (The value of the field), collection_name (The name of the collection)
    This function returns the document path when it receives a field name, its value, and collection name by making a query to the database
    returns: None (no document found) or a reference.path (One document found)
    """
    # Reference to the collection
    collection_ref = settings.FIRESTORE_DB.collection(collection_name)

    # Query to find the document with the specified name
    query = collection_ref.where(filter = FieldFilter(field_name, "==", value)).limit(1)
    
    # Execute the query
    results = query.stream()

    # Check if the document was found
    if results:
        for doc in results:
            # Return the path of the document
            return doc.reference.path

    # Return None if the document was not found
    return None

def get_document_path_id(value, collection_name):
    """
    Parameters: field_name (The name of the field), value (The value of the field), collection_name (The name of the collection)
    This function returns the document path when it receives a field name, its value, and collection name by making a query to the database
    returns: None (no document found) or a reference.path (One document found)
    """
    # Reference to the collection
    document_ref = settings.FIRESTORE_DB.collection(collection_name).document(value)
    doc = document_ref.get()
    if doc.exists:
        return doc.reference.path
    else:
        return None

def add_document_to_collection(document, collection):
    try:
        main_collection_ref = settings.FIRESTORE_DB.collection(collection)
        main_document_ref = main_collection_ref.add(document)
        return main_document_ref
    except:
        return None

def add_subdocument_to_document(subdocument, name_subcollection, document):
    try:
        subcollection_ref = document.collection(name_subcollection)
        subdocument_ref = subcollection_ref.add(subdocument)
        return subdocument_ref
    except:
        return None

def is_value_unique(field, value, collection):
    try:
        # Build the query to find documents with the specified value
        query = settings.FIRESTORE_DB.collection(collection).where(filter = FieldFilter(field, "==", value)).limit(1)
        # Execute the query
        query_result = query.stream()
        # Check if there are no documents with the specified value
        return not any(query_result)
    except Exception as e:
        # Handle Firestore query errors
        print(f"Error querying Firestore: {e}")
        return None
    
def get_uid_from_field(field, value, collection):
    try:
        #Specifying the collection
        collection_ref = settings.FIRESTORE_DB.collection(collection)
        query = collection_ref.where(filter = FieldFilter(field, '==', value)).limit(1)
        docs = query.stream()
        for doc in docs:
            return True, doc.id
        return False, None
    except:
        return False, None
def get_field_value(collection_name, document_id, field_name):
    # Reference to the collection
    collection_ref = settings.FIRESTORE_DB.collection(collection_name)
    # Reference to the document
    document_ref = collection_ref.document(document_id)
    # Get the document snapshot
    document_snapshot = document_ref.get()
    # Check if the document exists
    if document_snapshot.exists() :
        # Get the field value
        field_value = document_snapshot.get(field_name)
        return field_value
    else:
        print(f"Document '{document_id}' not found in collection '{collection_name}'.")
        return None

def update_field_in_document(collection_name, document_id, field_name, new_value):
    try:
        # Reference to the document
        doc_ref = settings.FIRESTORE_DB.collection(collection_name).document(document_id)

        # Update the specific field in the document
        doc_ref.update({field_name: new_value})
        return True
    except:
        return False
    
def query_composite_filter(name_field1, value1, name_field2, value2, collection_name):
    #Checking if the username has the same email

    try:
        # Making a composite_filter that requires a user with the same email and username
        composite_filter = BaseCompositeFilter(
            # If you use StructuredQuery.CompositeFilter.Operator.AND here it gives the same effect as chaining "where" functions
            operator=StructuredQuery.CompositeFilter.Operator.AND,
            filters=[
                FieldFilter(name_field1, "==", value1),
                FieldFilter(name_field2, "==", value2)
            ]
        )
        # Query the Firestore collection to check if any user has the given username
        user_query = settings.FIRESTORE_DB.collection(collection_name).where(filter=composite_filter).limit(1)
        existing_user = user_query.stream()
        # If existing_user has 1 user, the username has the same email
        return existing_user
    except Exception as e:
        # Handle Firestore query errors
        print(f"Error querying Firestore: {e}")
        return None
