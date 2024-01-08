from django.shortcuts import render
from datetime import datetime
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
import os
os.chdir('../')
from firebase_functions import *
# Create your views here.
class CreatePost(APIView):
    def post(self, request):
        # The json or dictionary sent to this function must contain:
        """
            - allow_comment: bool (optional) .
            - anonymous_author: bool (optional) .
            - description: string (required) .
            - author: user_id from the token provided (required) .
            - images: List of image links (optional) 
            - is_posted: bool (optional) .
            - is_modified: bool (optional) .
            - modification_date: datetime (optional) -> this will be added after modifying the post
            - location: string (optional) .
            - posted_date: datetime (optional) It will be stored when the is_posted is true .
            - title: string (required) .
            - forum: reference to a forum (required) .
            - Survey: Subcollection that is optional and contains:
                - survey_title: string (required)
                - num_responses (set to 0)
                - options: map 
                    - name_option: map
                        - image: string (url) optional
                        - result: integer
                        - content: string
        """ 
        """We verify that the token sent is valid"""
        # We obtain the token
        authorization_header = request.headers.get('Authorization', '')
        token = authorization_header
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        # We verify if the token is valid and get the user_id from the token
        valid_uid, uid = verifyToken(token)
        if not valid_uid:
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        author = get_document_path_id(uid, 'users')
        # Getting the college of the user:
        college = get_field_value("users", uid, "college")
        # Getting the required fields to make a post
        try:
            forum = data['forum']
        except:
            return Response({'status': False, 'message': 'Provide a forum'}, status = status.HTTP_400_BAD_REQUEST)
        # Getting the document path for the forum using a composite query (name_forum + name_college)
        forum = query_composite_filter('name', forum, 'college', college, 'forums').reference.path
        if forum == None:
            return Response({'status': False, 'message': 'Could not find the forum'}, status = status.HTTP_400_BAD_REQUEST)
        try:
            title = data['title']
        except:
            return Response({'status': False, 'message': 'Provide a title'}, status = status.HTTP_400_BAD_REQUEST)
        try:
            description = data['description']
        except:
            return Response({'status': False, 'message': 'Provide a description'}, status = status.HTTP_400_BAD_REQUEST)
        
        #optional fields: allow_comment, anonymous_author, and is_posted
        try:
            allow_comment = data['allow_comment']
        except:
            allow_comment = False

        try:
            anonymous_author = data['anonymous_author']
        except:
            anonymous_author = False

        try:
            is_posted = data['is_posted']
        except:
            is_posted = False
        document = {
            'title': title,
            'author': author,
            'forum': forum,
            'description': description,
            'allow_comment': allow_comment,
            'anonymous_author': anonymous_author,
            'is_posted': is_posted,
            'is_modified': False,
        }

        try: 
            date = datetime.fromtimestamp(float(data['date']))
            if is_posted:
                document['posted_date'] = date
            else:
                document['drafted date'] = date
        except:
            return Response({'status': False, 'message': 'provide a valid posted_date'}, status = status.HTTP_400_BAD_REQUEST)
        
        if 'location' in data:
            location = data['location']
            document['location'] = location

        #Then, create the post document inside the post collection.

        document_ref = add_document_to_collection(document, 'posts')
        if document_ref == None:
            return Response({'status': False, 'message': 'post could not be added to the database'}, status = status.HTTP_400_BAD_REQUEST)
        
        #Make a survey subcollection
        if 'survey' in data:
            """Structure
            survey: {
                survey_title: ...,
                num_responses: 0,
                options: {
                    text_of_option: {
                        image_url : '/cat.jpg',
                        times_selected: 1
                    }, 
                    text_of_option: {
                        image_url : '/cat.jpg',
                        times_selected: 1
                    }
                }
            }
            """
            for option in data['survey']['options']:
                option['result'] = 0
            data['survey']['num_responses'] = 0
            subdocument_ref = add_subdocument_to_document(data['survey'],'Survey', document_ref)
            if subdocument_ref == None:
                return Response({'status': False, 'message': 'survey could not be added to the post'}, status = status.HTTP_400_BAD_REQUEST)    
        return Response({'status': True, 'message': 'post created successfully'}, status = status.HTTP_201_CREATED)
class GetDraftsFromUser(APIView):
    def get(self, request):
        #For every draft return the name of the post, name of the forum, date
                # We obtain the token
        authorization_header = request.headers.get('Authorization', '')
        token = authorization_header
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        # We verify if the token is valid and get the user_id from the token
        valid_uid, uid = verifyToken(token)
        if not valid_uid:
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        #With the user uid I can make a composite filter (user == uid + is_posted == False) that would get me a list with all the posts that are drafts
        """Then, I can make a dictionary: 
            {
                id1: {
                    title: title,
                    forum: forum,
                    date: date
                },
                id2: {
                    title: title,
                    forum: forum,
                    date: date
                },
            }
        """
        author = get_document_path_id(uid, 'users')
        list_drafts =  query_composite_filter_docs('author', author, 'is_posted', False, 'posts')
        if list_drafts == None:
            return Response({'status': False, 'message': 'No drafts associated with the user'}, status=status.HTTP_401_UNAUTHORIZED)
class EditPost(APIView):
    def put(self, request):
        #Placeholder for the function edit_post
        pass
    
class GetPostsFromForum(APIView):
    def get(self, request):
        pass
class GetPostsFromUser(APIView):
    def get(self, request):
        pass
class ClickOnOption(APIView):
    def patch(self, request):
        pass
class GetRandomPostsFromCollege(APIView):
    def get(self, request,  *args, **kwargs):
        pass
class DeletePost(APIView):
    def delete(self, request):
        pass