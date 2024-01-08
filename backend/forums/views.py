from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import os
os.chdir('../')
from firebase_functions import *
# Create your views here.
class CreateForum(APIView):
    def post(self, request):
        authorization_header = request.headers.get('Authorization', '')
        token = authorization_header
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        valid_uid, uid = verifyToken(token)
        if not valid_uid:
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        # Assigning the author
        creator = get_document_path_id(uid, 'users')
        data = request.data
        #Obtaining the college from the user
        college = get_field_value("users", uid, "college")
        # Verifying the name of the forum
        try:
            name = data['name']
            if query_composite_filter('college', college, 'name', name, 'forums') != None:
                return Response({'status': False, 'message': f'The forum {name} already exists in the {college} community' }, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'status': False, 'message': 'Provide a name for the forum'}, status=status.HTTP_401_UNAUTHORIZED)
        # Verifying is_public field
        try:
            is_public = data['is_public']
        except:
            return Response({'status': False, 'message': 'Provide if the forum is public or private'}, status=status.HTTP_401_UNAUTHORIZED)
        document = {
            'name': name,
            'is_public': is_public,
            'college': college,
            'creator': creator
        }

        document_ref = add_document_to_collection(document, 'forums')
        if document_ref == None:
            return Response({'status': False, 'message': 'post could not be added to the database'}, status = status.HTTP_400_BAD_REQUEST)
        return Response({'status': True, 'message': 'post created successfully'}, status = status.HTTP_201_CREATED)
class ToggleForumPrivacy(APIView):
    def patch(self, request):
        """
        This function will receive a forum name and its previous privacy option and will toggle it.
        It should check the documents that have that forum name and college from the uid.
        """
        authorization_header = request.headers.get('Authorization', '')
        token = authorization_header
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        valid_uid, uid = verifyToken(token)
        college = get_field_value("users", uid, "college")
        if not valid_uid:
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            is_public = request.data['is_public']
        except:
            return Response({'status': False, 'message': 'Provide is_public value'}, status=status.HTTP_412_PRECONDITION_FAILED)
        try:
            forum_name = request.data['forum_name']
        except:
            return Response({'status': False, 'message': 'Provide a forum name'}, status=status.HTTP_412_PRECONDITION_FAILED)
        forum_doc = query_composite_filter('name', forum_name, 'college', college, 'forums')
        if forum_doc == None:
            return Response({'status': False, 'message': 'Could not find a forum'}, status=status.HTTP_400_BAD_REQUEST)
        updated_privacy = update_field_in_document('forums', forum_doc.id, 'is_public', (not is_public))
        if not updated_privacy:
            return Response({'status': False, 'message': 'Privacy not updated'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': True, 'message': 'Privacy updated'}, status=status.HTTP_200_OK)
class ChangeForumName(APIView):
    def patch(self, request):
        """
        This function will receive a forum name and will change it to the new forum name provided
        """
        #Retrieving the token
        authorization_header = request.headers.get('Authorization', '')
        token = authorization_header
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        #Getting the user uid from the token
        valid_uid, uid = verifyToken(token)
        #Getting the college name from the user
        college = get_field_value("users", uid, "college")
        if not valid_uid: #Any error that happens when trying to get a uid from the token
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        #Retrieving the current forum name
        try:
            current_forum_name = request.data['current_forum_name']
        except:
            return Response({'status': False, 'message': 'Provide the current forum name'}, status=status.HTTP_412_PRECONDITION_FAILED)
        #Retrieving the new forum name
        try:
            new_forum_name = request.data['new_forum_name']
        except:
            return Response({'status': False, 'message': 'Provide the new forum name'}, status=status.HTTP_409_CONFLICT)
        #Getting the document with the current_forum_name
        forum_doc = query_composite_filter('name', current_forum_name, 'college', college, 'forums')
        if forum_doc == None:
            return Response({'status': False, 'message': f'Could not find the forum \'{current_forum_name}\''}, status=status.HTTP_400_BAD_REQUEST)
        #verifying if the new forum name is available
        if query_composite_filter('name', new_forum_name, 'college', college, 'forums') != None:
            return Response({'status': False, 'message': f'The forum \'{new_forum_name}\' already exists in the college {college} community'}, status=status.HTTP_409_CONFLICT)
        updated_name = update_field_in_document('forums', forum_doc.id, 'name', new_forum_name)
        if not updated_name:
            return Response({'status': False, 'message': 'Forum name not modified'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'status': True, 'message': 'Forum name modifed'}, status=status.HTTP_200_OK)
class DeleteForum(APIView):
    def delete(self, request):
        """
        deletes a forum with the name of the forum
        """
        authorization_header = request.headers.get('Authorization', '')
        token = authorization_header
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        valid_uid, uid = verifyToken(token)
        if not valid_uid:
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        college = get_field_value("users", uid, "college")        
        try:
            forum_name = request.data['forum_name']
        except:
            return Response({'status': False, 'message': 'Provide the current forum name'}, status=status.HTTP_404_NOT_FOUND)
        forum_doc = query_composite_filter('name', forum_name, 'college', college, 'forums')
        if forum_doc == None:
            return Response({'status': False, 'message': f'Could not find the forum \'{forum_name}\''}, status=status.HTTP_400_BAD_REQUEST)
        if delete_document('forums', forum_doc.id):
            return Response({'status': True, 'message': 'Forum deleted'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'message': 'Could not delete forum'}, status=status.HTTP_304_NOT_MODIFIED)
#GetForumsFollowedByUser
class GetForumsFollowedByUser(APIView):
    def get(self, request):
        """
        Gets the forums followed by a user.
        """
        pass