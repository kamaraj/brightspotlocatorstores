"""
Setup Script for Enterprise Features
Install required dependencies for Redis, Database, Circuit Breaker
"""

import subprocess
import sys
import os

def install_packages():
    """Install required Python packages"""
    
    packages = [
        "redis>=5.0.0",          # Redis cache client
        "sqlalchemy>=2.0.0",     # Database ORM
        "aiosqlite>=0.19.0",     # Async SQLite support
        "prometheus-client>=0.19.0"  # Metrics (optional)
    ]
    
    print("📦 Installing enterprise dependencies...")
    print("="*80)
    
    for package in packages:
        print(f"\nInstalling {package}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ])
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    print("\n" + "="*80)
    print("✅ All dependencies installed successfully!")
    return True


def setup_redis():
    """Instructions for Redis setup"""
    print("\n" + "="*80)
    print("🔧 Redis Setup Instructions")
    print("="*80)
    
    if os.name == 'nt':  # Windows
        print("""
Windows Redis Setup:

Option 1: Using Docker (Recommended)
    1. Install Docker Desktop from https://www.docker.com/products/docker-desktop
    2. Run: docker run -d -p 6379:6379 redis:latest
    
Option 2: Using Redis for Windows
    1. Download from: https://github.com/microsoftarchive/redis/releases
    2. Run redis-server.exe
    3. Default port: 6379

Option 3: Using WSL (Windows Subsystem for Linux)
    1. Install WSL2
    2. Run: sudo apt-get install redis-server
    3. Run: redis-server
""")
    else:  # Linux/Mac
        print("""
Linux/Mac Redis Setup:

Ubuntu/Debian:
    sudo apt-get update
    sudo apt-get install redis-server
    redis-server

Mac (using Homebrew):
    brew install redis
    redis-server

Docker (all platforms):
    docker run -d -p 6379:6379 redis:latest
""")
    
    print("\nTest Redis connection:")
    print("    redis-cli ping")
    print("    Expected response: PONG")
    print("="*80)


def test_redis_connection():
    """Test if Redis is available"""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, socket_timeout=2)
        client.ping()
        print("\n✅ Redis is running and accessible!")
        return True
    except ImportError:
        print("\n⚠️ redis package not installed. Run install_packages() first.")
        return False
    except Exception as e:
        print(f"\n⚠️ Redis not accessible: {e}")
        print("The system will fall back to in-memory caching.")
        return False


def create_database():
    """Initialize SQLite database"""
    print("\n" + "="*80)
    print("🗄️ Database Setup")
    print("="*80)
    
    try:
        from database import Database
        db = Database("childcare_analysis.db")
        print("✅ Database initialized: childcare_analysis.db")
        
        stats = db.get_statistics()
        print(f"\nDatabase Statistics:")
        print(f"  Total analyses: {stats['total_analyses']}")
        print(f"  Unique locations: {stats['unique_locations']}")
        print("="*80)
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


def verify_installation():
    """Verify all components are working"""
    print("\n" + "="*80)
    print("🔍 Verification")
    print("="*80)
    
    results = {
        "Redis": test_redis_connection(),
        "Database": create_database()
    }
    
    print("\n" + "="*80)
    print("📊 Installation Summary")
    print("="*80)
    
    for component, status in results.items():
        icon = "✅" if status else "⚠️"
        print(f"{icon} {component}: {'Ready' if status else 'Needs attention'}")
    
    print("\n" + "="*80)
    
    if all(results.values()):
        print("🎉 All enterprise features are ready!")
        print("\nStart the server:")
        print("    python production_server_optimized.py")
    else:
        print("⚠️ Some features need configuration")
        print("The server will work with degraded functionality")
        print("\nMissing features will fall back to:")
        print("  - Redis → In-memory caching")
        print("  - Database → No historical storage")
    
    print("="*80)


def main():
    """Run complete setup"""
    print("\n" + "="*80)
    print("🚀 Enterprise Features Setup")
    print("="*80)
    
    # Step 1: Install packages
    if not install_packages():
        print("\n❌ Package installation failed!")
        return
    
    # Step 2: Redis instructions
    setup_redis()
    
    # Step 3: Verify
    verify_installation()


if __name__ == "__main__":
    main()
