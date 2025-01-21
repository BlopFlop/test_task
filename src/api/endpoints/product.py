from fastapi import APIRouter, Depends

from schemas import ProductSchemaDB, ProductSchemaGetFromStore
from repository import get_product_repository, RepositoryBase
from services import create_or_update_product_from_store

router = APIRouter()


@router.post(
    "/",
    # dependencies=[Depends(current_user)],
    summary="Загрузка товара в базу данных.",
    description=(
        "Получает товар из магазина по артикулу, и загружает его в базу данных"
    ),
    response_model=ProductSchemaDB,
)
async def load_product_to_db(
    get_schema_product: ProductSchemaGetFromStore,
    repository_product: RepositoryBase = Depends(get_product_repository)
) -> ProductSchemaDB:
    return await create_or_update_product_from_store(
        get_schema_product=get_schema_product.article,
        repository_product=repository_product
    )
