from django.http import HttpRequest
from django.contrib import messages, auth
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.decorators import login_required
from rest_framework import generics, mixins, permissions, viewsets, status

from .helper import *
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User, UserProfile
from .serializers import UserSerializer


# Create your views here.
def register_user(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'Register successfully !')
            return redirect('register-user')
    else:
        form = UserForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/register-user.html', context)


def register_vendor(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and vendor_form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.role = User.VENDOR
            user.save()
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor.user_profile = UserProfile.objects.get(user=user)
            vendor.save()
            send_verification_email(request=request, user=user)
            messages.success(request, 'Register successfully !')
            return redirect('register-vendor')
    else:
        form = UserForm()
        vendor_form = VendorForm()
    context = {
        'form': form,
        'vendor_form': vendor_form
    }
    return render(request, 'accounts/register-vendor.html', context)


def activate(request: HttpRequest, uidb64: str, token: str):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Your account active successfully')
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Invalid activation link')

    return redirect('dashboard')


def login(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = auth.authenticate(
            email=request.POST.get('email'),
            password=request.POST.get('password')
        )

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')
    return render(request, 'accounts/login.html')


def logout(request: HttpRequest):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request: HttpRequest):
    role: str = request.user.get_role()
    if role == 'SuperAdmin': return redirect('/admin')
    html_file_path = f'accounts/{role.lower()}-dashboard.html'
    return render (request, html_file_path)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        # Allow users to update their own account
        if self.get_object() != request.user:
            return Response({"detail": "You do not have permission to perform this action."}, status=403)
        return self.update(request, *args, **kwargs)


class UserLogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def logout(self, request):
        # Perform logout logic
        # ...

        return Response({"detail": "Successfully logged out."})


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        # Perform login logic
        # ...

        return Response({"detail": "Successfully logged in."})


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_200_OK)

class UserLogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Perform logout logic
            # ...

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST)