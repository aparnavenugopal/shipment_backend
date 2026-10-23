from unittest.mock import MagicMock, patch
from celery.exceptions import Retry
from training.celery.tasks import log_shipment_created, send_shipment_email


def test_log_shipment_created():
    result = log_shipment_created.apply(
        args=[123]
    ).get()

    assert result == {
        "shipment_id": 123,
        "status": "logged",
    }

@patch("training.celery.tasks.smtplib.SMTP")
def test_send_shipment_email_success(mock_smtp):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    with patch.dict(
        "os.environ",
        {
            "BREVO_SENDER_EMAIL": "sender@example.com",
            "BREVO_SMTP_HOST": "localhost",
            "BREVO_SMTP_PORT": "587",
            "BREVO_SMTP_LOGIN": "test-login",
            "BREVO_SMTP_KEY": "test-key",
        },
    ):
        result = send_shipment_email.apply(
            args=[
                "customer@example.com",
                123,
                "Vijayawada",
            ]
        ).get()

    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with(
        "test-login",
        "test-key",
    )
    mock_server.send_message.assert_called_once()

    assert result == {
        "shipment_id": 123,
        "status": "sent",
    }

@patch(
    "training.celery.tasks.smtplib.SMTP",
    side_effect=OSError("Temporary SMTP connection failure"),
)
def test_send_shipment_email_retries(mock_smtp):
    with patch.dict(
        "os.environ",
        {
            "BREVO_SENDER_EMAIL": "sender@example.com",
            "BREVO_SMTP_HOST": "localhost",
            "BREVO_SMTP_PORT": "587",
            "BREVO_SMTP_LOGIN": "test-login",
            "BREVO_SMTP_KEY": "test-key",
        },
    ):
        with patch.object(
            send_shipment_email,
            "retry",
            side_effect=Retry(),
        ) as mock_retry:
            try:
                send_shipment_email.apply(
                    args=[
                        "customer@example.com",
                        123,
                        "Vijayawada",
                    ],
                    throw=True,
                )
            except Retry:
                pass
            else:
                raise AssertionError("Expected a Celery retry")

    mock_retry.assert_called_once()

