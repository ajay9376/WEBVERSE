from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import DashboardStatsResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Protected Phase 1 endpoint verifying authenticated session and user scoping.
    """
    return DashboardStatsResponse(
        user_id=current_user.id,
        full_name=current_user.full_name,
        college_name=current_user.college_name,
        branch=current_user.branch,
        semester=current_user.semester,
        system_status="ONLINE",
        active_phase="PHASE 1: Foundation & Authentication",
        connected_dimensions=["StudentOS (Academics)", "AI Money Manager", "Life Admin Vault", "Universal AI Core"]
    )
