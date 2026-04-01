from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.rewrite_record import RewriteRecord
from app.models.user import User
from app.schemas.rewrite import FileExtractResponse, RewriteRequest, RewriteResponse
from app.services.file_extract import FileExtractError, extract_text_from_upload
from app.services.rewrite import RewriteServiceError, rewrite_text
from app.services.viking_rag_service import VikingRAGService
from app.core.config import settings

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

    # 保存到本地数据库
    record = RewriteRecord(
        user_id=current_user.id,
        source_text=payload.source_text,
        result_text=result_text,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # ⚠️ 不再自动写入 VikingDB - 由用户手动选择
    # VikingDB 只存储明确成功的降重案例

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


@router.post("/{record_id}/sync-to-viking")
def sync_record_to_viking(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    手动将历史记录写入 VikingDB（用于 RAG 检索）
    
    只有明确成功的降重案例才写入向量数据库
    """
    # 查询记录
    record = db.query(RewriteRecord).filter(
        RewriteRecord.id == record_id,
        RewriteRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    try:
        from app.services.viking_rag_service import VikingRAGService
        rag_service = VikingRAGService()
        
        # metadata 使用字符串数组（VikingDB 要求的格式）
        # 存储：用户名、使用模型、使用时间
        username = getattr(current_user, 'username', f'user_{current_user.id}')
        metadata = [
            username,
            settings.anthropic_model,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        
        print(f"📝 手动写入 VikingDB:")
        print(f"  record_id: {record_id}")
        print(f"  original_text: {record.source_text[:50]}...")
        print(f"  rewrite_text: {record.result_text[:50]}...")
        print(f"  metadata: {metadata}")
        
        success = rag_service.add_single(
            original_text=record.source_text,
            rewrite_text=record.result_text,
            metadata=metadata
        )
        
        if success:
            print(f"✅ 成功写入 VikingDB")
            return {
                "success": True,
                "message": "已成功写入向量数据库",
                "record_id": record_id
            }
        else:
            print(f"⚠️ VikingDB 写入返回失败")
            raise HTTPException(status_code=500, detail="VikingDB 写入失败")
            
    except Exception as e:
        print(f"❌ 写入 VikingDB 异常：{e}")
        raise HTTPException(status_code=500, detail=f"写入失败：{str(e)}")


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
