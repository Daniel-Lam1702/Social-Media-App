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
        if author == None:
            return Response({'status': False, 'message': 'User does not exist.'}, status=status.HTTP_401_UNAUTHORIZED)
        # Getting the college of the user:
        college = get_field_value("users", uid, "college")
        # Getting the required fields to make a post
        try:
            forum_id = data['forum_id']
        except:
            return Response({'status': False, 'message': 'Provide a forum_id'}, status = status.HTTP_400_BAD_REQUEST)
        if get_document_reference_id(forum_id, "forums") == None:
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
            'author': get_document_ref_with_id(author, "users"),
            'forum_id': get_document_ref_with_id(forum_id,"forums"),
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
        #We have to return the post information
            
        return Response({'status': True, 'message': 'post created successfully', 'post_id': document_ref.id}, status = status.HTTP_201_CREATED)
class EditPost(APIView):
    def patch(self, request):
        #Get a dictionary with the fields that are changed
        """
        {
            post_id: ...,
            field_name : ...,
            is_survey_created: bool,
            survey : {
            
            }
        }
        """
        #Placeholder for the function edit_post
        authorization_header = request.headers.get('Authorization', '')
        token = authorization_header
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        # We verify if the token is valid and get the user_id from the token
        valid_uid, uid = verifyToken(token)
        if not valid_uid:
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        #Requesting the post_id from the dictionary
        try:
            post_id = data.pop('post_id')
        except:
            return Response({'status': False, 'message': 'Provide the post_id'}, status=status.HTTP_401_UNAUTHORIZED)
        #Authorization header -> check if the user == author to change the post
        author = get_field_value("posts", post_id, "author").id
        if author == None:
            return Response({'status': False, 'message': 'Cannot find the post_id in the database'}, status=status.HTTP_404_NOT_FOUND)
        if author != uid:
            return Response({'status': False, 'message': 'User is not allowed to edit the post'}, status=status.HTTP_401_UNAUTHORIZED)
        #Check if is_posted provided is false, return an error because it cannot be unposted
        if "is_posted" in data and not data['is_posted']:
            return Response({'status': False, 'message': 'A post cannot be set back to a draft'}, status=status.HTTP_401_UNAUTHORIZED)
        #Check if the post is_posted or not from the database
        is_posted = get_field_value('posts', post_id, 'is_posted')
        if is_posted == None:
            return Response({'status': False, 'message': 'Cannot find the post_id in the database'}, status=status.HTTP_404_NOT_FOUND)
        #Check if the user requests to post it and is_posted is false, then add a posted_date.
        if "is_posted" in data and data['is_posted'] and is_posted == False:
            data['posted_date'] = datetime.utcnow().astimezone(pytz.utc)
        #Add an edited_time to that dictionary if it was posted.
        if is_posted:
            data['modified_time'] = datetime.utcnow().astimezone(pytz.utc)
            #is_modified will be set to true:
            data["is_modified"] = True
        #Update the fields in the document
        #Getting the reference of the post
        post_ref = get_document_ref_with_id(post_id, "posts")
        #Popping the survey from the data if it exists
        # Request that the frontend sends a field "make_survey" to see if the survey has to be created or modified.
        if "make_survey" in data:
            make_survey = data.pop('make_survey')
            try:
                survey = data.pop('survey')
            except:
                return Response({'status': False, 'message': 'Provide a survey'}, status=status.HTTP_401_UNAUTHORIZED)
            # If make_survey == true: create the survey subdocument with the options
            if make_survey:
                survey_addition = {'num_responses': 0, 'survey_title': survey['survey_title']}
                survey_ref = add_subdocument_to_document(survey_addition, 'survey', post_ref)
                survey_ref = survey_ref[1]
                options = dict()
                for option in survey['options']:
                    options[option] = {}
                    if "image_url" in survey['options'][option]:
                        options[option]['image_url'] = survey['options'][option]['image_url']
                    options[option]['times_selected'] = 0
                options_ref = add_subdocument_to_document(options, 'options', survey_ref)
                if options_ref == None:
                    return Response({'status': False, 'message': 'options could not be added to the survey'}, status = status.HTTP_400_BAD_REQUEST)
            # elif query -> num_resposes == 0: modify the survey subdocument
            else: #This part is tricky because survey has another collection that is options
                try:
                    post_ref.collection('survey').document(survey.pop('id'))
                except:
                    return Response({'status': False, 'message': 'Provide the survey id'}, status = status.HTTP_400_BAD_REQUEST)
        post_ref.update(data)
        # return the whole post
        return Response({'status': True, 'message': 'post modified', 'post': {}}, status=status.HTTP_200_OK)
