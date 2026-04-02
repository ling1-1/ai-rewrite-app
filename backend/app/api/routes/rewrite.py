from datetime import datetime
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.rewrite_record import RewriteRecord
from app.models.user import User
from app.schemas.rewrite import FileExtractResponse, RewriteRequest, RewriteResponse
from app.services.file_extract import FileExtractError, extract_text_from_upload
from app.services.rewrite import RewriteServiceError, rewrite_text
from app.services.vector_db_backend import get_vector_db

router = APIRouter()


def _build_vector_doc(record: RewriteRecord, username: str) -> dict:
    return {
        "id": record.id,
        "original_text": record.source_text,
        "rewrite_text": record.result_text,
        "metadata": [username],
        "payload": {
            "record_id": record.id,
            "user_id": record.user_id,
            "username": username,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "notes": record.notes,
            "is_favorite": record.is_favorite,
            "name": record.name,
        },
    }


def _sync_documents_to_vector_db(vector_db, documents: list[dict]) -> int:
    if not documents:
        return 0

    if hasattr(vector_db, "service") and hasattr(vector_db.service, "add_documents"):
        return int(vector_db.service.add_documents(documents))

    synced_count = 0
    for doc in documents:
        if vector_db.add(
            doc["original_text"],
            doc["rewrite_text"],
            doc["metadata"],
            doc_id=doc.get("id"),
            extra_payload=doc.get("payload"),
        ):
            synced_count += 1
    return synced_count


def _mark_record_synced(record: RewriteRecord) -> int:
    metadata = record.metadata_ or {}
    previous_count = int(metadata.get("vector_db_sync_count", 0) or 0)
    sync_count = previous_count + 1
    record.is_favorite = False
    record.metadata_ = {
        **metadata,
        "vector_db_synced": True,
        "vector_db_synced_at": datetime.utcnow().isoformat(),
        "vector_db_point_id": record.id,
        "vector_db_sync_count": sync_count,
    }
    return sync_count


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
            result_text = rewrite_text(
                payload.source_text,
                db=db,
                use_rag=True,
                rewrite_mode=payload.rewrite_mode,
            )
        else:
            # 普通改写（不使用 RAG）
            result_text = rewrite_text(
                payload.source_text,
                db=db,
                use_rag=False,
                rewrite_mode=payload.rewrite_mode,
            )
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

    return record


@router.post("/sync-to-viking", response_model=dict)
@router.post("/sync-to-vector-db", response_model=dict)
def sync_to_vector_db(
    limit: int = 100,
    favorites_only: bool = Query(True, description="仅同步已收藏记录"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    同步历史数据到当前向量数据库
    
    从本地数据库读取历史改写记录，批量导入到当前向量数据库
    
    Args:
        limit: 同步数量上限
        db: 数据库会话
        current_user: 当前用户
    """
    try:
        query = db.query(RewriteRecord).filter(
            RewriteRecord.user_id == current_user.id
        )

        if favorites_only:
            query = query.filter(RewriteRecord.is_favorite.is_(True))

        records = query.order_by(
            RewriteRecord.created_at.desc()
        ).limit(limit).all()

        if not records:
            return {
                "success": True,
                "message": "没有需要同步的历史记录",
                "synced_count": 0
            }
        
        documents = [_build_vector_doc(record, current_user.username) for record in records]
        
        vector_db = get_vector_db(db=db)
        synced_count = _sync_documents_to_vector_db(vector_db, documents)

        if synced_count:
            updated_count = 0
            for record in records:
                sync_count = _mark_record_synced(record)
                if sync_count > 1:
                    updated_count += 1
            db.commit()
            return {
                "success": True,
                "message": (
                    f"成功批量入库 {synced_count} 条记录"
                    if not updated_count
                    else f"成功批量入库 {synced_count} 条记录，其中 {updated_count} 条已更新入库"
                ),
                "synced_count": synced_count
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
@router.post("/{record_id}/sync-to-vector-db")
def sync_record_to_vector_db(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    手动将历史记录写入当前向量数据库（用于 RAG 检索）
    
    只有明确成功的降重案例才写入向量数据库
    """
    # 查询记录
    record = db.query(RewriteRecord).filter(
        RewriteRecord.id == record_id,
        RewriteRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    if not record.is_favorite:
        raise HTTPException(status_code=400, detail="请先将该记录标记为收藏，再同步到向量数据库")
    
    try:
        print(f"📝 手动写入向量数据库:")
        print(f"  record_id: {record_id}")
        print(f"  original_text: {record.source_text[:50]}...")
        print(f"  rewrite_text: {record.result_text[:50]}...")
        print(f"  favorite: {record.is_favorite}")

        vector_db = get_vector_db(db=db)
        success = vector_db.add(
            record.source_text,
            record.result_text,
            [current_user.username],
            doc_id=record.id,
            extra_payload=_build_vector_doc(record, current_user.username)["payload"],
        )
        
        if success:
            previous_count = record.vector_db_sync_count
            sync_count = _mark_record_synced(record)
            db.commit()
            print(f"✅ 成功写入向量数据库")
            return {
                "success": True,
                "message": "已成功更新入库" if previous_count > 0 else "已成功入库",
                "record_id": record_id,
                "sync_count": sync_count,
            }
        else:
            print(f"⚠️ 向量数据库写入返回失败")
            raise HTTPException(status_code=500, detail="向量数据库写入失败")
            
    except Exception as e:
        print(f"❌ 写入向量数据库异常：{e}")
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
