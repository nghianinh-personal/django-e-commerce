from django.db.models import *
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have email address')
        if not username:
            raise ValueError('User must have username')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            first_name = first_name,
            last_name = last_name,
            username = username,
            email = email,
            password = password
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):
    VENDOR = 1
    CUSTOMER = 2
    ROLE_CHOICE = (
        (VENDOR, 'Vendor'),
        (CUSTOMER, 'Customer'),
    )

    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=50, unique=True)
    phone_number = CharField(max_length=20, blank=True)
    role = PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True, null=True)

    # require fiels 
    date_joined = DateTimeField(auto_now_add=True)
    last_login = DateTimeField(auto_now_add=True)
    created_date = DateTimeField(auto_now_add=True)
    modified_date = DateTimeField(auto_now=True)
    is_admin = BooleanField(default=False)
    is_staff = BooleanField(default=False)
    is_active = BooleanField(default=True)
    is_superadmin = BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self) -> str:
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label) -> bool:
        return True

    def get_role(self) -> str:
        if self.is_superadmin: return 'SuperAdmin' 
        return dict(User.ROLE_CHOICE)[self.role]


class UserProfile(Model):
    user = OneToOneField(User, on_delete=CASCADE, blank=True, null=True)

    profile_picture = ImageField(upload_to='users/profile_pictures', blank=True, null=True)
    cover_photo = ImageField(upload_to='users/cover_photos', blank=True, null=True)
    address_line_1 = CharField(max_length=50, blank=True, null=True)
    address_line_2 = CharField(max_length=50, blank=True, null=True)
    country = CharField(max_length=15, blank=True, null=True)
    state = CharField(max_length=15, blank=True, null=True)
    city = CharField(max_length=15, blank=True, null=True)
    pin_code = CharField(max_length=6, blank=True, null=True)
    latitude = CharField(max_length=20, blank=True, null=True)
    longitude = CharField(max_length=20, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)
    modified_at = DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user.email
