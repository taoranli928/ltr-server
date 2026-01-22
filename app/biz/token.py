import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any

SECRET_KEY = "mock_secret_key_1234567890_!@#$%^&*()"
ALGORITHM = "HS256"


def generate_jwt_token(
        custom_payload: Dict[str, Any],
        expire_minutes: int = 30,
) -> str:
    payload = custom_payload.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })

    return jwt.encode(
        payload=payload,
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_jwt_token(
        token: str,
) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            jwt=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "verify_exp": True,
                "require_exp": True
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidSignatureError:
        return None
    except jwt.MissingRequiredClaimError as e:
        return None
    except jwt.DecodeError:
        return None
    except Exception as e:
        return None
