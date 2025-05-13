import toml
import json
import logging

from fastapi import FastAPI, Request, HTTPException

from utils import verify_signature, render_template, run_commands

logging.basicConfig(level=logging.INFO)

app = FastAPI()


@app.post("/githooker")
async def webhook(request: Request):
    config = toml.load("config.toml")

    body = await request.body()
    if not body:
        logging.warning("Empty request body")
        raise HTTPException(status_code=400, detail="Empty request body")
    signature = request.headers.get("X-Hub-Signature-256")

    payload = json.loads(body)
    ref = payload.get("ref")
    repo_full_name = payload.get("repository", {}).get("full_name")

    # Check repo match
    repo_conf = config.get("repos", {}).get(repo_full_name)
    if not repo_conf:
        logging.info(f"Ignored: repo '{repo_full_name}' not configured")
        return {"status": f"Ignored: repo '{repo_full_name}' not configured"}

    # Verify signature
    if signature:
        if not verify_signature(repo_conf.get("secret"), body, signature):
            logging.warning(f"Invalid signature for repo '{repo_full_name}'")
            raise HTTPException(status_code=403, detail="Invalid signature")

    # Check branch match
    expected_ref = f"refs/heads/{repo_conf['branch']}"
    if ref != expected_ref:
        logging.info(f"Ignored: ref '{ref}' does not match '{expected_ref}'")
        return {"status": f"Ignored: ref '{ref}' does not match '{expected_ref}'"}

    # Determine command source: template or raw list
    try:
        if "template" in repo_conf:
            commands = render_template(repo_conf["template"], repo_conf.get("template_context", {}))
        elif "commands" in repo_conf:
            commands = repo_conf["commands"]
        else:
            logging.warning(f"No commands or template found for repo '{repo_full_name}'")
            raise HTTPException(status_code=400, detail="No commands or template found")

        run_commands(repo_conf["workdir"], commands)

    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=f"Deployment failed: {e}")

    logging.info(f"Deployment succeeded for repo '{repo_full_name}'")
    return {"status": "Success: deployment triggered"}
