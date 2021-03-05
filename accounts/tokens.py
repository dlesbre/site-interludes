# Code adapted from django.contrib.auth.tokens

from datetime import date

from django.conf import settings
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36


class EmailVerificationTokenGenerator:
	"""
	Strategy object used to generate and check tokens for the email
	verification mechanism.
	"""
	key_salt = "shared.EmailVerificationTokenGenerator"
	secret = settings.SECRET_KEY

	def make_token(self, user):
		"""
		Return a token that can be used once to do a password reset
		for the given user.
		"""
		return self._make_token_with_timestamp(user, self._num_days(self._today()))

	def check_token(self, user, token):
		"""
		Check that a password reset token is correct for a given user.
		"""
		if not (user and token):
				return False
		# Parse the token
		try:
				ts_b36, _ = token.split("-")
		except ValueError:
				return False

		try:
				ts = base36_to_int(ts_b36)
		except ValueError:
				return False

		# Check that the timestamp/uid has not been tampered with
		if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
				return False

		return True

	def _make_token_with_timestamp(self, user, timestamp):
		# timestamp is number of days since 2001-1-1.  Converted to
		# base 36, this gives us a 3 digit string until about 2121
		ts_b36 = int_to_base36(timestamp)
		hash_string = salted_hmac(
				self.key_salt,
				self._make_hash_value(user, timestamp),
				secret=self.secret,
		).hexdigest()[::2]  # Limit to 20 characters to shorten the URL.
		return "%s-%s" % (ts_b36, hash_string)

	def _make_hash_value(self, user, timestamp):
		"""
		Hash the user's primary key and its email to make sure that the token
		is invalidated after email change.

		Running this data through salted_hmac() prevents cracking attempts,
		provided the secret isn't compromised.
		"""
		return str(user.pk) + user.email + str(timestamp)

	def _num_days(self, dt):
		return (dt - date(2001, 1, 1)).days

	def _today(self):
		# Used for mocking in tests
		return date.today()


email_token_generator = EmailVerificationTokenGenerator()
