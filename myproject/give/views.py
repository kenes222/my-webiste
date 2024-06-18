from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from .forms import *
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from validate_email import validate_email
import re 
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from geopy.distance import geodesic

def home(request):
    return render(request, 'give/home.html')


def is_valid_email(email):
    """Simple regex check for email format."""
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email)

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already used by another user.')
            elif not is_valid_email(email):
                messages.error(request, 'Email is not valid. Please enter a valid email address.')
            else:
                # Try sending the confirmation email
                try:
                    email_message = EmailMessage(
                        'Account Created Successfully',
                        'Your account has been created successfully. You can now log in.',
                        'give&share@gmail.com',
                        [email],
                        connection=get_connection(
                            username='giveshare18@gmail.com',
                            password='fhut yuqx xpua cnri',
                            fail_silently=False,
                        )
                    )
                    email_message.send(fail_silently=False)
                    user = form.save(commit=False)
                    user.is_active = True  # Activate account immediately
                    user.save()
                    messages.success(request, 'Account was created successfully and a confirmation email has been sent. You can now log in.')
                    return redirect('login')
                except Exception as e:
                    messages.error(request, 'Email is not valid or there was an issue sending the confirmation email. Please try again.')
        else:
            messages.error(request, 'Form is not valid. Please correct the errors and try again.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'give/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Email or password is incorrect')
    else:
        form = LoginForm()
    return render(request, 'give/login.html', {'form': form})


@login_required(login_url='login')
def dashboard(request):
    # Ensure the user has a profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    user_location = (profile.latitude, profile.longitude)
    posts = Post.objects.all().order_by('-created_at')
    post_list = []

    for post in posts:
        if post.latitude and post.longitude:
            post_distance = geodesic(user_location, (post.latitude, post.longitude)).km
        else:
            post_distance = float('inf')  # Assign a very high distance for posts with no location

        post_list.append({
            'post': post,
            'distance': post_distance
        })

    # Sort the posts by distance first and then by creation time
    post_list.sort(key=lambda x: (x['distance'], -x['post'].created_at.timestamp()))

    context = {
        'posts': [post_info['post'] for post_info in post_list]
    }

    return render(request, 'give/dashboard.html', context)

@login_required(login_url='login')
def create_post(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        category_id = request.POST.get('category')
        new_category_name = request.POST.get('category_new')
        images = request.FILES.getlist('images')
        uploaded_file_ids = request.POST.get('uploaded_file_ids', '')
        deleted_file_ids = request.POST.get('deleted_file_ids', '')

        category = None
        if category_id and category_id != 'none':
            category = get_object_or_404(Category, id=category_id)
        elif new_category_name:
            category, _ = Category.objects.get_or_create(
                user=request.user,
                name=new_category_name
            )

        post = Post.objects.create(
            user=request.user,
            title=title,
            description=description,
            category=category
        )

        # Add files uploaded immediately
        for image in images:
            photo = Photo.objects.create(image=image, description="")
            post.photos.add(photo)

        # Add files uploaded gradually
        if uploaded_file_ids:
            for file_id in uploaded_file_ids.split(','):
                if file_id and file_id not in deleted_file_ids.split(','):
                    try:
                        photo = Photo.objects.get(id=file_id)
                        post.photos.add(photo)
                    except Photo.DoesNotExist:
                        pass

        messages.success(request, 'Post created successfully')
        return redirect('dashboard')

    categories = Category.objects.filter(user=request.user)
    return render(request, 'give/create_post.html', {'categories': categories})

@login_required(login_url='login')
def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        try:
            photo = Photo.objects.create(image=file, description="")
            return JsonResponse({'success': True, 'file_id': photo.id, 'file_url': photo.image.url})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required(login_url='login')
def delete_file(request):
    if request.method == 'POST':
        file_id = request.GET.get('file_id')
        try:
            photo = Photo.objects.get(id=file_id)
            photo.delete()
            return JsonResponse({'success': True})
        except Photo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'File does not exist'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required(login_url='login')
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    profile, created = Profile.objects.get_or_create(user=post.user)
    return render(request, 'give/view_post.html', {'post': post, 'profile': profile})


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def portfolio(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile)

    posts = Post.objects.filter(user=request.user)
    post_count = posts.count()

    return render(request, 'give/portfolio.html', {
        'form': form,
        'profile': profile,
        'posts': posts,
        'post_count': post_count,
    })

@login_required(login_url='login')
def my_posts(request):
    posts = Post.objects.filter(user=request.user)
    return render(request, 'give/my_posts.html', {'posts': posts})

@login_required(login_url='login')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user:
        post.delete()
        messages.success(request, 'Post deleted successfully')
    else:
        messages.error(request, 'You do not have permission to delete this post')
    return redirect('my_posts')

@login_required(login_url='login')
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user != request.user:
        messages.error(request, 'You do not have permission to edit this post')
        return redirect('my_posts')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()

            # Handle the addition of new images
            images = request.FILES.getlist('images')
            for image in images:
                photo = Photo.objects.create(image=image, description="")
                post.photos.add(photo)

            # Handle the deletion of images
            images_to_delete = request.POST.getlist('delete_images')
            if images_to_delete:
                for image_id in images_to_delete:
                    photo = Photo.objects.get(id=image_id)
                    post.photos.remove(photo)
                    photo.delete()

            messages.success(request, 'Post updated successfully')
            return redirect('my_posts')
    else:
        form = PostForm(instance=post)

    return render(request, 'give/edit_post.html', {'form': form, 'post': post})

@login_required(login_url='login')
def search(request):
    form = SearchForm()
    posts = []
    categories = []
    users = []
    query = ""
    search_type = ""
    if request.method == 'GET':
        query = request.GET.get('query', '')
        if query:
            if query.startswith('@'):
                username_query = query[1:]
                users = Profile.objects.filter(username__icontains=username_query)
                search_type = "user"
                if not users:
                    messages.info(request, "No users found with that username.")
            else:
                posts = Post.objects.filter(title__icontains=query)
                categories = Category.objects.filter(name__icontains=query)
                users = Profile.objects.filter(username__icontains=query)
                search_type = "all"
                if not posts:
                    messages.info(request, "No posts found with that title.")
                if not categories:
                    messages.info(request, "No categories found with that name.")
                if not users:
                    messages.info(request, "No users found with that username.")
    return render(request, 'give/search.html', {
        'form': form, 
        'query': query, 
        'posts': posts, 
        'categories': categories, 
        'users': users, 
        'search_type': search_type
    })

@login_required(login_url='login')
def portfolio2(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    posts = Post.objects.filter(user=user)
    return render(request, 'give/portfolio2.html', {
        'profile': profile,
        'posts': posts,
        'post_count': posts.count()
    })


@login_required
def start_private_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    chats = PrivateChat.objects.filter(participants=request.user).filter(participants=other_user)

    if chats.exists():
        chat = chats.first()
    else:
        chat = PrivateChat.objects.create()
        chat.participants.add(request.user)
        chat.participants.add(other_user)
    
    return redirect('private_chat', chat_id=chat.id)


@login_required
def private_chat(request, chat_id):
    chat = get_object_or_404(PrivateChat, id=chat_id)
    other_user = chat.participants.exclude(id=request.user.id).first()
    messages = chat.messages.all()  # Use the related_name 'messages'

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.sender = request.user
            message.save()
            DeletedChat.objects.filter(user=request.user, chat=chat).delete()
            return redirect('private_chat', chat_id=chat.id)
    else:
        form = MessageForm()

    context = {
        'chat': chat,
        'profile': other_user.profile,
        'messages': messages,
        'form': form
    }
    return render(request, 'give/private_chat.html', context)

@login_required
def chat_list(request):
    deleted_chats = DeletedChat.objects.filter(user=request.user).values_list('chat_id', flat=True)
    chats = PrivateChat.objects.filter(participants=request.user).exclude(id__in=deleted_chats)
    query = request.GET.get('q')
    if query:
        chats = chats.filter(participants__username__icontains=query).distinct()
    return render(request, 'give/chat_list.html', {'chats': chats})


@login_required
def delete_chat(request):
    if request.method == 'POST':
        chat_ids = request.POST.getlist('chat_ids')
        print("Chat IDs to delete:", chat_ids)  # Debug statement
        if chat_ids:
            for chat_id in chat_ids:
                chat = get_object_or_404(PrivateChat, id=chat_id)
                print(f"Marking chat {chat.id} as deleted for user {request.user}")  # Debug statement
                DeletedChat.objects.get_or_create(user=request.user, chat=chat)
            return redirect('chat_list')
        else:
            print("No chat IDs received")  # Debug statement
    return redirect('chat_list')


@csrf_exempt
@login_required
def save_location(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # Use an external API to get location details
        url = f'https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={latitude}&longitude={longitude}&localityLanguage=en'
        response = requests.get(url)
        location_data = response.json()

        # Save location data to the database
        user = request.user
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.country = location_data.get('countryName')
        user_profile.city = location_data.get('city')
        user_profile.state = location_data.get('principalSubdivision')
        user_profile.latitude = latitude
        user_profile.longitude = longitude
        user_profile.save()

        return JsonResponse(location_data)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
