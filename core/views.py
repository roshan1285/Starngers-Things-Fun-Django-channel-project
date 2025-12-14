from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Count
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Friends
from .serializers import UserSearchSerializer

def signup(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.errors:
            # Print errors to console for debugging if needed
            print(form.errors) 
        if form.is_valid():
            user = form.save()
            auth_login(request, user) # Auto-login after register
            return redirect('home') # Change 'home' to your landing page URL name
    else:
        form = RegisterForm()

    return render(request, 'sign_up.html', {'form': form})

def login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.errors:
            # Print errors to console for debugging if needed
            print(form.errors)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home') # Change 'home' to your landing page URL name
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('landing') # Change 'landing' to your landing page URL name

def landing(request):
    return render(request, 'landing.html')

@login_required
def home(request):
    if not request.user.is_authenticated:
        return redirect('landing')   # logged-in home
    return render(request, 'home.html')

@api_view(['GET'])
def search_users(request):
    query = request.GET.get('q', '').strip()
    user = request.user

    if query:
        # PROFESSIONAL LOGIC:
        # 1. Search ALL users matching the name
        # 2. Exclude the superuser or yourself if you want
        users = User.objects.filter(username__icontains=query).exclude(id=user.id)[:10]
    else:
        # DEFAULT: Show only my accepted friends (Limit 10)
        # We find friend IDs first
        friend_ships = Friends.objects.filter(
            (Q(sender=user) | Q(receiver=user)) & Q(status=2)
        )
        # Extract the IDs of the OTHER person
        friend_ids = []
        for f in friend_ships:
            if f.sender == user:
                friend_ids.append(f.receiver.id)
            else:
                friend_ids.append(f.sender.id)
        
        users = User.objects.filter(id__in=friend_ids)[:10]

    # Pass 'request' to serializer context so it knows who YOU are
    serializer = UserSearchSerializer(users, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    sender = request.user

    existing_friendship = Friends.objects.filter(
        (Q(sender=sender, receiver=receiver) |
        Q(sender=receiver, receiver=sender))
    ).first()

    if existing_friendship:
        return Response({'status':'error','message':'Signal already established or pending.'})
    
    new_friendship = Friends.objects.create(
        sender=sender,
        receiver=receiver,
        status=1
    )

    return Response({'status':'success','new_state':'sent'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_friend_request(request, user_id):
    sender = get_object_or_404(User, id=user_id)
    receiver = request.user

    friendship = Friends.objects.filter(sender=sender,receiver=receiver,status=1).first()

    if not friendship:
        return Response({'status':'error','message':'No incoming signal found.'})
    
    friendship.status = 2
    friendship.save()

    return Response({'status':'success','new_state':'accepted'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_friend_request(request, user_id):
    sender = get_object_or_404(User, id=user_id)
    receiver = request.user

    friendship = Friends.objects.filter(sender=sender,receiver=receiver,status=1).first()

    if not friendship:
        return Response({'status':'error','message':'No incoming signal foung.'})
    
    friendship.status = 3
    friendship.save()

    return Response({'status':'success','new_state':'accepted'})