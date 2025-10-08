import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending notifications via external API
    """

    BASE_URL = "https://notifications.k3scluster.tech/"

    def __init__(self):
        self.jwt_token = getattr(settings, "NOTIFICATION_JWT_TOKEN", "")
        self.owner_id = getattr(settings, "NOTIFICATION_OWNER_ID", "")

    def send_confirmation_email(self, email, full_name, confirmation_code, even_name):
        """
        Send confirmation email with verification code
        """
        subject = f"Registration Confirmation: {even_name}"
        message = f"""
        Hello {full_name}!
        
        You have successfully registered for the event "{even_name}".
        
        Your confirmation code: {confirmation_code}
        """

        payload = {
            "owner_id": self.owner_id,
            "to": email,
            "subject": subject,
            "message": message,
            "notification_type": "email",
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jwt_token}",
        }

        try:
            response = requests.post(
                f"{self.BASE_URL}/api/notifications",
                json=payload,
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                logger.info(f"Notification sent successfully to {email}")
                return True
            else:
                logger.error(
                    f"Notification sending error: {response.status_code} - {response.text}"
                )

                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Notification service connection error: {e}")
            return False

    def is_configured(self):
        """
        Check if notification credentials are configured
        """
        return bool(self.jwt_token and self.owner_id)
