from django.urls import path
from . import views
urlpatterns = [
    path('create-forum/', views.CreateForum.as_view(), name='create-forum'),
    path('toggle-forum-privacy/', views.ToggleForumPrivacy.as_view(), name='toggle-forum-privacy'),
    path('change-forum-name/', views.ChangeForumName.as_view(), name='change-forum-name'),
    path('delete-forum/', views.DeleteForum.as_view(), name='delete-forum'),
]