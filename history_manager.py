"""
history_manager.py
Manage job analysis history and auto-save/recovery functionality.

Features:
  - Auto-save current form data every 30 seconds
  - Recover last session on app restart
  - Keep history of last 20 analyzed jobs
  - Quick-load previous jobs from history
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional


class HistoryManager:
    """Manage job history and auto-save functionality."""
    
    def __init__(self, history_file: Optional[Path] = None, draft_file: Optional[Path] = None):
        """
        Initialize history manager.
        
        Args:
            history_file: Path to store job history (default: .history.json)
            draft_file: Path to store current draft (default: .draft.json)
        """
        if history_file is None:
            history_file = Path(__file__).parent / ".history.json"
        if draft_file is None:
            draft_file = Path(__file__).parent / ".draft.json"
            
        self.history_file = history_file
        self.draft_file = draft_file
        self.max_history = 20
        
        # Ensure files exist
        if not self.history_file.exists():
            self.history_file.write_text(json.dumps({"jobs": []}, indent=2))
        if not self.draft_file.exists():
            self.draft_file.write_text(json.dumps({}, indent=2))
    
    def save_draft(self, job_title: str, company: str, role: str, job_circular: str) -> None:
        """Auto-save current form data as draft."""
        try:
            draft = {
                "job_title": job_title,
                "company": company,
                "role": role,
                "job_circular": job_circular,
                "saved_at": datetime.now().isoformat()
            }
            self.draft_file.write_text(json.dumps(draft, indent=2))
        except Exception as exc:
            print(f"Warning: Could not save draft: {exc}")
    
    def load_draft(self) -> dict:
        """Load last saved draft data."""
        try:
            if self.draft_file.exists():
                content = self.draft_file.read_text()
                if content.strip():
                    return json.loads(content)
        except Exception as exc:
            print(f"Warning: Could not load draft: {exc}")
        
        return {
            "job_title": "",
            "company": "",
            "role": "",
            "job_circular": ""
        }
    
    def clear_draft(self) -> None:
        """Clear draft data after successful generation."""
        try:
            self.draft_file.write_text(json.dumps({}, indent=2))
        except Exception as exc:
            print(f"Warning: Could not clear draft: {exc}")
    
    def add_to_history(self, job_title: str, company: str, role: str, job_circular: str) -> None:
        """Add analyzed job to history."""
        try:
            data = self._load_history()
            
            job_entry = {
                "job_title": job_title,
                "company": company,
                "role": role,
                "job_circular": job_circular,
                "created_at": datetime.now().isoformat()
            }
            
            # Add to beginning (newest first)
            data["jobs"].insert(0, job_entry)
            
            # Keep only last 20
            data["jobs"] = data["jobs"][:self.max_history]
            
            self.history_file.write_text(json.dumps(data, indent=2))
        except Exception as exc:
            print(f"Warning: Could not save to history: {exc}")
    
    def get_history(self) -> list[dict]:
        """Get all job history entries."""
        try:
            data = self._load_history()
            return data.get("jobs", [])
        except Exception as exc:
            print(f"Warning: Could not load history: {exc}")
            return []
    
    def get_history_summary(self) -> list[str]:
        """Get readable history summaries (for UI dropdown)."""
        history = self.get_history()
        summaries = []
        
        for i, job in enumerate(history[:10], 1):
            company = job.get("company", "Unknown")
            role = job.get("role", "Unknown")
            date = job.get("created_at", "")
            
            # Format: "1. TechCorp - Backend Developer (2h ago)"
            if date:
                dt = datetime.fromisoformat(date)
                ago = self._time_ago(dt)
                summary = f"{i}. {company} - {role} ({ago})"
            else:
                summary = f"{i}. {company} - {role}"
            
            summaries.append(summary)
        
        return summaries
    
    def load_from_history(self, index: int) -> dict:
        """Load specific job from history by index."""
        history = self.get_history()
        
        if 0 <= index < len(history):
            job = history[index]
            return {
                "job_title": job.get("job_title", ""),
                "company": job.get("company", ""),
                "role": job.get("role", ""),
                "job_circular": job.get("job_circular", "")
            }
        
        return {}
    
    def clear_history(self) -> None:
        """Clear all history (for reset/cleanup)."""
        try:
            self.history_file.write_text(json.dumps({"jobs": []}, indent=2))
        except Exception as exc:
            print(f"Warning: Could not clear history: {exc}")
    
    def _load_history(self) -> dict:
        """Internal: Load history file."""
        if self.history_file.exists():
            content = self.history_file.read_text()
            if content.strip():
                return json.loads(content)
        
        return {"jobs": []}
    
    @staticmethod
    def _time_ago(dt: datetime) -> str:
        """Convert datetime to relative time string."""
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "now"
        elif seconds < 3600:
            mins = int(seconds / 60)
            return f"{mins}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        else:
            days = int(seconds / 86400)
            return f"{days}d ago"
