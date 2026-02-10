from datetime import datetime, timezone

class PriorityScorer:
    def __init__(self):
        self.priority_keywords = {
            "critical": 50,
            "crash": 40,
            "security": 50,
            "urgent": 30,
            "bug": 20,
            "error": 20,
            "failure": 30
        }

    def calculate_score(self, issue: dict) -> int:
        """
        Calculates priority score based on keywords in title/body and issue age.
        """
        score = 0
        text = (issue.get("title", "") + " " + issue.get("body", "")).lower()

        # Keyword scoring
        for keyword, points in self.priority_keywords.items():
            if keyword in text:
                score += points

        # Age scoring (e.g., +1 point per day open)
        created_at_str = issue.get("created_at")
        if created_at_str:
            try:
                # GitHub timestamp format: 2011-04-10T20:09:31Z
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                age_days = (now - created_at).days
                if age_days > 0:
                    score += age_days  # 1 point per day
            except ValueError:
                pass # logging.warning("Invalid date format")

        return score
