from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from .forms import RegisterForm, PostForm
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import Post
from django.http import HttpResponseRedirect
from django.contrib import messages



# View for home page
def home(request):
    # Retrieve posts, adjust the query if needed (e.g., order by created date)
    posts = Post.objects.all().order_by('-created')  # Or any other criteria you prefer

    return render(request, 'social/home.html', {
        'posts': posts,
        'user': request.user,  # Pass the user object to the template
    })


# View for registration page
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log in the user after successful registration
            return redirect('home')  # Use URL name for redirection
    else:
        form = RegisterForm()
    
    return render(request, 'registration/register.html', {"form": form})

# View for login page
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Use auth_login to avoid name conflict with the view
            return redirect('home')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

# View for logout
def logout_view(request):
    auth_logout(request)
    return redirect('home')  # Redirect to home page after logout







@login_required(login_url="/login")
@permission_required("social.add_post", login_url="/login", raise_exception=True)
def create_post(request, post_id=None):
    post = None

    # If post_id is provided, fetch the post for editing
    if post_id:
        post = get_object_or_404(Post, id=post_id)
        
        # Check if the user is either the author or in the "mod" group
        if post.author != request.user and not request.user.groups.filter(name='mod').exists():
            return HttpResponseForbidden("You do not have permission to edit this post.")

    # Handle form submission
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')  # Redirect to the post list after saving
    else:
        form = PostForm(instance=post)  # Pre-fill the form if editing

    return render(request, 'social/create_post.html', {'form': form, 'post': post})



# @login_required(login_url="/login")
# def post_list(request):
#     posts = Post.objects.all()
#     is_mod = request.user.groups.filter(name='mod').exists()

#     # Get the 'default' group, which manages banned users
#     default_group = Group.objects.get(name='default')

#     # Get all users who are part of the 'default' group (banned users)
#     banned_users = default_group.user_set.all()

#     # Create a set of banned user IDs for easier lookup in the template
#     banned_user_ids = set(banned_users.values_list('id', flat=True))

#     # Prepare a dictionary to check if post authors are mods
#     post_authors_mod_status = {
#         post.id: post.author.groups.filter(name='mod').exists() for post in posts
#     }

#     if request.method == "POST":
#         action = request.POST.get("action")
#         user_id = request.POST.get("user-id")
#         post_id = request.POST.get("post-id")

#         if action == "ban_user":
#             user_to_ban = User.objects.filter(id=user_id).first()
#             if user_to_ban and not user_to_ban.groups.filter(name="default").exists():
#                 # Add user to 'default' group (ban)
#                 default_group.user_set.add(user_to_ban)
#                 messages.success(request, f"{user_to_ban.username} has been banned.")
#                 return HttpResponseRedirect(reverse('post_list'))

#         elif action == "unban_user":
#             user_to_unban = User.objects.filter(id=user_id).first()
#             if user_to_unban and user_to_unban.groups.filter(name="default").exists():
#                 # Remove user from 'default' group (unban)
#                 default_group.user_set.remove(user_to_unban)
#                 messages.success(request, f"{user_to_unban.username} has been unbanned.")
#                 return HttpResponseRedirect(reverse('post_list'))

#         elif action == "ban_mod":
#             user_to_ban = User.objects.filter(id=user_id).first()
#             if user_to_ban and user_to_ban.groups.filter(name="mod").exists():
#                 # Remove user from 'mod' group (ban mod)
#                 user_to_ban.groups.remove(Group.objects.get(name="mod"))
#                 messages.success(request, f"{user_to_ban.username} has been banned from mods.")
#                 return HttpResponseRedirect(reverse('post_list'))

#         elif action == "unban_mod":
#             user_to_unban = User.objects.filter(id=user_id).first()
#             if user_to_unban and not user_to_unban.groups.filter(name="mod").exists():
#                 # Add user back to 'mod' group (unban mod)
#                 user_to_unban.groups.add(Group.objects.get(name="mod"))
#                 messages.success(request, f"{user_to_unban.username} has been unbanned as a mod.")
#                 return HttpResponseRedirect(reverse('post_list'))

#         elif action == "delete":
#             post = Post.objects.filter(id=post_id).first()
#             if post and (post.author == request.user or request.user.has_perm("social.delete_post")):
#                 post.delete()
#                 messages.success(request, f"Post deleted successfully!")
#                 return HttpResponseRedirect(reverse('post_list'))

