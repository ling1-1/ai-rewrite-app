from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.rewrite_record import RewriteRecord
from app.models.user import User
from app.schemas.rewrite import FileExtractResponse, RewriteRequest, RewriteResponse
from app.services.file_extract import FileExtractError, extract_text_from_upload
from app.services.rewrite import RewriteServiceError, rewrite_text
from app.services.viking_rag_service import VikingRAGService

router = APIRouter()


@router.post("", response_model=RewriteResponse)
def create_rewrite(
    payload: RewriteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    use_rag: bool = True  # 是否使用 RAG 增强
):
    """
    改写文本（支持 RAG 增强）
    
    Args:
        payload: 改写请求
        db: 数据库会话
        current_user: 当前用户
        use_rag: 是否使用 RAG 增强（默认 True）
    """
    if not payload.source_text.strip():
        raise HTTPException(status_code=400, detail="原文不能为空")

    try:
        if use_rag:
            # 使用 RAG 增强改写
            result_text = rewrite_text(payload.source_text, db=db, use_rag=True)
        else:
            # 普通改写（不使用 RAG）
            result_text = rewrite_text(payload.source_text, db=db, use_rag=False)
    except RewriteServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    record = RewriteRecord(
        user_id=current_user.id,
        source_text=payload.source_text,
        result_text=result_text,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.post("/sync-to-viking", response_model=dict)
def sync_to_viking(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    同步历史数据到 VikingDB
    
    从本地数据库读取历史改写记录，批量导入到 VikingDB 向量数据库
    
    Args:
        limit: 同步数量上限
        db: 数据库会话
        current_user: 当前用户
    """
    try:
        # 查询历史记录
        records = db.query(RewriteRecord).filter(
            RewriteRecord.user_id == current_user.id
        ).order_by(
            RewriteRecord.created_at.desc()
        ).limit(limit).all()
        
        if not records:
            return {
                "success": True,
                "message": "没有需要同步的历史记录",
                "synced_count": 0
            }
        
        # 转换为 VikingDB 格式
        documents = []
        for record in records:
            doc = {
                "original_text": record.source_text,
                "rewrite_text": record.result_text,
                "metadata": []  # 可以添加标签
            }
            documents.append(doc)
        
        # 批量导入到 VikingDB
        rag_service = VikingRAGService()
        success = rag_service.add_documents(documents)
        
        if success:
            return {
                "success": True,
                "message": f"成功同步 {len(documents)} 条记录到 VikingDB",
                "synced_count": len(documents)
            }
        else:
            return {
                "success": False,
                "message": "同步失败",
                "synced_count": 0
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败：{str(e)}")


@router.post("/extract-file", response_model=FileExtractResponse)
def extract_file_content(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    del current_user

    try:
        source_text = extract_text_from_upload(file)
    except FileExtractError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "filename": file.filename or "未命名文件",
        "source_text": source_text,
        "char_count": len(source_text),
    }
