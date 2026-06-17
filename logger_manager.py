"""
logger_manager.py
Manage application logging to file for debugging and auditing.

Logs are stored in app_logs/ folder with timestamped files.
Each log entry includes timestamp, level (INFO/ERROR/WARNING), and message.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class LoggerManager:
    """Manage application logging to file."""
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize logger manager.
        
        Args:
            log_dir: Directory to store logs (default: app_logs/)
        """
        if log_dir is None:
            log_dir = Path(__file__).parent / "app_logs"
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Current log file (changes daily)
        self.current_log_file = self._get_log_file()
    
    def info(self, message: str) -> None:
        """Log info message."""
        self._write_log("INFO", message)
    
    def error(self, message: str, exc_info: Optional[str] = None) -> None:
        """Log error message with optional exception info."""
        if exc_info:
            message = f"{message}\n  Exception: {exc_info}"
        self._write_log("ERROR", message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self._write_log("WARNING", message)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self._write_log("DEBUG", message)
    
    def log_analysis(self, company: str, role: str, provider: str, success: bool) -> None:
        """Log job analysis operation."""
        status = "✓ SUCCESS" if success else "✗ FAILED"
        msg = f"Analyzed job | Company: {company} | Role: {role} | Provider: {provider} | {status}"
        self.info(msg)
    
    def log_generation(self, company: str, role: str, num_files: int, success: bool) -> None:
        """Log PDF generation operation."""
        status = "✓ SUCCESS" if success else "✗ FAILED"
        msg = f"Generated PDFs | Company: {company} | Role: {role} | Files: {num_files} | {status}"
        self.info(msg)
    
    def log_setting_change(self, setting: str, old_value: str, new_value: str) -> None:
        """Log settings change."""
        msg = f"Setting changed | {setting}: '{old_value}' → '{new_value}'"
        self.info(msg)
    
    def get_recent_logs(self, lines: int = 50) -> list[str]:
        """Get last N lines from current log file."""
        try:
            log_file = self.current_log_file
            if log_file.exists():
                content = log_file.read_text()
                return content.strip().split("\n")[-lines:]
        except Exception as exc:
            return [f"Error reading logs: {exc}"]
        
        return []
    
    def _write_log(self, level: str, message: str) -> None:
        """Write log entry to file."""
        try:
            # Check if we need to rotate log file (daily)
            self.current_log_file = self._get_log_file()
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {level:8} | {message}\n"
            
            with open(self.current_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as exc:
            # Silently fail on log write errors to not crash app
            pass
    
    def _get_log_file(self) -> Path:
        """Get today's log file path."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"app_{date_str}.log"
    
    def cleanup_old_logs(self, days: int = 30) -> None:
        """Delete log files older than N days."""
        try:
            cutoff = datetime.now().timestamp() - (days * 86400)
            
            for log_file in self.log_dir.glob("app_*.log"):
                if log_file.stat().st_mtime < cutoff:
                    log_file.unlink()
                    self.debug(f"Deleted old log: {log_file.name}")
        except Exception as exc:
            print(f"Warning: Could not cleanup old logs: {exc}")
