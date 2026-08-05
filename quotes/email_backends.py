"""Send mail through Brevo's HTTPS API instead of SMTP.

Railway blocks outbound SMTP: every attempt timed out at the TCP connect, on
ports 465 and 587, against both Naver and Brevo — while HTTPS calls to Kakao
from the same process succeed. Nothing on the mail provider's side can fix
that, so the mail leaves over port 443 like the rest of the app's traffic.

Implemented as a Django email backend so quotes.notifications keeps using the
ordinary EmailMessage API and can be switched back to SMTP by changing settings.
"""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

API_URL = 'https://api.brevo.com/v3/smtp/email'
TIMEOUT = 15


def _address(value):
    """Split 'Name <a@b.c>' into Brevo's {name, email} shape."""
    value = (value or '').strip()
    if value.endswith('>') and '<' in value:
        name, _, rest = value.rpartition('<')
        return {'name': name.strip().strip('"'), 'email': rest[:-1].strip()}
    return {'email': value}


class BrevoAPIBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        api_key = settings.BREVO_API_KEY
        if not api_key:
            logger.warning('Brevo API key missing; mail not sent.')
            return 0

        sent = 0
        for message in email_messages:
            payload = {
                'sender': _address(message.from_email),
                'to': [{'email': addr} for addr in message.to],
                'subject': message.subject,
                'textContent': message.body,
            }
            if message.reply_to:
                payload['replyTo'] = _address(message.reply_to[0])
            if message.cc:
                payload['cc'] = [{'email': a} for a in message.cc]

            request = urllib.request.Request(
                API_URL,
                data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                headers={
                    'api-key': api_key,
                    'content-type': 'application/json',
                    'accept': 'application/json',
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=TIMEOUT):
                    sent += 1
            except urllib.error.HTTPError as exc:
                # Brevo explains refusals in the body — an unverified sender or
                # a spent daily quota is invisible from the status code alone.
                detail = exc.read().decode('utf-8', 'replace')[:400]
                logger.error('Brevo rejected the message (HTTP %s): %s', exc.code, detail)
                if not self.fail_silently:
                    raise
            except Exception:
                logger.exception('Brevo API request failed')
                if not self.fail_silently:
                    raise
        return sent
