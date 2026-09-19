import os

# Provide test defaults before any app module reads settings
os.environ.setdefault("JWT_SECRET", "test-secret-not-for-production")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
