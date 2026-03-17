from datetime import datetime
import pytz
from typing import Optional

class TimeTool:
    @staticmethod
    def get_current_time(timezone: Optional[str] = None) -> str:
        if timezone:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
        else:
            now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")