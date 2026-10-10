"""Save an API key locally without displaying it or placing it in shell history."""
import getpass
import os
from pathlib import Path
from dotenv import set_key


def main():
    path = Path(__file__).resolve().parents[1] / '.env'
    key = getpass.getpass('Paste your OpenAI API key (hidden), then press Enter: ').strip()
    if not key or any(c.isspace() for c in key):
        raise SystemExit('No valid key entered; nothing saved.')
    if path.is_symlink():
        raise SystemExit('Refusing to write through a .env symlink.')
    fd = os.open(path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
    os.close(fd)
    path.chmod(0o600)
    set_key(str(path), 'OPENAI_API_KEY', key)
    path.chmod(0o600)
    print('Key saved to the private, Git-ignored .env file. The key was not displayed.')


if __name__ == '__main__':
    main()
