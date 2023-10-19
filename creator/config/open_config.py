import os
import appdirs
import subprocess
import platform


def open_user_config():
    # modified from https://github.com/KillianLucas/open-interpreter/blob/be38ef8ed6ce9d0b7768e2ec3f542337f3444f54/interpreter/cli/cli.py#L101
    # MIT license
    config_path = os.path.join(appdirs.user_config_dir(), 'Open-Creator', 'config.yaml')
    config_path = os.path.join(appdirs.user_config_dir(), 'Open-Creator', 'config.yaml')
    print(f"Opening `{config_path}`...")
    # Use the default system editor to open the file
    if platform.system() == 'Windows':
        os.startfile(config_path)  # This will open the file with the default application, e.g., Notepad
    else:
        try:
            # Try using xdg-open on non-Windows platforms
            subprocess.call(['xdg-open', config_path])
        except FileNotFoundError:
            # Fallback to using 'open' on macOS if 'xdg-open' is not available
            subprocess.call(['open', config_path])
