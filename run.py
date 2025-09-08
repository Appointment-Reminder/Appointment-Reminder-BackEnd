import sys
from pathlib import Path
import uvicorn

# Add project root to sys.path so subprocesses can find 'app'
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
