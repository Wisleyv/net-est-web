from fastapi import APIRouter, HTTPException, Body, Depends, Query, Response
from typing import List
from src.models.annotation import AnnotationAction, AnnotationResponse, AnnotationsList, Annotation, AnnotationCreate, AuditEntry
from src.repository.fs_repository import get_repository
import json
import csv
import io

router = APIRouter(prefix="/api/v1/annotations", tags=["annotations"])

def get_session_id(session_id: str = Query(..., description="Session identifier")):
    return session_id

@router.get("/", response_model=AnnotationsList)
async def list_annotations(session_id: str = Depends(get_session_id)):
    repo = get_repository()
    repo.load_session(session_id)
    return AnnotationsList(annotations=repo.list_visible())

@router.get("/search", response_model=AnnotationsList)
async def search_annotations(
    session_id: str = Depends(get_session_id),
    statuses: List[str] | None = Query(None),
    strategy_codes: List[str] | None = Query(None),
):
    repo = get_repository()
    repo.load_session(session_id)
    anns = repo.query(statuses=statuses, strategy_codes=strategy_codes, session_id=session_id)
    return AnnotationsList(annotations=anns)

@router.patch("/{annotation_id}", response_model=AnnotationResponse)
async def patch_annotation(annotation_id: str, payload: AnnotationAction = Body(...), session_id: str = Depends(get_session_id)):
    repo = get_repository()
    repo.load_session(session_id)
    try:
        if payload.action == 'accept':
            ann = repo.accept(annotation_id, payload.session_id)
        elif payload.action == 'reject':
            ann = repo.reject(annotation_id, payload.session_id)
        elif payload.action == 'modify':
            if not payload.new_code:
                raise HTTPException(status_code=400, detail='missing_new_code')
            ann = repo.modify(annotation_id, payload.session_id, payload.new_code)
        else:
            raise HTTPException(status_code=400, detail='unsupported_action')
        repo.persist_session(payload.session_id)
        return AnnotationResponse(annotation=ann)
    except KeyError:
        raise HTTPException(status_code=404, detail='annotation_not_found')
    except ValueError as ve:
        if str(ve) == 'cannot_accept_modified':
            raise HTTPException(status_code=400, detail='cannot_accept_modified')
        if str(ve) == 'invalid_new_code':
            raise HTTPException(status_code=400, detail='invalid_new_code')
        raise HTTPException(status_code=400, detail='invalid_state')

@router.post("/", response_model=AnnotationResponse)
async def create_annotation(payload: AnnotationCreate, session_id: str = Depends(get_session_id)):
    repo = get_repository()
    repo.load_session(session_id)
    try:
        ann = repo.create(session_id, payload.strategy_code, [o.model_dump() if hasattr(o, 'model_dump') else o for o in payload.target_offsets], payload.comment)
        repo.persist_session(session_id)
        return AnnotationResponse(annotation=ann)
    except Exception:
        raise HTTPException(status_code=400, detail='creation_failed')

@router.get('/audit', response_model=List[AuditEntry])
async def list_audit(session_id: str = Depends(get_session_id), annotation_id: str | None = Query(None), actions: List[str] | None = Query(None)):
    repo = get_repository()
    repo.load_session(session_id)
    return repo.list_audit(annotation_id, actions=actions, session_id=session_id)

@router.post('/export')
async def export_annotations(
    format: str = Query('jsonl', enum=['jsonl','csv']),
    scope: str = Query('both', enum=['gold','raw','both'], description='Which annotations to include'),
    session_id: str = Depends(get_session_id)
):
    repo = get_repository()
    repo.load_session(session_id)
    # Scope filtering: gold => validated true and status in accepted/created; raw => pending/modified (and unvalidated)
    if scope == 'gold':
        anns = [a for a in repo.export(include_statuses=['accepted','created']) if getattr(a, 'validated', False)]
    elif scope == 'raw':
        anns = repo.export(include_statuses=['pending','modified'])
    else:
        anns = repo.export()
    if format == 'jsonl':
        def convert(obj):
            if isinstance(obj, list):
                return [convert(x) for x in obj]
            if isinstance(obj, dict):
                return {k: convert(v) for k,v in obj.items()}
            from datetime import datetime
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        lines = []
        for a in anns:
            base = convert(a.model_dump())
            # Ensure explanation present in export payload for API parity with CLI (Phase 4f)
            base['explanation'] = a.explanation
            # ML alignment: expose gold flags and decision fields
            base['validated'] = getattr(a, 'validated', False)
            base['manually_assigned'] = getattr(a, 'manually_assigned', False)
            base['decision'] = a.status
            lines.append(json.dumps(base, ensure_ascii=False))
        content = '\n'.join(lines)
        return Response(content=content, media_type='application/x-ndjson', headers={
            'Content-Disposition': 'attachment; filename="annotations.jsonl"'
        })
    # CSV
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['id','strategy_code','status','decision','origin','created_at','updated_at','original_code','comment','explanation','validated','manually_assigned'])
    for a in anns:
        writer.writerow([a.id,a.strategy_code,a.status,a.status,a.origin,a.created_at.isoformat(),a.updated_at.isoformat(),a.original_code or '', a.comment or '', a.explanation or '', int(getattr(a,'validated',False)), int(getattr(a,'manually_assigned',False))])
    return Response(content=buf.getvalue(), media_type='text/csv', headers={
        'Content-Disposition': 'attachment; filename="annotations.csv"'
    })
