from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True) # This will be the GitHub Issue ID
    number = Column(Integer, unique=True, index=True)
    title = Column(String, index=True)
    body = Column(String, nullable=True)
    state = Column(String)
    created_at = Column(String) # Storing as string for simplicity, or could use DateTime
    html_url = Column(String)
    
    # Triage fields
    status = Column(String, default="new") # new, triaged
    predicted_label = Column(String, nullable=True)
    priority_score = Column(Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "title": self.title,
            "body": self.body,
            "state": self.state,
            "created_at": self.created_at,
            "html_url": self.html_url,
            "status": self.status,
            "predicted_label": self.predicted_label,
            "priority_score": self.priority_score,
        }