#     return render(request, 'social/post_list.html', {
#         "posts": posts,
#         "is_mod": is_mod,
#         "banned_user_ids": banned_user_ids,
#         "post_authors_mod_status": post_authors_mod_status,
#     })




    """
def post_list(request):
    posts = Post.objects.all()
    is_mod = request.user.groups.filter(name='mod').exists()

    # Get the 'default' group, which manages banned users
    default_group = Group.objects.get(name='default')

    # Get all users who are part of the 'default' group (banned users)
    banned_users = default_group.user_set.all()

    # Create a set of banned user IDs for easier lookup in the template
    banned_user_ids = set(banned_users.values_list('id', flat=True))

    if request.method == "POST":
        action = request.POST.get("action")
        user_id = request.POST.get("user-id")
        post_id = request.POST.get("post-id")

        if action == "ban":
            user_to_ban = User.objects.filter(id=user_id).first()
            if user_to_ban and user_to_ban.groups.filter(name="default").exists():
                # Remove user from 'default' group (ban)
                default_group.user_set.remove(user_to_ban)
                messages.success(request, f"{user_to_ban.username} has been banned.")
                return HttpResponseRedirect(reverse('post_list'))
            

        elif action == "unban":
            
            user_to_unban = User.objects.filter(id=user_id).first()
            if user_to_unban and not user_to_unban.groups.filter(name="default").exists():
                # Add user to 'default' group (unban)
                default_group.user_set.add(user_to_unban)
                messages.success(request, f"{user_to_unban.username} has been unbanned.")
                return HttpResponseRedirect(reverse('post_list'))

        elif action == "delete":
            post = Post.objects.filter(id=post_id).first()
            if post and (post.author == request.user or request.user.has_perm("social.delete_post")):
                post.delete()
                messages.success(request, f"Post deleted successfully!")
                return HttpResponseRedirect(reverse('post_list'))

    return render(request, 'social/post_list.html', {
        "posts": posts,
        "is_mod": is_mod,
        "banned_user_ids": banned_user_ids,
    })    
    
    """


def post_list(request):
    posts = Post.objects.all().order_by('-created')
    is_mod = request.user.groups.filter(name='mod').exists()

    # Get the 'default' group and 'mod' group
    default_group = Group.objects.get(name='default')
    mod_group = Group.objects.get(name='mod')

    # Get all users who are part of the 'default' group (banned users)
    banned_users = default_group.user_set.all()

    # Create a set of banned user IDs for easier lookup in the template
    banned_user_ids = set(banned_users.values_list('id', flat=True))

    if request.method == "POST":
        action = request.POST.get("action")
        user_id = request.POST.get("user-id")
        post_id = request.POST.get("post-id")

        user_to_act_on = User.objects.filter(id=user_id).first()

        if action == "ban":
            if user_to_act_on:
                if user_to_act_on.groups.filter(name="mod").exists():
                    # Remove from 'mod' group (ban a mod user)
                    mod_group.user_set.remove(user_to_act_on)
                    messages.info(request, f"{user_to_act_on.username} has been banned and removed from the mod group.")
                elif user_to_act_on.groups.filter(name="default").exists():
                    # Remove from 'default' group (ban a default user)
                    default_group.user_set.remove(user_to_act_on)
                    messages.info(request, f"{user_to_act_on.username} has been banned.")
                return HttpResponseRedirect(reverse('post_list'))

        elif action == "unban":
            if user_to_act_on:
                # Add the user back to the group based on their previous status
                if request.POST.get("was_mod") == "true":
                    mod_group.user_set.add(user_to_act_on)
                    messages.info(request, f"{user_to_act_on.username} has been unbanned and added back to the mod group.")
                else:
                    default_group.user_set.add(user_to_act_on)
                    messages.info(request, f"{user_to_act_on.username} has been unbanned.")
                
                return HttpResponseRedirect(reverse('post_list'))

        elif action == "delete":
            post = Post.objects.filter(id=post_id).first()
            if post and (post.author == request.user or request.user.has_perm("social.delete_post")):
                post.delete()
                messages.success(request, f"Post deleted successfully!")
                return HttpResponseRedirect(reverse('post_list'))

    return render(request, 'social/post_list.html', {
        "posts": posts,
        "is_mod": is_mod,
        "banned_user_ids": banned_user_ids,
    })


# @login_required(login_url="/login")
# def post_list(request):
#     posts = Post.objects.all()
#     is_mod = request.user.groups.filter(name='mod').exists()
#     banned_users = {user.id: not user.groups.filter(name='default').exists() for user in User.objects.all()}

#     if request.method == "POST":
#         action = request.POST.get("action")
#         user_id = request.POST.get("user-id")
#         post_id = request.POST.get("post-id")

#         if action == "ban":
#             user_to_ban = User.objects.filter(id=user_id).first()
#             if user_to_ban and user_to_ban.groups.filter(name="default").exists():
#                 user_to_ban.groups.remove(Group.objects.get(name="default"))
#                 success(request, f"User banned successfully!")
#                 return HttpResponseRedirect(reverse('post_list'))  # Redirect immediately

#         elif action == "unban":
#             user_to_unban = User.objects.filter(id=user_id).first()
#             if user_to_unban:
#                 group, created = Group.objects.get_or_create(name="default")
#                 group.user_set.add(user_to_unban)
#                 success(request, f"User unbanned successfully!")
#                 return HttpResponseRedirect(reverse('post_list'))  # Redirect immediately

#         elif action == "delete":
#             post = Post.objects.filter(id=post_id).first()
#             if post and (post.author == request.user or request.user.has_perm("social.delete_post")):
#                 post.delete()
#                 success(request, f"Post deleted successfully!")  # Add success message
#                 return HttpResponseRedirect(reverse('post_list'))

#     return render(request, 'social/post_list.html', {
#         "posts": posts,
#         "is_mod": is_mod,
#         "banned_users": banned_users,
#     })