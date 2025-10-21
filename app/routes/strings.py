# Endpoints for string analysis

from fastapi import APIRouter, HTTPException, Depends, Response
from sqlmodel import Session, select
from app.models import StringRecord
from app.database import get_session
from app.utils import analyze_string, parse_natural_query
from app.schemas import StringResponse, StringProperties
from pydantic import BaseModel, validator

router = APIRouter(prefix="/strings", tags=["Strings"])

class StringInput(BaseModel):
    value: str
    
    @validator('value')
    def validate_value(cls, v):
        if not isinstance(v, str):
            raise ValueError('value must be a string')
        return v

@router.post("", status_code=201, response_model=StringResponse)
def create_string(payload: StringInput, session: Session = Depends(get_session)):
    value = payload.value
    
    if not value:
        raise HTTPException(status_code=400, detail="Invalid or missing 'value' field")

    analysis = analyze_string(value)
    existing = session.get(StringRecord, analysis["sha256_hash"])
    if existing:
        raise HTTPException(status_code=409, detail="String already exists")

    new_record = StringRecord(
        id=analysis["sha256_hash"],
        value=value,
        properties=analysis
    )
    session.add(new_record)
    session.commit()
    session.refresh(new_record)
    # Build response using schema for correct field order
    return StringResponse(
        id=new_record.id,
        value=new_record.value,
        properties=StringProperties(**new_record.properties),
        created_at=new_record.created_at
    )

# Natural language filter MUST come before /{value} to avoid routing conflicts
@router.get("/filter-by-natural-language")
def filter_by_natural_language(query: str, session: Session = Depends(get_session)):
    parsed_filters = parse_natural_query(query)
    if not parsed_filters:
        raise HTTPException(400, "Unable to parse natural language query")
    records = session.exec(select(StringRecord)).all()
    filtered = []
    for r in records:
        props = r.properties
        match = True
        for key, value in parsed_filters.items():
            if key == 'is_palindrome' and props.get('is_palindrome') != value:
                match = False
            elif key == 'min_length' and props.get('length', 0) < value:
                match = False
            elif key == 'max_length' and props.get('length', 0) > value:
                match = False
            elif key == 'word_count' and props.get('word_count', 0) != value:
                match = False
            elif key == 'contains_character' and value not in props.get('character_frequency_map', {}):
                match = False
        if match:
            filtered.append(r)
    # Format each item using the response schema
    formatted = [
        StringResponse(
            id=item.id,
            value=item.value,
            properties=StringProperties(**item.properties),
            created_at=item.created_at
        ) for item in filtered
    ]
    return {
        "data": formatted,
        "count": len(formatted),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed_filters
        }
    }

@router.get("/{value}", response_model=StringResponse)
def get_string(value: str, session: Session = Depends(get_session)):
    records = session.exec(select(StringRecord).where(StringRecord.value == value)).all()
    if not records:
        raise HTTPException(status_code=404, detail="String not found")
    record = records[0]
    return StringResponse(
        id=record.id,
        value=record.value,
        properties=StringProperties(**record.properties),
        created_at=record.created_at
    )

@router.get("")
def get_strings(
    is_palindrome: bool = None,
    min_length: int = None,
    max_length: int = None,
    word_count: int = None,
    contains_character: str = None,
    session: Session = Depends(get_session)
):
    records = session.exec(select(StringRecord)).all()
    filtered = []
    for r in records:
        props = r.properties
        if is_palindrome is not None and props.get('is_palindrome') != is_palindrome:
            continue
        if min_length is not None and props.get('length', 0) < min_length:
            continue
        if max_length is not None and props.get('length', 0) > max_length:
            continue
        if word_count is not None and props.get('word_count', 0) != word_count:
            continue
        if contains_character is not None and contains_character not in props.get('character_frequency_map', {}):
            continue
        filtered.append(r)
    filters_applied = {k: v for k, v in locals().items() if k in ['is_palindrome', 'min_length', 'max_length', 'word_count', 'contains_character'] and v is not None}
    # Format each item using the response schema
    formatted = [
        StringResponse(
            id=item.id,
            value=item.value,
            properties=StringProperties(**item.properties),
            created_at=item.created_at
        ) for item in filtered
    ]
    return {
        "data": formatted,
        "count": len(formatted),
        "filters_applied": filters_applied
    }

@router.delete("/{value}")
def delete_string(value: str, session: Session = Depends(get_session)):
    # Compute hash
    analysis = analyze_string(value)
    record = session.get(StringRecord, analysis["sha256_hash"])
    if not record:
        raise HTTPException(404, "String not found")
    session.delete(record)
    session.commit()
    return Response(status_code=204)
