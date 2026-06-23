import hashlib
import hmac
import time
from config import settings


class OTPService:
    """Handles OTP generation and verification using HMAC-SHA256."""

    def __init__(self):
        self._secret = settings.OTP_SECRET.encode()
        self._length = settings.OTP_LENGTH
        self._window_seconds = settings.OTP_WINDOW_SECONDS

    def _compute_otp(self, email: str, window: int) -> str:
        """Derive a numeric OTP from secret + email + time window."""

        message = f"{email.lower()}:{window}".encode()
        digest = hmac.new(self._secret, message, hashlib.sha256).digest()

        code = int.from_bytes(digest[:4], "big") % (10**self._length)

        return str(code).zfill(self._length)

    def generate_otp(self, email: str) -> str:
        """Generate an OTP for the given email using the secret."""

        window = int(time.time()) // self._window_seconds

        return self._compute_otp(email, window)

    def verify_otp(self, email: str, otp: str) -> bool:
        """Verify the OTP for the given email using the secret."""

        current_window = int(time.time()) // self._window_seconds

        for window in [current_window, current_window - 1]:
            expected = self._compute_otp(email, window)
            if hmac.compare_digest(expected, otp):
                return True

        return False


otp_service = OTPService()
