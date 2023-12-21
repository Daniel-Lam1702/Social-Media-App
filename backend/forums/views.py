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
        print(authorization_header)
        token = authorization_header
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        valid_uid, uid = verifyToken(token)
        if not valid_uid:
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        print('uid', uid)
        # Assigning the author
        creator = get_document_path_id(uid, 'users')
        data = request.data
        # Verifying college
        try:
            college = data['college']
        except:
            return Response({'status': False, 'message': 'Provide the college of the forum'}, status=status.HTTP_401_UNAUTHORIZED) 
        # Verifying the name of the forum
        try:
            name = data['name']
            if any(query_composite_filter('college', college, 'name', name, 'forums')):
                return Response({'status': False, 'message': 'The forum name already exists in ' + college}, status=status.HTTP_401_UNAUTHORIZED)
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
        This function will receive a forum name and its privacy option and will toggle it
        """
        authorization_header = request.headers.get('Authorization', '')
        token = get_token(authorization_header)
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        valid_uid, uid = verifyToken(token)
        if not valid_uid:
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            is_public = request.data['is_public']
        except:
            return Response({'status': False, 'message': 'Provide is_public value'}, status=status.HTTP_304_NOT_MODIFIED)
        try:
            forum_name = request.data['forum_name']
        except:
            return Response({'status': False, 'message': 'Provide a forum name'}, status=status.HTTP_304_NOT_MODIFIED)
        is_found, forum_uid = get_uid_from_field('name', forum_name, 'forums')
        if not is_found:
            return Response({'status': False, 'message': 'Could not find a forum'}, status=status.HTTP_304_NOT_MODIFIED)
        updated_privacy = update_field_in_document('forums', forum_uid, 'is_public', not is_public)
        if not updated_privacy:
            return Response({'status': False, 'message': 'Privacy not updated'}, status=status.HTTP_304_NOT_MODIFIED)
        
        return Response({'status': True, 'message': 'Privacy updated'}, status=status.HTTP_200_OK)
class ChangeForumName(APIView):
    def patch(self, request):
        """
        This function will receive a forum name and will change it to the new forum name provided
        """
        authorization_header = request.headers.get('Authorization', '')
        token = get_token(authorization_header)
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        valid_uid, uid = verifyToken(token)
        if not valid_uid:
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            current_forum_name = request.data['current_forum_name']
        except:
            return Response({'status': False, 'message': 'Provide the current forum name'}, status=status.HTTP_304_NOT_MODIFIED)
        try:
            new_forum_name = request.data['new_forum_name']
        except:
            return Response({'status': False, 'message': 'Provide the new forum name'}, status=status.HTTP_304_NOT_MODIFIED)
        is_found, forum_uid = get_uid_from_field('name', current_forum_name, 'forums')
        if not is_found:
            return Response({'status': False, 'message': 'Could not find a forum'}, status=status.HTTP_304_NOT_MODIFIED)
        updated_name = update_field_in_document('forums', forum_uid, 'name', new_forum_name)
        if not updated_name:
            return Response({'status': False, 'message': 'Forum name not modified'}, status=status.HTTP_304_NOT_MODIFIED)
        
        return Response({'status': True, 'message': 'Forum name modifed'}, status=status.HTTP_200_OK)
class DeleteForum(APIView):
    def delete(self, request):
        """
        deletes a forum with the name of the forum
        """
        authorization_header = request.headers.get('Authorization', '')
        token = get_token(authorization_header)
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        valid_uid, uid = verifyToken(token)
        if not valid_uid:
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            forum_name = request.data['forum_name']
        except:
            return Response({'status': False, 'message': 'Provide the current forum name'}, status=status.HTTP_304_NOT_MODIFIED)
        is_found, forum_uid = get_uid_from_field('name', forum_name, 'forums')
        if not is_found:
            return Response({'status': False, 'message': 'Could not find a forum'}, status=status.HTTP_304_NOT_MODIFIED)
        document_ref = get_document_path_id(forum_uid, 'forums')
        if document_ref == None:
            return Response({'status': False, 'message': 'Could not find a forum'}, status=status.HTTP_304_NOT_MODIFIED)
        try:
            document_ref.delete()
            return Response({'status': True, 'message': 'Forum deleted'}, status=status.HTTP_200_OK)
        except:
            return Response({'status': False, 'message': 'Could not delete forum'}, status=status.HTTP_304_NOT_MODIFIED)
