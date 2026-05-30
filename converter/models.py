from pydantic import BaseModel, Field

class ConvertRequest(BaseModel):
    number_str: str
    from_base: int
    to_base: int

class DecodeTextRequest(BaseModel):
    number_str: str = Field(..., description="Строка в кастомной системе (например: #8αw)")
    from_base: int = Field(..., description="База, в которой написан текст", ge=2, le=1007)

class EncodeTextRequest(BaseModel):
    input_text: str = Field(..., description="Обычный читаемый текст (например: Привет)")
    to_base: int = Field(..., description="В какую базу закодировать текст", ge=2, le=1007)