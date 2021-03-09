from django.contrib.auth.base_user import BaseUserManager

def normalize_email(email: str) -> str:
	"""Normalizes an email address"""
	return BaseUserManager.normalize_email(email)