class GetPosts(APIView):
    def get_survey(self, draft_ref):
        survey_data = {}
        survey_ref = draft_ref.collection('survey')
        for survey in survey_ref.stream():
            survey_data = survey.to_dict()
            survey_data['id'] = survey.id
            survey_data['options'] = self.get_options(survey.reference)
        return survey_data

    def get_options(self, survey_ref):
        options_ref = survey_ref.collection('options')
        for option in options_ref.stream():
            options = option.to_dict()
        return options
class GetPostsFromUser(GetPosts):
    def get(self, request):
        # We obtain the token
        authorization_header = request.headers.get('Authorization', '')
        token = authorization_header
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        # We verify if the token is valid and get the user_id from the token
        valid_uid, uid = verifyToken(token)
        if not valid_uid:
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        #Here the client decides whether we get the drafts or the posted posts
        try:
            is_posted = request.data["is_posted"]
        except:
            return Response({'status': False, 'message': 'Provide is_posted'}, status=status.HTTP_401_UNAUTHORIZED)
        #With the user uid I can make a composite filter (user == uid + is_posted == False) that would get me a list with all the posts that are drafts
        list_posts =  query_composite_filter_list('author', get_document_ref_with_id(uid, "users"), 'is_posted', is_posted, 'posts')
        if list_posts == None:
            return Response({'status': False, 'message': 'No posts associated with the user'}, status=status.HTTP_200_OK)
        posts = {}
        #Iterating through each draft
        for post in list_posts:
            #Each draft gets converted into a dictionary
            posts[post.id] = post.to_dict()
            posts[post.id]['forum_id'] = posts[post.id]['forum_id'].id
            posts[post.id]['author'] = posts[post.id]['author'].id
            #Time to get the survey subcollection
            survey = self.get_survey(post.reference)
            if survey != {}:
                posts[post.id]['survey'] = survey
        return Response({'status': True, 'posts': posts}, status=status.HTTP_200_OK)
class GetPostsFromForum(GetPosts):
    def get(self, request):
        # We obtain the token
        authorization_header = request.headers.get('Authorization', '')
        token = authorization_header
        if not token:
            return Response({'status': False, 'message': 'Invalid Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)
        # We verify if the token is valid and get the user_id from the token
        valid_uid, uid = verifyToken(token)
        if not valid_uid:
            return Response({'status': False, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        #Here the client decides whether we get the drafts or the posted posts
        try:
            forum_id = request.data["forum_id"]
        except:
            return Response({'status': False, 'message': 'Provide the forum_id'}, status=status.HTTP_401_UNAUTHORIZED)
        #With the user uid I can make a composite filter (user == uid + is_posted == False) that would get me a list with all the posts that are drafts
        list_posts =  query_composite_filter_list('forum_id', get_document_ref_with_id(forum_id, "forums"), 'is_posted', True, 'posts')
        if list_posts == None:
            return Response({'status': False, 'message': 'No posts associated with the user'}, status=status.HTTP_200_OK)
        posts = {}
        #Iterating through each draft
        for post in list_posts:
            #Each draft gets converted into a dictionary
            posts[post.id] = post.to_dict()
            posts[post.id]['forum_id'] = posts[post.id]['forum_id'].id
            posts[post.id]['author'] = posts[post.id]['author'].id
            #Time to get the survey subcollection
            survey = self.get_survey(post.reference)
            if survey != {}:
                posts[post.id]['survey'] = survey
        return Response({'status': True, 'posts': posts}, status=status.HTTP_200_OK)
class ClickOnOption(APIView):
    def patch(self, request):
        pass
class GetRecentPostsFollowedByUser(APIView):
    def get(self, request,  *args, **kwargs):
        pass
class DeletePost(APIView):
    def delete(self, request):
        pass