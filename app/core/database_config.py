"""
Modular Database Configuration for Brahma Vastu Backend
Supports multiple environments: development, staging, production
"""

import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

class DatabaseConfig:
    """Modular database configuration class"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.config = self._get_config()
    
    def _get_config(self) -> dict:
        """Get database configuration based on environment"""
        
        # Development configuration (local Docker MySQL)
        if self.environment == "development":
            return {
                "DATABASE_URL": os.getenv(
                    "DATABASE_URL", 
                    "mysql+pymysql://bvuser:bv_password@mysql:3306/brahmavastu"
                ),
                "POOL_SIZE": int(os.getenv("DB_POOL_SIZE", "5")),
                "MAX_OVERFLOW": int(os.getenv("DB_MAX_OVERFLOW", "10")),
                "POOL_TIMEOUT": int(os.getenv("DB_POOL_TIMEOUT", "30")),
                "POOL_RECYCLE": int(os.getenv("DB_POOL_RECYCLE", "3600")),
                "ECHO": True,  # Log SQL queries in development
            }
        
        # Staging configuration
        elif self.environment == "staging":
            return {
                "DATABASE_URL": os.getenv(
                    "DATABASE_URL",
                    "mysql+pymysql://bvuser:staging_password@staging-db-host/brahmavastu_staging"
                ),
                "POOL_SIZE": 10,
                "MAX_OVERFLOW": 20,
                "POOL_TIMEOUT": 30,
                "POOL_RECYCLE": 3600,
                "ECHO": False,
            }
        
        # Production configuration
        elif self.environment == "production":
            return {
                "DATABASE_URL": os.getenv(
                    "DATABASE_URL",
                    "mysql+pymysql://bvuser:production_password@prod-db-host/brahmavastu_prod"
                ),
                "POOL_SIZE": 20,
                "MAX_OVERFLOW": 30,
                "POOL_TIMEOUT": 30,
                "POOL_RECYCLE": 3600,
                "ECHO": False,
            }
        
        # AWS RDS configuration (commented out - uncomment when using AWS RDS)
        elif self.environment == "aws_rds":
            return {
                "DATABASE_URL": os.getenv(
                    "DATABASE_URL",
                    "mysql+pymysql://admin:rds_password@your-rds-endpoint.region.rds.amazonaws.com:3306/brahmavastu"
                ),
                "POOL_SIZE": 15,
                "MAX_OVERFLOW": 25,
                "POOL_TIMEOUT": 30,
                "POOL_RECYCLE": 3600,
                "ECHO": False,
            }
        
        # AWS RDS with SSL (commented out - uncomment when using AWS RDS with SSL)
        elif self.environment == "aws_rds_ssl":
            return {
                "DATABASE_URL": os.getenv(
                    "DATABASE_URL",
                    "mysql+pymysql://admin:rds_password@your-rds-endpoint.region.rds.amazonaws.com:3306/brahmavastu?ssl_ca=rds-ca-2019-root.pem"
                ),
                "POOL_SIZE": 15,
                "MAX_OVERFLOW": 25,
                "POOL_TIMEOUT": 30,
                "POOL_RECYCLE": 3600,
                "ECHO": False,
            }
        
        else:
            raise ValueError(f"Unknown environment: {self.environment}")
    
    def get_engine(self):
        """Create and return SQLAlchemy engine with appropriate configuration"""
        
        # Parse connection parameters
        database_url = self.config["DATABASE_URL"]
        
        # Engine configuration
        engine_kwargs = {
            "poolclass": QueuePool,
            "pool_size": self.config["POOL_SIZE"],
            "max_overflow": self.config["MAX_OVERFLOW"],
            "pool_timeout": self.config["POOL_TIMEOUT"],
            "pool_recycle": self.config["POOL_RECYCLE"],
            "echo": self.config["ECHO"],
        }
        
        # Add SSL configuration for AWS RDS if needed
        if self.environment in ["aws_rds", "aws_rds_ssl"]:
            engine_kwargs.update({
                "connect_args": {
                    "ssl_disabled": False,
                    "ssl_verify_cert": True,
                    "ssl_verify_identity": True,
                }
            })
        
        return create_engine(database_url, **engine_kwargs)
    
    def get_session_factory(self):
        """Create and return session factory"""
        engine = self.get_engine()
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def get_connection_string(self) -> str:
        """Get the database connection string"""
        return self.config["DATABASE_URL"]
    
    def get_pool_info(self) -> dict:
        """Get connection pool information"""
        return {
            "pool_size": self.config["POOL_SIZE"],
            "max_overflow": self.config["MAX_OVERFLOW"],
            "pool_timeout": self.config["POOL_TIMEOUT"],
            "pool_recycle": self.config["POOL_RECYCLE"],
        }


# Environment-specific database configurations
# Uncomment and modify as needed for your deployment

# Development database (local MySQL)
DEVELOPMENT_DB = DatabaseConfig("development")

# Staging database (staging server)
# STAGING_DB = DatabaseConfig("staging")

# Production database (production server)
# PRODUCTION_DB = DatabaseConfig("production")

# AWS RDS database (uncomment when using AWS RDS)
# AWS_RDS_DB = DatabaseConfig("aws_rds")

# AWS RDS with SSL (uncomment when using AWS RDS with SSL)
# AWS_RDS_SSL_DB = DatabaseConfig("aws_rds_ssl")


def get_database_config(environment: Optional[str] = None) -> DatabaseConfig:
    """
    Get database configuration based on environment
    
    Args:
        environment: Environment name (development, staging, production, aws_rds, aws_rds_ssl)
    
    Returns:
        DatabaseConfig instance
    """
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    return DatabaseConfig(environment)


# Example usage:
# db_config = get_database_config("production")
# engine = db_config.get_engine()
# SessionLocal = db_config.get_session_factory()
