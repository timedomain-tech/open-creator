from abc import ABC, abstractmethod
import datetime
import re


class BaseMemory(ABC):
    page_size: int = 5

    @abstractmethod
    def __repr__(self) -> str:
        """Returns a string representation of the object."""
        pass

    @abstractmethod
    async def add(self, memory_string, name=None):
        """Adds a new memory string. Optionally, a name can be provided."""
        pass

    @abstractmethod
    async def modify(self, old_content, new_content, name=None):
        """Modifies an existing memory. The old content, new content, and an optional name are required."""
        pass

    @abstractmethod
    async def search(self, query, page, start_date=None, end_date=None):
        """Searches the memory based on a query. Pagination is supported. Optionally, a date range can be provided."""
        pass

    def _paginate_results(self, matches, page):
        """Utility to paginate results."""
        total = len(matches)
        start = self.page_size * page
        end = start + self.page_size
        return matches[start:end], total

    def _validate_date_format(self, date_str):
        """Validate the given date string in the format 'YYYY-MM-DD'."""
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def _extract_date_from_timestamp(self, timestamp):
        """Extracts and returns the date from the given timestamp."""
        match = re.match(r"(\d{4}-\d{2}-\d{2})", timestamp)
        return match.group(1) if match else None

    def _filter_by_date(self, matches, start_date, end_date):
        # First, validate the start_date and end_date format
        if not self._validate_date_format(start_date) or not self._validate_date_format(end_date):
            raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")

        # Convert dates to datetime objects for comparison
        start_date_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        # Next, match items inside self._message_logs
        matches = [
            d for d in matches
            if start_date_dt <= datetime.datetime.strptime(self._extract_date_from_timestamp(d['timestamp']), '%Y-%m-%d') <= end_date_dt
        ]
        return matches
