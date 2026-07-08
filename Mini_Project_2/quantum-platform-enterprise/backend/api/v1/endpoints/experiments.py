from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database.session import get_db
from models.user import User
from schemas.experiment import ExperimentCreate, ExperimentResponse, ExperimentUpdate
from services.experiment_service import ExperimentService
from api.deps import get_current_user
from repositories.experiment_repo import experiment_repo
import uuid

router = APIRouter()

@router.post("", response_model=ExperimentResponse)
async def create_experiment(
    *,
    db: AsyncSession = Depends(get_db),
    experiment_in: ExperimentCreate,
    current_user: User = Depends(get_current_user)
):
    return await ExperimentService.create_experiment(db, experiment_in, current_user.id)

@router.get("", response_model=List[ExperimentResponse])
async def list_experiments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await experiment_repo.get_by_owner(db, current_user.id, skip=skip, limit=limit)

@router.get("/{id}", response_model=ExperimentResponse)
async def get_experiment(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    is_admin = current_user.role.value == "admin"
    return await ExperimentService.get_experiment(db, id, current_user.id, is_admin)

@router.delete("/{id}", response_model=ExperimentResponse)
async def delete_experiment(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exp = await ExperimentService.get_experiment(db, id, current_user.id)
    return await ExperimentService.soft_delete(db, exp)

@router.post("/{id}/execute")
async def execute_experiment(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exp = await ExperimentService.get_experiment(db, id, current_user.id, is_admin=True)
    
    # Mocking actual Quantum Execution for the dashboard
    import asyncio
    await asyncio.sleep(2) # simulate compiling & running
    
    # Update status
    from core.state_machine import ExperimentStatus
    await ExperimentService.update_status(db, exp, ExperimentStatus.COMPLETED)
    
    circuit_ascii = """
     ┌───┐     ┌─┐
q_0: ┤ H ├──■──┤M├───
     └───┘┌─┴─┐└╥┘┌─┐
q_1: ─────┤ X ├─╫─┤M├
          └───┘ ║ └╥┘
c: 2/═══════════╩══╩═
                0  1 
    """
    if exp.algorithm == "quantum_teleportation":
        circuit_ascii = """
        ┌───┐          ┌─┐      
  q_0: ─┤ H ├──■───────┤M├──────
        └───┘┌─┴─┐     └╥┘┌─┐   
  q_1: ──────┤ X ├──■───╫─┤M├───
             └───┘┌─┴─┐ ║ └╥┘┌─┐
  q_2: ───────────┤ X ├─╫──╫─┤M├
                  └───┘ ║  ║ └╥┘
c_0: 1/═════════════════╩══╬══╬═
                        0  ║  ║ 
c_1: 1/════════════════════╩══╬═
                           0  ║ 
c_2: 1/═══════════════════════╩═
                              0 
        """
        
    return {
        "job_id": f"job_{uuid.uuid4().hex[:8]}",
        "status": "COMPLETED",
        "counts": {"00": 512, "11": 512} if exp.algorithm == "bell_state" else {"000": 256, "011": 256, "100": 256, "111": 256},
        "circuit_ascii": circuit_ascii.strip()
    }
