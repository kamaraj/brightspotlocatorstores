"""
Configuration Management for Childcare Location Intelligence Application
Uses Pydantic Settings for type-safe configuration with environment variable support
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main application settings with validation"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ============================================
    # Application Settings
    # ============================================
    app_name: str = Field(default="Tile & Flooring Optimizer AI")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=4)
    reload: bool = Field(default=False)
    
    # ============================================
    # AI & LLM Configuration
    # ============================================
    # GitHub Models (Primary)
    github_token: str = Field(default="")
    github_models_base_url: str = Field(
        default="https://models.github.ai/inference"
    )
    github_model_id: str = Field(default="gpt-4.1-mini")
    
    # Azure OpenAI (Alternative)
    azure_openai_api_key: Optional[str] = Field(default=None)
    azure_openai_endpoint: Optional[str] = Field(default=None)
    azure_openai_deployment: Optional[str] = Field(default=None)
    azure_openai_api_version: str = Field(default="2024-08-01-preview")
    
    # OpenAI Direct (Alternative)
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")
    
    # Agent Configuration
    max_agent_iterations: int = Field(default=10)
    agent_timeout_seconds: int = Field(default=120)
    enable_agent_streaming: bool = Field(default=True)
    
    # ============================================
    # Database Configuration
    # ============================================
    mysql_host: str = Field(default="localhost")
    mysql_port: int = Field(default=3306)
    mysql_user: str = Field(default="childcare_app")
    mysql_password: str = Field(default="")
    mysql_database: str = Field(default="childcare_location_db")
    
    # Connection Pool
    db_pool_size: int = Field(default=20)
    db_max_overflow: int = Field(default=10)
    db_pool_recycle: int = Field(default=3600)
    
    @property
    def database_url(self) -> str:
        """Construct MySQL database URL"""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )
    
    # ============================================
    # Redis Configuration
    # ============================================
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_password: str = Field(default="")
    redis_db: int = Field(default=0)
    
    # Cache Settings
    cache_ttl_seconds: int = Field(default=3600)
    cache_enabled: bool = Field(default=True)
    
    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # ============================================
    # ChromaDB Configuration
    # ============================================
    chroma_host: str = Field(default="localhost")
    chroma_port: int = Field(default=8001)
    chroma_collection_name: str = Field(default="location_embeddings")
    chroma_persist_directory: str = Field(default="./data/chromadb")
    
    # Embedding Model
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    
    # ============================================
    # External API Keys
    # ============================================
    google_maps_api_key: str = Field(default="")
    google_places_api_key: Optional[str] = Field(default=None)
    google_distance_matrix_api_key: Optional[str] = Field(default=None)
    
    census_api_key: str = Field(default="")
    
    # FBI Crime Data Explorer
    fbi_crime_api_key: Optional[str] = Field(default=None)
    fbi_crime_api_base_url: str = Field(default="https://api.usa.gov/crime/fbi/cde")
    
    # EPA Envirofacts (no key needed)
    epa_api_base_url: str = Field(default="https://data.epa.gov/efservice")
    
    # HUD User API
    hud_api_key: Optional[str] = Field(default=None)
    hud_api_base_url: str = Field(default="https://www.huduser.gov/hudapi/public")
    
    # FEMA Flood Maps (no key needed)
    fema_api_base_url: str = Field(default="https://hazards.fema.gov/gis/nfhl/rest/services")
    
    # Legacy fields (deprecated, kept for compatibility)
    crime_api_key: Optional[str] = Field(default=None)
    crime_api_base_url: Optional[str] = Field(default=None)
    epa_api_key: Optional[str] = Field(default=None)
    real_estate_api_key: Optional[str] = Field(default=None)
    real_estate_api_base_url: Optional[str] = Field(default=None)
    
    @property
    def places_api_key(self) -> str:
        """Get Google Places API key (fallback to Maps key)"""
        return self.google_places_api_key or self.google_maps_api_key
    
    @property
    def distance_matrix_api_key(self) -> str:
        """Get Distance Matrix API key (fallback to Maps key)"""
        return self.google_distance_matrix_api_key or self.google_maps_api_key
    
    # ============================================
    # Security & Authentication
    # ============================================
    secret_key: str = Field(
        default="change_this_to_a_secure_secret_key_in_production"
    )
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    
    # CORS
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8000")
    cors_allow_credentials: bool = Field(default=True)
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=30)
    rate_limit_per_hour: int = Field(default=500)
    
    # PII Detection
    enable_pii_detection: bool = Field(default=True)
    pii_anonymize: bool = Field(default=True)
    
    # ============================================
    # Pricing & Billing
    # ============================================
    free_tier_analyses_per_week: int = Field(default=1)
    paid_tier_price: int = Field(default=29)
    pro_tier_price: int = Field(default=99)
    premium_tier_price: int = Field(default=299)
    
    # ============================================
    # Monitoring & Observability
    # ============================================
    prometheus_enabled: bool = Field(default=True)
    prometheus_port: int = Field(default=9090)
    
    grafana_enabled: bool = Field(default=True)
    grafana_port: int = Field(default=3000)
    
    loki_enabled: bool = Field(default=True)
    loki_url: str = Field(default="http://localhost:3100")
    
    otel_enabled: bool = Field(default=False)
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")
    otel_service_name: str = Field(default="childcare-location-intelligence")
    
    sentry_dsn: Optional[str] = Field(default=None)
    sentry_environment: Optional[str] = Field(default=None)
    
    # ============================================
    # Performance & Limits
    # ============================================
    analysis_timeout_seconds: int = Field(default=90)
    max_concurrent_analyses: int = Field(default=20)
    
    data_collection_timeout_seconds: int = Field(default=30)
    max_retry_attempts: int = Field(default=3)
    retry_backoff_seconds: int = Field(default=2)
    
    max_upload_size_mb: int = Field(default=10)
    allowed_file_extensions: str = Field(default=".csv,.xlsx,.json")
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse allowed extensions string to list"""
        return [ext.strip() for ext in self.allowed_file_extensions.split(",")]
    
    # ============================================
    # Feature Flags
    # ============================================
    enable_discovery_mode: bool = Field(default=True)
    enable_comparison_mode: bool = Field(default=True)
    enable_batch_analysis: bool = Field(default=False)
    enable_export_pdf: bool = Field(default=True)
    enable_export_json: bool = Field(default=True)
    enable_historical_tracking: bool = Field(default=True)
    
    # ============================================
    # Development & Testing
    # ============================================
    test_database_url: str = Field(default="sqlite:///./test.db")
    mock_external_apis: bool = Field(default=False)
    auto_reload: bool = Field(default=False)
    show_sql_queries: bool = Field(default=False)
    
    # ============================================
    # Deployment
    # ============================================
    compose_project_name: str = Field(default="childcare-location-intelligence")
    
    ssl_cert_path: Optional[str] = Field(default=None)
    ssl_key_path: Optional[str] = Field(default=None)
    force_https: bool = Field(default=False)
    
    backup_enabled: bool = Field(default=True)
    backup_schedule: str = Field(default="0 2 * * *")
    backup_retention_days: int = Field(default=30)
    
    # ============================================
    # Validators
    # ============================================
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Ensure environment is valid"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v_upper
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is secure enough"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if v == "change_this_to_a_secure_secret_key_in_production":
            # Only raise in non-dev environments
            import os
            if os.getenv("ENVIRONMENT", "development") != "development":
                raise ValueError("Must change SECRET_KEY in production!")
        return v
    
    # ============================================
    # Helper Methods
    # ============================================
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"
    
    def get_llm_config(self) -> dict:
        """Get LLM configuration based on priority"""
        # Priority: GitHub Models > Azure OpenAI > OpenAI Direct
        if self.github_token:
            return {
                "provider": "github",
                "base_url": self.github_models_base_url,
                "api_key": self.github_token,
                "model": self.github_model_id,
            }
        elif self.azure_openai_api_key:
            return {
                "provider": "azure",
                "endpoint": self.azure_openai_endpoint,
                "api_key": self.azure_openai_api_key,
                "deployment": self.azure_openai_deployment,
                "api_version": self.azure_openai_api_version,
            }
        elif self.openai_api_key:
            return {
                "provider": "openai",
                "api_key": self.openai_api_key,
                "model": self.openai_model,
            }
        else:
            raise ValueError("No LLM API key configured! Set GITHUB_TOKEN, AZURE_OPENAI_API_KEY, or OPENAI_API_KEY")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Use this function throughout the application to access settings
    
    Example:
        from app.config import get_settings
        settings = get_settings()
        print(settings.database_url)
    """
    return Settings()


# Convenience instance for imports
settings = get_settings()
