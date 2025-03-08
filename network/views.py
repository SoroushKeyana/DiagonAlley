from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json
from .models import User, Post, Follow, Comment
from .forms import NewPost, ProfilePicture


def index(request):
    posts = Post.objects.all().order_by('-time_stamp')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    profile = request.user

    for post in page_obj:
        post.comments_list = post.comments.all()

    return render(request, "network/index.html",{
        "form": NewPost(),
        "profile": profile,
        "page_obj": page_obj,
    })


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(username=profile).order_by('-time_stamp')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        is_following = profile.followers.filter(follower__username__iexact=request.user.username).exists()
        is_own_profile = request.user.username == username
        form = ProfilePicture(instance=request.user)
    else:
        is_following = False
        is_own_profile = False
        form = None

    followers = profile.followers.all()
    following = profile.following.all()

    if request.method == "POST" and request.user.is_authenticated:
        current_user = request.user

        if 'follow' in request.POST:
            action = request.POST['follow']

            if action == "follow":
                if not Follow.objects.filter(follower=current_user, following=profile).exists():
                    Follow.objects.create(follower=current_user, following=profile)
                is_following = True

            elif action == "unfollow":
                Follow.objects.filter(follower=current_user, following=profile).delete()
                is_following = False

        elif 'profile_picture' in request.FILES:
            form = ProfilePicture(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse("profile", args=[username]))

    for post in page_obj:
        post.comments_list = post.comments.all()

    return render(request, "network/profile_page.html", {
        "profile": profile,
        "page_obj": page_obj,
        "is_following": is_following,
        "is_own_profile": is_own_profile,
        "form": form,
        "following": following,
        "followers": followers
    })


def search(request):
    search_query = request.GET.get('search', '')

    if search_query:
        users = User.objects.filter(
            Q(username__icontains=search_query)
        )
    else:
        users = User.objects.all()
    return render(request, "network/search.html", {"users": users})


@login_required
def following(request):
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(username__in=following_users).order_by('-time_stamp')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for post in page_obj:
        post.comments_list = post.comments.all()

    return render(request, "network/following.html", {
        "page_obj": page_obj
    })


@login_required
def add_new_post(request):
    form = NewPost()

    if request.method == "POST":
        form = NewPost(request.POST, request.FILES)

        if form.is_valid():
            content = form.cleaned_data['content']
            image = form.cleaned_data['image']
            new_post = Post(content=content, username=request.user, image=image)
            new_post.save()
            
            return HttpResponseRedirect(reverse('index'))
        
    return render(request, "network/add_new_post.html", {
        "form": form
    })


@login_required
def delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.method == 'POST':
        data = request.POST
        if "content" in data:
            post.content = data["content"]

        if "remove_image" in data and data["remove_image"] == "true":
            post.image.delete(save=False)
            post.image = None

        if "image" in request.FILES:
            post.image = request.FILES["image"]
            
        post.save()
        
        return JsonResponse({
            "message": "Changes were saved successfully", 
            "content": post.content,
            "image": post.image.url if post.image else None,
        })
    

@login_required
def comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == "POST":
        comment_content = request.POST.get("content", "").strip()
        
        if not comment_content:
            return JsonResponse({"error": "Comment cannot be empty."}, status=400)

        comment = Comment.objects.create(post=post, user=request.user, content=comment_content)
        return JsonResponse({
            "message": "Comment added successfully", 
            "content": comment.content, 
            "user": request.user.username,
            "profile_picture": request.user.profile_picture.url if request.user.profile_picture else "/media/profile_pics/default_profile.png",
            "time_stamp": comment.time_stamp.strftime("%Y-%m-%d %H:%M"),
            "post_id": post_id
        })  


@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    post.save()
    
    return JsonResponse({"likes": post.likes.count(), "liked": liked})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
