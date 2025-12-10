"""
Run the application
Quick start script for development and production
"""

import uvicorn
import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from app.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    print(f"""
    ╔════════════════════════════════════════════════════════════════╗
    ║  Childcare Location Intelligence System                       ║
    ║  Version: {settings.app_version}                                         ║
    ║  Environment: {settings.environment}                                   ║
    ╚════════════════════════════════════════════════════════════════╝
    
    Starting server...
    - Host: {settings.host}:{settings.port}
    - Docs: http://localhost:{settings.port}/api/docs
    - Health: http://localhost:{settings.port}/health
    
    Press Ctrl+C to stop
    """)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload or settings.auto_reload,
        log_level=settings.log_level.lower(),
        workers=1 if (settings.reload or settings.auto_reload) else settings.workers,
        access_log=True
    )
