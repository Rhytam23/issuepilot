from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Optional
from src.config import Config
from src.models import Base, Issue

class Storage:
    def __init__(self):
        # Use sqlite:///issue_pilot.db for default
        db_path = Config.STORAGE_FILE.replace(".json", ".db") if Config.STORAGE_FILE.endswith(".json") else "issue_pilot.db"
        self.engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()

    def get_session(self) -> Session:
        return self.SessionLocal()

    def load_data(self) -> List[Dict]:
        """
        Returns all issues as dictionaries.
        """
        session = self.get_session()
        try:
            issues = session.query(Issue).all()
            return [issue.to_dict() for issue in issues]
        finally:
            session.close()

    def create_tables(self):
        """Creates the issues table if it doesn't exist."""
        # Check if repository column exists, if not add it (simple migration)
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT repository FROM issues LIMIT 1"))
        except Exception:
            # Column likely missing, add it
            try:
                with self.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE issues ADD COLUMN repository TEXT"))
                    conn.commit()
            except Exception as e:
                # Table might not exist yet, which is fine
                pass

        Base.metadata.create_all(bind=self.engine)

    def save_issue_result(self, issue_id, result_data):
        """Saves or updates the analysis result in the database."""
        session = self.get_session()
        try:
            issue = session.query(Issue).filter(Issue.id == str(issue_id)).first()
            if not issue:
                issue = Issue(id=str(issue_id))
                session.add(issue)
            
            # Update fields
            issue.number = result_data.get("number")
            issue.title = result_data.get("title")
            issue.body = result_data.get("body")
            issue.state = result_data.get("state")
            issue.created_at = result_data.get("created_at")
            issue.html_url = result_data.get("html_url")
            issue.status = result_data.get("status", "new")
            issue.predicted_label = result_data.get("predicted_label")
            issue.priority_score = result_data.get("priority_score", 0)
            issue.repository = result_data.get("repository") # New field
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def bulk_save(self, issues_data: List[Dict]):
        """
        Saves multiple issues at once.
        """
        session = self.get_session()
        try:
            for data in issues_data:
                issue = session.query(Issue).filter(Issue.id == data["id"]).first()
                if not issue:
                    issue = Issue(id=data["id"])
                    session.add(issue)
                
                # Update fields
                if "number" in data: issue.number = data.get("number")
                if "title" in data: issue.title = data.get("title")
                if "body" in data: issue.body = data.get("body")
                if "state" in data: issue.state = data.get("state")
                if "created_at" in data: issue.created_at = data.get("created_at")
                if "html_url" in data: issue.html_url = data.get("html_url")
                
                # Only update status if it's new, or forcing update
                if not issue.status:
                     issue.status = "new"
                
                # If triage data is present in input, update it
                if "predicted_label" in data:
                    issue.predicted_label = data["predicted_label"]
                if "priority_score" in data:
                    issue.priority_score = data["priority_score"]
                if "status" in data:
                    issue.status = data["status"]

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
