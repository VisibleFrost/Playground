from fastapi import FastAPI
from fastapi import Body
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

Node.update_forward_refs()

@app.get("/")
async def root():
    return {"message": "Hello World"}

def build_tree(arr: List[Optional[int]], index = 0) -> Optional[Node]:
    if index >= len(arr) or arr[index] is None:
        return None

    return Node(
        val = arr[index],
        left = build_tree(arr, 2*index + 1),
        right = build_tree(arr, 2*index + 2)
    )

def build_bst(values: List[int]):
    if not values:
        return None
    mid = len(values) // 2
    return Node(
        val = values[mid],
        left = build_bst(values[:mid]),
        right = build_bst(values[mid+1:])
    )

def inorder(node: Optional[Node]) -> List[int]:
    if not node:
        return []

    return inorder(node.left) + [node.val] + inorder(node.right)

def ascii_tree(node: Optional[Node], prefix="", is_left=True) -> str:
    if not node:
        return ""
    right = ascii_tree(node.right, prefix + ("|   " if is_left else "    "), False)
    root = prefix + ("└── " if is_left else "┌── ") + str(node.val) + "\n"
    left = ascii_tree(node.left, prefix + ("    " if is_left else "|   "), True)
    return right + root + left

#@app.post("/tree")
#def create_tree(arr: List[Optional[int]] = Body(...)):
#    root = build_tree(arr)
#    return {
#        "inorder": inorder(root),
#        "ascii_tree": ascii_tree(root)
#    }
@app.post("/tree_ascii", response_class=PlainTextResponse)
def create_tree_ascii(request: TreeRequest = Body(...)):
    if request.mode == "bst":
        filtered = [v for v in request.values if v is not None]
        filtered.sort()
        root = build_bst(filtered)
    else:
        root = build_tree(request.values)
    return ascii_tree(root)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Tree API",
        version="1.0.0",
        description="API для дерева",
        routes=app.routes,
    )
    # В нужный путь добавляем примеры для запроса
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
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi