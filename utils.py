import hmac
import hashlib
import subprocess
from jinja2 import Environment, FileSystemLoader


def verify_signature(secret: str, body: bytes, signature_header: str) -> bool:
    if not signature_header:
        return False

    mac = hmac.new(secret.encode(), msg=body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)


def render_template(template_name: str, context: dict) -> list[str]:
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(template_name + ".j2")
    rendered = template.render(context)
    return [line.strip() for line in rendered.strip().splitlines() if line.strip()]


def run_commands(workdir: str, commands: list[str]):
    for cmd in commands:
        subprocess.run(cmd, shell=True, check=True, cwd=workdir)
