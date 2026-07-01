import hmac, hashlib, os
from urllib.parse import parse_qsl
from fastapi import Header, HTTPException, status

from ..config import bot_token


def get_current_telegram_user(
        authorization: str = Header(None)):
    if not authorization or authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Missing or invalid Auth headers structure')
    
    init_data_raw = authorization.replace('Bearer ', '').strip()
    parsed_data = dict(parse_qsl(init_data_raw))

    if 'hash' not in parsed_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Error Telegram payload: missing hash parameter')
    
    received_hash = parsed_data.pop('hash')
    data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(parsed_data.items()))

    secret_key = hmac.new(b'WebAppData', bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization failed: Data verification mismatch'
        )
    return parsed_data