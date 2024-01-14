from django.shortcuts import render
from datetime import datetime
import pytz
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
        author = get_document_reference_id(uid, 'users')
        # Getting the college of the user:
        college = get_field_value("users", uid, "college")
        # Getting the required fields to make a post
        try:
            forum_id = data['forum_id']
        except:
            return Response({'status': False, 'message': 'Provide a forum_id'}, status = status.HTTP_400_BAD_REQUEST)
        if get_document_path_id( forum_id, "forums") == None:
            return Response({'status': False, 'message': 'Cannot find the forum id in the database'}, status=status.HTTP_404_NOT_FOUND)
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
            'forum_id': forum_id,
            'description': description,
            'allow_comment': allow_comment,
            'anonymous_author': anonymous_author,
            'is_posted': is_posted,
            'is_modified': False,
        }

        try: 
            # Get the current date and time
            current_time = datetime.utcnow().astimezone(pytz.utc)
            if is_posted:
                document['posted_date'] = current_time
            else:
                document['drafted_date'] = current_time
        except:
            return Response({'status': False, 'message': 'provide a valid date'}, status = status.HTTP_400_BAD_REQUEST)
        
        if 'location' in data:
            location = data['location']
            document['location'] = location

        #Then, create the post document inside the post collection.

        document_ref = add_document_to_collection(document, 'posts')
        if document_ref == None:
            return Response({'status': False, 'message': 'post could not be added to the database'}, status = status.HTTP_400_BAD_REQUEST)
        document_ref = document_ref[1]
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
            survey = {'num_responses': 0, 'survey_title': data['survey']['survey_title']}
            survey_ref = add_subdocument_to_document(survey, 'survey', document_ref)
            if survey_ref == None:
                return Response({'status': False, 'message': 'survey could not be added to the post'}, status = status.HTTP_400_BAD_REQUEST)    
            survey_ref = survey_ref[1]
            options = dict()
            for option in data['survey']['options']:
                options[option] = {}
                if "image_url" in data['survey']['options'][option]:
                    options[option]['image_url'] = data['survey']['options'][option]['image_url']
                options[option]['times_selected'] = 0
            options_ref = add_subdocument_to_document(options, 'options', survey_ref)
            if options_ref == None:
                return Response({'status': False, 'message': 'options could not be added to the survey'}, status = status.HTTP_400_BAD_REQUEST)    
        return Response({'status': True, 'message': 'post created successfully'}, status = status.HTTP_201_CREATED)
class GetDraftsFromUser(APIView):
    def get(self, request):
        #For every draft return all the details
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
        list_drafts =  query_composite_filter_list('author', uid, 'is_posted', False, 'posts')
        if list_drafts == None:
            return Response({'status': False, 'message': 'No drafts associated with the user'}, status=status.HTTP_401_UNAUTHORIZED)
        drafts = {}
        for draft in list_drafts:
            drafts[draft.id] = {'title': draft.get('title'), 'forum': draft.get('forum'), 'date': draft.get('drafted_date')}
        return Response({'status': True, 'drafts': drafts}, status=status.HTTP_302_FOUND)
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