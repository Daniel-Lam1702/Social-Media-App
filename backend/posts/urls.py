from django.urls import path
from . import views
urlpatterns = [
    path('create-post/', views.CreatePost.as_view(), name='create-post'),
    path('get-posts-from-forum/', views.GetPostsFromForum.as_view(), name='get-posts-from-forum'),
    path('get-posts-from-user/', views.GetPostsFromUser.as_view(), name='get-posts-from-user'),
    path('get-drafts-from-user/', views.GetDraftsFromUser.as_view(), name='get-drafts-from-user'),
    path('click-on-option/', views.ClickOnOption.as_view(), name='click-on-option'),
    path('get-random-posts-from-college/<str:college>/', views.GetRandomPostsFromCollege.as_view(), name='get-random-public-posts-from-college'),
    path('delete-post/', views.DeletePost.as_view(), name='delete-post'),
    path('edit-post/', views.EditPost.as_view(), name='edit-post'),
    #path('generate-invitation-link/', views.GenerateInvitationLink.as_view(), name='generate-invitation-link')
]