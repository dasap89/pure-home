from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.core.mail.utils import DNS_NAME
import smtplib

connection = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, local_hostname=DNS_NAME.get_fqdn())
if settings.EMAIL_USE_TLS:
	connection.ehlo()
	connection.starttls()
	connection.ehlo()

connection.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
print connection
