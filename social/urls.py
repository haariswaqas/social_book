from django.urls import path
from .views import home, register_view, login_view, logout_view, create_post, post_list

urlpatterns = [
    
    # Homepage
    path('', home, name='home'),
    
    # Registration
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # CRUD Posts
    path('post_list/', post_list, name="post_list"),
    path('create_post/', create_post, name="create_post"),
    path('edit_post/<int:post_id>/', create_post, name='edit_post'),  # New URL for editing posts
]
