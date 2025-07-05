from fastapi import FastAPI
from fastapi import Body, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi.responses import PlainTextResponse
from fastapi.openapi.utils import get_openapi


app = FastAPI()

class TreeRequest(BaseModel):
    values: List[Optional[int]] = Field(..., description="Массив чисел для построения дерева")
    mode: Optional[str] = Field(None, description="Режим построения дерева")

class Node(BaseModel):
    val: int
    left: Optional['Node'] = None
    right: Optional['Node'] = None

class EncodeRequest(BaseModel):
    decimal: int

class DecodeRequest(BaseModel):
    encoded: str

Node.update_forward_refs()

class CustomBaseConverter:
    def __init__(self) -> None:
        self.base62 = (
                [str(i) for i in range(10)] +
                [chr(ord('A') + i) for i in range(26)] +
                [chr(ord('a') + i) for i in range(26)]
        )
        self.MAX_LENGTH = 1050
        self.prefixes = ["!", "@", "#", "$", "%", "^", "&", "*", "_", "~", "α", "β", "γ", "δ", "λ"]
        self.all_chars = self.base62.copy() + self.prefixes.copy()

        for prefix in self.prefixes:
            for char in self.base62:
                self.all_chars.append(prefix + char)

        self.char_to_value = {char: i for i, char in enumerate(self.all_chars)}

    def to_custom_base(self, n: int) -> str:
        if n == 0:
            return "0"

        res = []
        is_negative = n < 0
        n = abs(n)
        while n > 0:
            d = n % len(self.all_chars)
            res.append(self.all_chars[d])
            n = n // len(self.all_chars)

        if is_negative:
            res.append("-")

        result = "".join(reversed(res))
        return "-" + result if is_negative else result

    def from_custom_base(self, s: str) -> int:
        if not s:
            raise ValueError("Пустая строка")
        if len(s) > self.MAX_LENGTH:
            raise ValueError(f"Слишком длинное число (максимум {self.MAX_LENGTH} символов)")
        if s == "0":
            return 0

        is_negative = len(s) > 0 and s[0] == "-"
        if is_negative:
            s = s.replace("-", "", 1)

        n = 0
        i = 0
        while i < len(s):
            char = s[i]
            found = False
            for prefix in self.prefixes:
                if s.startswith(prefix, i) and i + 1 < len(s):
                    combined = prefix + s[i + 1]
                    if combined in self.char_to_value:
                        n = n * len(self.all_chars) + self.char_to_value[combined]
                        i += 2
                        found = True
                        break
            if not found:
                if char in self.char_to_value:
                    n = n * len(self.all_chars) + self.char_to_value[char]
                    i += 1
                else:
                    raise ValueError(f"Недопустимый символ: '{char}'")
        return -n if is_negative else n

class TreeProcessor:
    def build_tree(self, arr: List[Optional[int]], index=0) -> Optional[Node]:
        if index >= len(arr) or arr[index] is None:
            return None

        return Node(
            val=arr[index],
            left=self.build_tree(arr, 2 * index + 1),
            right=self.build_tree(arr, 2 * index + 2)
        )

    def build_bst(self, values: List[int]):
        if not values:
            return None
        mid = len(values) // 2
        return Node(
            val=values[mid],
            left=self.build_bst(values[:mid]),
            right=self.build_bst(values[mid + 1:])
        )

    def inorder(self, node: Optional[Node]) -> List[int]:
        if not node:
            return []

        return self.inorder(node.left) + [node.val] + self.inorder(node.right)

    def ascii_tree(self, node: Optional[Node], prefix="", is_left=True) -> str:
        if not node:
            return ""
        right = self.ascii_tree(node.right, prefix + ("|   " if is_left else "    "), False)
        root = prefix + ("└── " if is_left else "┌── ") + str(node.val) + "\n"
        left = self.ascii_tree(node.left, prefix + ("    " if is_left else "|   "), True)
        return right + root + left

converter = CustomBaseConverter()
TPr = TreeProcessor()
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/tree_ascii", response_class=PlainTextResponse)
def create_tree_ascii(request: TreeRequest = Body(...)):
    if request.mode == "bst":
        filtered = [v for v in request.values if v is not None]
        filtered.sort()
        root = TPr.build_bst(filtered)
    else:
        root = TPr.build.build_tree(request.values)
    return TPr.ascii_tree(root)

@app.post("/custom-base/encode")
def custom_encode(request: EncodeRequest):
    try:
        result = converter.to_custom_base(request.decimal)
        return {"decimal": request.decimal, "encoded": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.post("/custom-base/decode")
def custom_decode(request: DecodeRequest):
    try:
        result = converter.from_custom_base(request.encoded)
        return {"encoded": request.decimal, "decimal": result}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Tree API",
        version="1.0.0",
        description="API для дерева и 1007-ричной системы",
        routes=app.routes,
    )
    # В нужный путь добавляем примеры для запроса(для себя)
    openapi_schema["paths"]["/tree_ascii"]["post"]["requestBody"]["content"]["application/json"]["examples"] = {
        "bst_example": {
            "summary": "BST пример",
            "value": {
                "values": [5, 3, 7, 2, 4, 6, 8],
                "mode": "bst"
            }
        },
        "any_tree_example": {
            "summary": "Любое дерево",
            "value": {
                "values": [537278, 358627, 753862, 253768, None, 653827, 862753],
                "mode": None
            }
        }
    }

    openapi_schema["paths"]["/custom-base/encode"]["post"]["requestBody"]["content"]["application/json"]["examples"] = {
        "decimal": 12543
    }

    openapi_schema["paths"]["/custom-base/decode"]["post"]["requestBody"]["content"]["application/json"]["examples"] = {
        "encoded" : "*_βλ"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi