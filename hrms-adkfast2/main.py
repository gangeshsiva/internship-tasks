import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

SESSION_SERVICE_URI ="sqlite:///sessions.db"

ALLOWED_ORIGINS = ["*","http://localhost","http://localhost:8080"]

SERVE_WEB_INTERFACE = True

app=get_fast_api_app(   
    agents_dir=os.path.join(AGENT_DIR, "agents_hrms"),
    session_service_uri=SESSION_SERVICE_URI,
    allowed_origins=ALLOWED_ORIGINS,
    serve_web_interface=SERVE_WEB_INTERFACE
)

if __name__ == "__main__":
    port=int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)