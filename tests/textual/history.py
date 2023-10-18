import collections
import datetime
import os


class HistoryCache:
    """
    A class used to manage a history cache of queries.
    
    The class keeps track of the frequency of each query and stores/retrieves them 
    from a file, allowing to persist the data between different sessions.

    Attributes:
        filepath (str): The path to the file used to store the history of queries.
        queries (collections.OrderedDict): An ordered dictionary containing the history 
            of queries, where the key is the query and the value is the frequency.
    """
    def __init__(self, filepath):
        """
        Initializes the `HistoryCache` instance.

        Args:
            filepath (str): The path to the file used to store the history of queries.
        """
        self.filepath = filepath
        self.queries = collections.OrderedDict()  # Key: query, Value: frequency
        self._load_history()

    def _load_history(self):
        """
        Loads the historical queries into an ordered dictionary (`self.queries`) from the file.
        """
        for s in self.load_history_strings():
            query = s.strip()
            if query not in self.queries:
                self.queries[query] = 1
            else:
                self.queries[query] += 1

    def add(self, query):
        """
        Adds a new query to the ordered dictionary and stores it in the file.

        Args:
            query (str): The query to be added.
        """
        query = query.strip()
        if query in self.queries:
            self.queries.pop(query)
            self.queries[query] = self.queries.get(query, 0) + 1
        else:
            self.queries[query] = 1
        self.store_string(query)

    def get(self, prefix):
        """
        Retrieves the most recent query matching the provided prefix.

        Args:
            prefix (str): The prefix to match against the queries.

        Returns:
            str: The most recent query that starts with the given prefix, or None if no match is found.
        """
        candidates = [query for query in self.queries.keys() if query.startswith(prefix)]
        if candidates:
            return candidates[0]
        return None

    def load_history_strings(self):
        """
        Loads and returns the history strings from the file.

        Returns:
            list: A list of historical query strings from the file, in reverse order.
        """
        strings = []
        lines = []

        def add():
            if lines:
                s = "".join(lines)[:-1]
                strings.append(s)

        if os.path.exists(self.filepath):
            with open(self.filepath, "rb") as f:
                for line_bytes in f:
                    line = line_bytes.decode("utf-8", errors="replace")

                    if line.startswith("+"):
                        lines.append(line[1:])
                    else:
                        add()
                        lines = []

                add()
        return reversed(strings)

    def store_string(self, s):
        """
        Stores a query string in the file.

        Args:
            s (str): The query string to be stored.
        """
        with open(self.filepath, "ab") as f:
            def write(t):
                f.write(t.encode("utf-8"))

            write("\n# %s\n" % datetime.datetime.now().isoformat())
            for line in s.split("\n"):
                write("+%s\n" % line)

    async def load(self):
        """
        Asynchronously loads and yields the keys (queries) from the ordered dictionary.

        Yields:
            str: The next query from the ordered dictionary.
        """
        for item in self.queries.keys():
            yield item
