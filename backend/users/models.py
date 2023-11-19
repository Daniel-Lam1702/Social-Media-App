from django.db import models

class UserProfile(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=100)
    username = models.CharField(max_length=50)
    profile_picture = models.URLField()
    description = models.TextField(default="Default description")  # Set a default value here
    # Add other user-related fields

class UserEvent(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='events')  # Change 'user' to 'user_profile'
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    class_name = models.CharField(max_length=50)
    description = models.TextField()

class User(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=100)  # Use a secure password hashing method in a real application
    username = models.CharField(max_length=50)
    profile_picture = models.URLField()
    description = models.TextField()
    # Add other user-related fields
    posts_created = models.ManyToManyField('ForumPost', related_name='users_created')
    forums_followed = models.ManyToManyField('Forum', related_name='users_following')
    schedule = models.ManyToManyField(UserEvent, related_name='users')

class Forum(models.Model):
    name = models.CharField(max_length=50)
    is_public = models.BooleanField(default=True)
    college = models.CharField(max_length=50)

class ForumPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.BooleanField(default=False)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    image_video = models.URLField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    is_posted = models.BooleanField(default=True)
    posted_date = models.DateTimeField()
    no_comment = models.IntegerField(default=0)
    allow_save = models.BooleanField(default=True)
    anonymous = models.BooleanField(default=False)

class Comment(models.Model):
    image_video = models.URLField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    posted_date = models.DateTimeField()
    parent_post = models.ForeignKey(ForumPost, on_delete=models.CASCADE)
    anonymous = models.BooleanField(default=False)

class Chatroom(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatrooms_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatrooms_user2')

class ChatMessage(models.Model):
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    content = models.TextField()
    video = models.URLField()
    picture = models.URLField()

class Class(models.Model):
    course_name = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    professor = models.ForeignKey('Professor', on_delete=models.CASCADE)

class Professor(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    rating = models.FloatField()

class Feedback(models.Model):
    rating = models.FloatField()
    course = models.CharField(max_length=50)
    description = models.TextField()

# Create your models here.
