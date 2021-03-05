from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser


class EmailUserManager(BaseUserManager):
	"""User model manager that replaces username with email"""
	def create_user(self, email, password, **extra_fields):
		"""Create and save a User with the given email and password."""
		if not email:
			raise ValueError("Creating user with no email")
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, email, password, **extra_fields):
		"""Create and save a SuperUser with the given email and password."""
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		extra_fields.setdefault('is_active', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')
		return self.create_user(email, password, **extra_fields)

class EmailUser(AbstractUser):
	"""Utilisateur identifié par son email et non
	un nom d'utilisateur"""
	username = None
	email = models.EmailField('adresse email', unique=True)
	first_name = models.CharField('prénom', max_length=100)
	last_name = models.CharField("nom", max_length=100)
	email_confirmed = models.BooleanField("Email vérifié", default=False)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ("last_name", "first_name",)

	objects = EmailUserManager()

	def __str__(self):
		return self.email

	class Meta:
		verbose_name = "utilisateur"
