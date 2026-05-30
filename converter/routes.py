from fastapi import APIRouter, HTTPException
from .logic import CustomBaseConverter
from .models import ConvertRequest, DecodeTextRequest, EncodeTextRequest

router = APIRouter(prefix="/converter", tags=["Converter"])
converter = CustomBaseConverter()

@router.post("/convert")
def convert_between_systems(body: ConvertRequest):
    try:
        result = converter.convert_any_base(
            number_str=body.number_str, 
            from_base=body.from_base, 
            to_base=body.to_base
        )
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/to-text")
def convert_to_text(body: DecodeTextRequest):
    try:
        binary_res, text_res = converter.system_to_text(
            number_str=body.number_str, 
            from_base=body.from_base
        )
        return {"status": "success", "binary": binary_res, "text": text_res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/from-text")
def convert_from_text(body: EncodeTextRequest):
    try:
        binary_res, system_res = converter.text_to_system(
            input_text=body.input_text,
            to_base=body.to_base
        )
        return {"status": "success", "binary": binary_res, "result": system_res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))