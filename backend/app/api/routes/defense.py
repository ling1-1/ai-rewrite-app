from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.defense import (
    DefenseFlowResponse,
    DefensePptRequest,
    DefensePptResponse,
    DefenseSpeechRequest,
    DefenseSpeechResponse,
)
from app.services.defense import (
    DefenseServiceError,
    generate_defense_flow,
    generate_defense_ppt,
    generate_defense_speech,
)

router = APIRouter()


@router.post("/ppt", response_model=DefensePptResponse)
def create_defense_ppt(
    payload: DefensePptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user

    if not payload.thesis_text.strip():
        raise HTTPException(status_code=400, detail="论文内容不能为空")

    try:
        ppt_content = generate_defense_ppt(
            payload.thesis_text,
            db=db,
            options=payload.model_dump(exclude={"thesis_text"}),
        )
    except DefenseServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"ppt_content": ppt_content}


@router.post("/speech", response_model=DefenseSpeechResponse)
def create_defense_speech(
    payload: DefenseSpeechRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user

    if not payload.thesis_text.strip():
        raise HTTPException(status_code=400, detail="论文内容不能为空")
    if not payload.ppt_content.strip():
        raise HTTPException(status_code=400, detail="请先生成或填写答辩PPT内容")

    try:
        speech_content = generate_defense_speech(
            payload.thesis_text,
            payload.ppt_content,
            db=db,
            options=payload.model_dump(exclude={"thesis_text", "ppt_content"}),
        )
    except DefenseServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"speech_content": speech_content}


@router.post("/flow", response_model=DefenseFlowResponse)
def create_defense_flow(
    payload: DefensePptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user

    if not payload.thesis_text.strip():
        raise HTTPException(status_code=400, detail="论文内容不能为空")

    try:
        ppt_content, speech_content = generate_defense_flow(
            payload.thesis_text,
            db=db,
            options=payload.model_dump(exclude={"thesis_text"}),
        )
    except DefenseServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "ppt_content": ppt_content,
        "speech_content": speech_content,
    }
