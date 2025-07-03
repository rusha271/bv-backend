from fastapi import APIRouter

router = APIRouter()
_reload_flag = {"reload": False}

@router.get("/should-reload")
def should_reload():
    value = _reload_flag["reload"]
    _reload_flag["reload"] = False  # Reset after one reload
    return {"reload": value}

@router.post("/trigger-reload")
def trigger_reload():
    _reload_flag["reload"] = True
    return {"ok": True} 