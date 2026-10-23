
import logging
import os
import smtplib

from .celery_app import celery_app
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@celery_app.task
def log_shipment_created(shipment_id: int):
    logger.info(
        "Shipment created",
        extra={"shipment_id": shipment_id},
    )

    return {
        "shipment_id": shipment_id,
        "status": "logged",
    }


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def send_shipment_email(
    self,
    recipient_email: str,
    shipment_id: int,
    destination: str,
):
    logger.info(
        "starting shipment email",
        extra = {
            "shipment_id": shipment_id,
            "task_id": self.request.id
        }
    )
    message = EmailMessage()

    message["Subject"] = f"Shipment #{shipment_id} created"
    message["From"] = os.environ["BREVO_SENDER_EMAIL"]
    message["To"] = recipient_email

    message.set_content(
        f"Your shipment #{shipment_id} has been created.\n"
        f"Destination: {destination}\n"
        "Thank you for using Shipment Tracker!"
    )

    try:
        with smtplib.SMTP(
            os.environ["BREVO_SMTP_HOST"],
            int(os.environ.get("BREVO_SMTP_PORT", "587")),
            timeout=20,
        ) as server:
            server.starttls()
            server.login(
                os.environ["BREVO_SMTP_LOGIN"],
                os.environ["BREVO_SMTP_KEY"],
            )
            server.send_message(message)

        logger.info(
            "Shipment confirmation email sent",
            extra={"shipment_id": shipment_id},
        )

        return {
            "shipment_id": shipment_id,
            "status": "sent",
        }

    except (
        OSError,
        TimeoutError,
        smtplib.SMTPServerDisconnected,
        smtplib.SMTPConnectError,
    ) as exc:
        logger.warning(
            "Temporary email failure for shipment %s",
            shipment_id,
        )
        raise self.retry(exc=exc)

    except Exception:
        logger.exception(
            "Failed to send shipment confirmation email",
            extra={"shipment_id": shipment_id},
        )
        raise
