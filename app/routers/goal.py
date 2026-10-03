import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Goal, GoalCreate, GoalRead, GoalUpdate

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("/", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(goal_in: GoalCreate, session: Session = Depends(get_session)):
    goal = Goal.model_validate(goal_in)
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


@router.get("/", response_model=List[GoalRead])
def list_goals(
    active_only: bool = True,
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    query = select(Goal)
    if active_only:
        query = query.where(Goal.active == True)
    goals = session.exec(query.offset(offset).limit(limit)).all()
    return goals


@router.get("/{goal_id}", response_model=GoalRead)
def get_goal(goal_id: uuid.UUID, session: Session = Depends(get_session)):
    goal = session.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    return goal


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(
    goal_id: uuid.UUID,
    goal_update: GoalUpdate,
    session: Session = Depends(get_session)
):
    goal = session.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
        
    update_data = goal_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(goal, key, value)
        
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: uuid.UUID, session: Session = Depends(get_session)):
    goal = session.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    session.delete(goal)
    session.commit()
    return None