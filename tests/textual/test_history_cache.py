import tempfile
import shutil
import unittest
from history import HistoryCache
import os


class TestHistoryCacheWithTempfile(unittest.TestCase):

    def setUp(self):
        # Creating a temporary directory to store the file
        self.temp_dir = tempfile.mkdtemp()
        self.filepath = os.path.join(self.temp_dir, "history.txt")
        self.history_string = """
# 2023-10-09 20:10:21.878189
+hello

# 2023-10-09 20:15:12.050138
+%help

# 2023-10-09 20:18:24.986704
+```python

# 2023-10-09 20:22:22.322989
+s

# 2023-10-09 20:23:07.192563
+# hello
+

# 2023-10-09 20:52:30.474997
+%exit

# 2023-10-09 22:08:41.254873
+%exit

# 2023-10-09 22:59:30.845552
+skill.show()

# 2023-10-09 23:01:47.807686
+%exit

# 2023-10-10 10:09:06.557410
+%exit
        """
        # Writing the history_string to the file
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(self.history_string)

    def tearDown(self):
        # Removing the temporary directory after the test
        shutil.rmtree(self.temp_dir)

    def test_load_history_strings(self):
        cache = HistoryCache(self.filepath)
        strings = list(cache.load_history_strings())
        expected = ['%exit', '%exit', 'skill.show()', '%exit', '%exit', '# hello\n', 's', '```python', '%help', 'hello']
        self.assertEqual(strings, expected)

    def test_add(self):
        cache = HistoryCache(self.filepath)
        cache.add("query4")
        self.assertEqual(cache.queries["query4"], 1)
        # Verifying the write to the file
        with open(self.filepath, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertTrue("+query4\n" in content)

    def test_get(self):
        cache = HistoryCache(self.filepath)
        self.assertEqual(cache.get("%ex"), second="%exit")
        self.assertIsNone(cache.get("nonexistent"))


# Running the tests with temporary file

unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestHistoryCacheWithTempfile))
