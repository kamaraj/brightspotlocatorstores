"""
SQLite Database Integration for Historical Analysis Storage
Stores analysis results, tracks trends, enables reporting
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class AnalysisRecord(Base):
    """Store complete analysis results with metadata"""
    __tablename__ = "analysis_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(500), nullable=False, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    radius = Column(Float, default=3.0)
    persona = Column(String(100), index=True)
    
    # Scores
    overall_score = Column(Float)
    safety_score = Column(Float)
    economic_score = Column(Float)
    education_score = Column(Float)
    healthcare_score = Column(Float)
    
    # Metrics
    data_points_collected = Column(Integer)
    api_calls_made = Column(Integer)
    cache_hit_rate = Column(Float)
    execution_time_seconds = Column(Float)
    
    # Full response data
    response_data = Column(JSON)  # Complete API response
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    version = Column(String(20), default="2.0-optimized")
    status = Column(String(50), default="completed")  # completed, failed, partial
    error_message = Column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius": self.radius,
            "persona": self.persona,
            "scores": {
                "overall": self.overall_score,
                "safety": self.safety_score,
                "economic": self.economic_score,
                "education": self.education_score,
                "healthcare": self.healthcare_score
            },
            "metrics": {
                "data_points": self.data_points_collected,
                "api_calls": self.api_calls_made,
                "cache_hit_rate": self.cache_hit_rate,
                "execution_time": self.execution_time_seconds
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "version": self.version,
            "status": self.status
        }


class LocationTrend(Base):
    """Track location scores over time"""
    __tablename__ = "location_trends"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(500), nullable=False, index=True)
    persona = Column(String(100), index=True)
    score = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Allow tracking specific metrics
    metric_type = Column(String(50), index=True)  # overall, safety, economic, etc.


class Database:
    """Database manager for analysis storage"""
    
    def __init__(self, db_path: str = "childcare_analysis.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        logger.info(f"✅ Database initialized: {db_path}")
    
    def save_analysis(
        self,
        address: str,
        response: Dict[str, Any],
        persona: str = "business",
        execution_time: float = 0.0,
        status: str = "completed",
        error_message: Optional[str] = None
    ) -> int:
        """
        Save analysis result to database
        
        Returns:
            Record ID
        """
        session = self.Session()
        try:
            # Extract scores from response
            scores = response.get("overall_scoring", {})
            
            record = AnalysisRecord(
                address=address,
                latitude=response.get("coordinates", {}).get("latitude"),
                longitude=response.get("coordinates", {}).get("longitude"),
                radius=response.get("search_radius", 3.0),
                persona=persona,
                overall_score=scores.get("overall_score"),
                safety_score=scores.get("safety_score"),
                economic_score=scores.get("economic_viability_score"),
                education_score=scores.get("education_score"),
                healthcare_score=scores.get("healthcare_score"),
                data_points_collected=response.get("data_points_collected", 0),
                api_calls_made=response.get("metrics", {}).get("api_calls", 0),
                cache_hit_rate=response.get("metrics", {}).get("cache_hit_rate", 0.0),
                execution_time_seconds=execution_time,
                response_data=response,
                status=status,
                error_message=error_message
            )
            
            session.add(record)
            session.commit()
            
            record_id = record.id
            logger.info(f"💾 Saved analysis: {address} (ID: {record_id})")
            
            # Also save to trends
            self._save_trends(session, record)
            
            return record_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Database save error: {e}")
            raise
        finally:
            session.close()
    
    def _save_trends(self, session, record: AnalysisRecord):
        """Save trend data for time-series analysis"""
        metrics = [
            ("overall", record.overall_score),
            ("safety", record.safety_score),
            ("economic", record.economic_score),
            ("education", record.education_score),
            ("healthcare", record.healthcare_score)
        ]
        
        for metric_type, score in metrics:
            if score is not None:
                trend = LocationTrend(
                    address=record.address,
                    persona=record.persona,
                    score=score,
                    metric_type=metric_type
                )
                session.add(trend)
        
        session.commit()
    
    def get_analysis_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve analysis by ID"""
        session = self.Session()
        try:
            record = session.query(AnalysisRecord).filter_by(id=record_id).first()
            return record.to_dict() if record else None
        finally:
            session.close()
    
    def get_recent_analyses(
        self,
        limit: int = 10,
        persona: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get most recent analyses"""
        session = self.Session()
        try:
            query = session.query(AnalysisRecord).order_by(
                AnalysisRecord.created_at.desc()
            )
            
            if persona:
                query = query.filter_by(persona=persona)
            
            records = query.limit(limit).all()
            return [r.to_dict() for r in records]
        finally:
            session.close()
    
    def get_location_history(
        self,
        address: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get historical analyses for a specific location"""
        session = self.Session()
        try:
            records = session.query(AnalysisRecord).filter_by(
                address=address
            ).order_by(
                AnalysisRecord.created_at.desc()
            ).limit(limit).all()
            
            return [r.to_dict() for r in records]
        finally:
            session.close()
    
    def get_trends(
        self,
        address: str,
        metric_type: str = "overall",
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get trend data for time-series visualization"""
        from datetime import timedelta
        
        session = self.Session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            trends = session.query(LocationTrend).filter(
                LocationTrend.address == address,
                LocationTrend.metric_type == metric_type,
                LocationTrend.recorded_at >= cutoff_date
            ).order_by(LocationTrend.recorded_at.asc()).all()
            
            return [
                {
                    "date": t.recorded_at.isoformat(),
                    "score": t.score,
                    "metric": t.metric_type
                }
                for t in trends
            ]
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        session = self.Session()
        try:
            total_analyses = session.query(AnalysisRecord).count()
            completed = session.query(AnalysisRecord).filter_by(status="completed").count()
            failed = session.query(AnalysisRecord).filter_by(status="failed").count()
            
            # Average scores
            avg_overall = session.query(
                AnalysisRecord.overall_score
            ).filter(
                AnalysisRecord.overall_score.isnot(None)
            ).all()
            
            avg_score = sum(r[0] for r in avg_overall) / len(avg_overall) if avg_overall else 0
            
            # Unique locations
            unique_locations = session.query(AnalysisRecord.address).distinct().count()
            
            return {
                "total_analyses": total_analyses,
                "completed": completed,
                "failed": failed,
                "success_rate": round(completed / total_analyses * 100, 2) if total_analyses > 0 else 0,
                "unique_locations": unique_locations,
                "average_score": round(avg_score, 2)
            }
        finally:
            session.close()
    
    def delete_old_records(self, days: int = 90) -> int:
        """Delete records older than specified days"""
        from datetime import timedelta
        
        session = self.Session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            count = session.query(AnalysisRecord).filter(
                AnalysisRecord.created_at < cutoff_date
            ).delete()
            
            session.commit()
            logger.info(f"🗑️ Deleted {count} old records (>{days} days)")
            return count
        except Exception as e:
            session.rollback()
            logger.error(f"Delete error: {e}")
            return 0
        finally:
            session.close()


# Global instance
_database: Optional[Database] = None


def get_database(db_path: str = "childcare_analysis.db") -> Database:
    """
    Get or create global database instance
    
    Usage:
        db = get_database()
        record_id = db.save_analysis(address, response)
        history = db.get_location_history(address)
    """
    global _database
    
    if _database is None:
        _database = Database(db_path)
    
    return _database


if __name__ == "__main__":
    # Test database
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Database...")
    db = Database("test_childcare.db")
    
    # Test data
    test_response = {
        "address": "Test Location, MN 55401",
        "coordinates": {"latitude": 44.9778, "longitude": -93.2650},
        "search_radius": 3.0,
        "overall_scoring": {
            "overall_score": 85.5,
            "safety_score": 90.0,
            "economic_viability_score": 80.0,
            "education_score": 88.0,
            "healthcare_score": 83.0
        },
        "data_points_collected": 66,
        "metrics": {
            "api_calls": 10,
            "cache_hit_rate": 0.75
        }
    }
    
    # Save
    record_id = db.save_analysis(
        "Test Location, MN 55401",
        test_response,
        persona="business",
        execution_time=25.5
    )
    print(f"Saved record ID: {record_id}")
    
    # Retrieve
    record = db.get_analysis_by_id(record_id)
    print(f"Retrieved: {json.dumps(record, indent=2)}")
    
    # Stats
    stats = db.get_statistics()
    print(f"Database stats: {json.dumps(stats, indent=2)}")
