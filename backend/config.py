import os
import secrets
from typing import List
from pydantic import BaseModel, Field

class Settings(BaseModel):
    """
    Central production configuration for ElderShield Backend.
    Reads values from environment variables with safe, production-ready defaults.
    """
    app_name: str = "ElderShield Scam Detection API"
    app_version: str = "2.3.0"
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "production"))
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() in ("true", "1"))
    
    # Network & Binding
    host: str = Field(default_factory=lambda: os.getenv("HOST", "127.0.0.1"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    allowed_origins: List[str] = Field(default_factory=lambda: [
        o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()
    ])
    
    # Authentication & Security
    require_auth: bool = Field(default_factory=lambda: os.getenv("REQUIRE_AUTH", "false").lower() in ("true", "1"))
    api_key: str = Field(default_factory=lambda: os.getenv("API_KEY", "eldershield-production-key-hwv4"))
    rate_limit_per_minute: int = Field(default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_MINUTE", "120")))
    
    # Audio & Model Configurations
    max_audio_upload_mb: int = Field(default_factory=lambda: int(os.getenv("MAX_AUDIO_UPLOAD_MB", "25")))
    whisper_model_size: str = Field(default_factory=lambda: os.getenv("WHISPER_MODEL_SIZE", "tiny"))
    whisper_device: str = Field(default_factory=lambda: os.getenv("WHISPER_DEVICE", "cpu"))
    whisper_compute_type: str = Field(default_factory=lambda: os.getenv("WHISPER_COMPUTE_TYPE", "int8"))
    
    # Session Management & Concurrency
    session_idle_timeout_seconds: int = Field(default_factory=lambda: int(os.getenv("SESSION_IDLE_TIMEOUT_SECONDS", "1800")))
    max_buffer_bytes_per_session: int = Field(default_factory=lambda: int(os.getenv("MAX_BUFFER_BYTES_PER_SESSION", str(10 * 1024 * 1024))))
    max_concurrent_sessions: int = Field(default_factory=lambda: int(os.getenv("MAX_CONCURRENT_SESSIONS", "50")))
    
    # Logging & Privacy
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    enable_json_logging: bool = Field(default_factory=lambda: os.getenv("ENABLE_JSON_LOGGING", "false").lower() in ("true", "1"))
    mask_log_pii: bool = Field(default_factory=lambda: os.getenv("MASK_LOG_PII", "true").lower() in ("true", "1"))
    data_retention_policy: str = "EPHEMERAL_ZERO_DISK_RETENTION"

settings = Settings()
