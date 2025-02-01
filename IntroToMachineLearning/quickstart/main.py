import os
import io

def _set_env(var: str):
    if not os.environ.get(var):
        with open("../secrets/anthropic-key", "r") as anthropic_key:
            os.environ[var] = anthropic_key.read()
        # This is silly and annoying
        # os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("ANTHROPIC_API_KEY")