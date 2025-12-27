from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError('Le login est obligatoire')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'Radmin')
        return self.create_user(login, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Rtable', 'Table'),
        ('Rservent', 'Serveur/Servante'),
        ('Rcuisinier', 'Cuisinier'),
        ('Rcomptable', 'Comptable'),
        ('Radmin', 'Administrateur'),
    ]

    login = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            MinLengthValidator(6, message="Le login doit contenir au moins 6 caractères"),
            RegexValidator(
                regex=r'^[a-zA-Z0-9]+$',
                message='Le login ne peut contenir que des lettres et des chiffres'
            )
        ]
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['role']

    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.login} ({self.get_role_display()})"

    def has_role(self, *roles):
        return self.role in roles
