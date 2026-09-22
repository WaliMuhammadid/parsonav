"""
Rate Limiter Service for Presenova API
Provides sliding-window rate limiting per IP or JWT Identity.
Support tier-based limits for Guest vs Authenticated users.
"""

import time
import os
import logging
import threading
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity

logger = logging.getLogger(__name__)

# Distributed Redis client (optional, initialized on demand if REDIS_URL is present)
_REDIS_CLIENT = None
_REDIS_INITIALIZED = False
_redis_lock = threading.Lock()


def _get_redis_client():
    global _REDIS_CLIENT, _REDIS_INITIALIZED
    with _redis_lock:
        if not _REDIS_INITIALIZED:
            _REDIS_INITIALIZED = True
            redis_url = os.getenv('REDIS_URL', '').strip()
            if redis_url:
                try:
                    import redis
                    _REDIS_CLIENT = redis.from_url(redis_url, decode_responses=True, socket_timeout=2.0)
                    _REDIS_CLIENT.ping()
                    logger.info("[RATE-LIMIT] Connected to Redis for distributed rate limiting.")
                except Exception as e:
                    logger.warning("[RATE-LIMIT] Redis connection failed (%s); using in-memory store fallback.", e)
                    _REDIS_CLIENT = None
        return _REDIS_CLIENT


# In-memory storage for sliding window timestamps (fallback)
# Structure: { key: [timestamp1, timestamp2, ...] }
_request_records = {}
_lock = threading.Lock()


def rate_limit(limit_authenticated: int = 15, limit_guest: int = 3, window_seconds: int = 60):
    """
    Decorator for Flask routes enforcing rate limits.
    Supports distributed Redis sliding window when REDIS_URL is set,
    with automatic thread-safe in-memory fallback.
    
    Args:
        limit_authenticated: Max requests per window for logged-in JWT users.
        limit_guest: Max requests per window for unauthenticated / guest users.
        window_seconds: Sliding window duration in seconds (default: 60s).
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Bypass rate limiting in testing mode
            try:
                if (current_app and current_app.config.get('TESTING')) or os.getenv('TESTING') == '1' or os.getenv('FLASK_ENV') == 'testing':
                    return f(*args, **kwargs)
            except Exception:
                pass

            try:
                user_id = get_jwt_identity()
            except Exception:
                user_id = None

            is_guest = not user_id or user_id == "guest"
            
            # Determine rate limit key & threshold
            client_ip = request.remote_addr or "127.0.0.1"
            key = f"usr:{user_id}" if not is_guest else f"ip:{client_ip}"
            max_allowed = limit_guest if is_guest else limit_authenticated
            
            now = time.time()
            cutoff = now - window_seconds
            
            # ── Option A: Distributed Redis sliding-window ──────────────────
            r_client = _get_redis_client()
            if r_client is not None:
                try:
                    redis_key = f"presenova:rl:{key}"
                    pipe = r_client.pipeline()
                    pipe.zremrangebyscore(redis_key, 0, cutoff)
                    pipe.zcard(redis_key)
                    pipe.zadd(redis_key, {str(now): now})
                    pipe.expire(redis_key, window_seconds + 5)
                    results = pipe.execute()
                    current_count = results[1]

                    if current_count >= max_allowed:
                        return jsonify({
                            "success": False,
                            "error": "TooManyRequests",
                            "message": f"Rate limit exceeded ({max_allowed} requests per {window_seconds}s). Please try again later.",
                            "is_guest": is_guest,
                            "retry_after_seconds": window_seconds
                        }), 429

                    return f(*args, **kwargs)
                except Exception as r_err:
                    logger.warning("[RATE-LIMIT] Redis check error (%s); falling back to in-memory store.", r_err)

            # ── Option B: Thread-safe in-memory sliding-window fallback ──────
            with _lock:
                # Periodic memory cleanup if table grows large
                if len(_request_records) > 2000:
                    expired_keys = [k for k, v in _request_records.items() if not v or v[-1] < cutoff]
                    for k in expired_keys:
                        del _request_records[k]

                timestamps = _request_records.get(key, [])
                # Filter out expired timestamps outside current window
                valid_timestamps = [t for t in timestamps if t > cutoff]
                
                if len(valid_timestamps) >= max_allowed:
                    retry_after = int(window_seconds - (now - valid_timestamps[0]))
                    return jsonify({
                        "success": False,
                        "error": "TooManyRequests",
                        "message": f"Rate limit exceeded ({max_allowed} requests per {window_seconds}s). Please try again in {retry_after} seconds.",
                        "is_guest": is_guest,
                        "retry_after_seconds": max(1, retry_after)
                    }), 429
                
                valid_timestamps.append(now)
                _request_records[key] = valid_timestamps
                
            return f(*args, **kwargs)
        return wrapped
    return decorator


def enforce_guest_size_limit(max_guest_bytes: int = 10 * 1024 * 1024):
    """
    Helper function checking if a guest upload exceeds guest size cap.
    
    Args:
        max_guest_bytes: Cap for unauthenticated guest trial uploads (default: 10 MB).
    """
    try:
        user_id = get_jwt_identity()
    except Exception:
        user_id = None

    is_guest = not user_id or user_id == "guest"
    
    if is_guest and request.content_length and request.content_length > max_guest_bytes:
        mb = max_guest_bytes // (1024 * 1024)
        return jsonify({
            "success": False,
            "error": "GuestFileSizeLimitExceeded",
            "message": f"Guest trial uploads are limited to {mb} MB. Please sign up or log in for larger uploads (up to 50 MB)."
        }), 413
    return None

