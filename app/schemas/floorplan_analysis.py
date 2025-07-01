from pydantic import BaseModel
from typing import Optional, Any

class FloorPlanAnalysisBase(BaseModel):
    file_id: int
    result_json: Optional[Any] = None

class FloorPlanAnalysisCreate(FloorPlanAnalysisBase):
    pass

class FloorPlanAnalysisRead(FloorPlanAnalysisBase):
    id: int
    user_id: int
    created_at: Optional[str]

    class Config:
        orm_mode = True 