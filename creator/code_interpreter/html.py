
import os
import tempfile
import webbrowser


class HTMLInterpreter:
    
    def run(self, query:str) -> dict:
        # Create a temporary HTML file with the content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
            f.write(query.encode())

        # Open the HTML file with the default web browser
        webbrowser.open('file://' + os.path.realpath(f.name))
        message = f"Saved to {os.path.realpath(f.name)} and opened with the user's default web browser."
        return {"status": "success", "stdout": message, "stderr": ""}


if __name__ == "__main__":
    inter = HTMLInterpreter()
    res = inter.run('<h1>Hello, World!</h1>')
    print(res)
