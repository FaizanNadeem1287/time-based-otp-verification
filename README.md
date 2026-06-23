# OTP Service

A lightweight, stateless One-Time Password (OTP) service using **HMAC-SHA256** and time-based windowing — no database required.

---

## How It Works

Each OTP is derived deterministically from:

- A **shared secret** (`OTP_SECRET`)
- The **user's email** (lowercased)
- The current **time window** (epoch seconds ÷ `OTP_WINDOW_SECONDS`)

This means the server never needs to store generated OTPs. Verification simply recomputes the expected value and compares it in constant time to prevent timing attacks.

A **grace window** (previous time window) is also checked during verification to tolerate clock skew or slight delivery delays.

---

## Configuration

Set the following in your `config.py` (or environment-backed settings):

| Setting | Description | Example |
|---|---|---|
| `OTP_SECRET` | Shared secret used for HMAC signing | `"supersecretkey"` |
| `OTP_LENGTH` | Number of digits in the OTP | `6` |
| `OTP_WINDOW_SECONDS` | Duration (in seconds) each OTP stays valid | `300` (5 min) |

---

## Usage

The module exposes a ready-to-use singleton — no need to instantiate the class yourself.

```python
from otp import otp_service
```

### Generate an OTP

```python
otp = otp_service.generate_otp("user@example.com")
print(otp)  # e.g. "482910"
```

### Verify an OTP

```python
is_valid = otp_service.verify_otp("user@example.com", "482910")

if is_valid:
    print("OTP verified successfully.")
else:
    print("Invalid or expired OTP.")
```

---

## API Reference

### `OTPService`

#### `generate_otp(email: str) -> str`
Generates a numeric OTP for the given email address.

- Lowercases the email before hashing
- Returns a zero-padded string of length `OTP_LENGTH`

#### `verify_otp(email: str, otp: str) -> bool`
Verifies a submitted OTP against the current and previous time windows.

- Uses `hmac.compare_digest` for constant-time comparison (safe against timing attacks)
- Returns `True` if the OTP matches either the current or previous window

#### `_compute_otp(email: str, window: int) -> str` *(internal)*
Core derivation function. Computes HMAC-SHA256 over `"email:window"` and truncates the digest to a fixed-length numeric code.

---

## Security Notes

- **Do not log OTPs** — treat them as short-lived passwords.
- **Rotate `OTP_SECRET`** immediately if it is ever exposed; all in-flight OTPs will be invalidated.
- **Use HTTPS** — OTPs transmitted over plain HTTP are trivially intercepted.
- The two-window grace period means an OTP can remain valid for up to `2 × OTP_WINDOW_SECONDS`. Set the window size accordingly for your security requirements.

---

## File Structure

```
otp.py          # OTPService class + otp_service singleton
config.py       # Settings (OTP_SECRET, OTP_LENGTH, OTP_WINDOW_SECONDS)
```

---

## Requirements

- Python 3.8+
- No external dependencies — uses only the standard library (`hashlib`, `hmac`, `time`)
