import contextlib
from typing import Any
import logging

import aiohttp
from fastapi.exceptions import HTTPException

from schemas import ProductSchemaCreate, ProductSchemaDB
from repository import ProductRepository, get_product_repository

from core.db import get_async_session
from core.config import settings
from core.constants import (
    STORE_URL_GET_PRODUCT,
    STORE_KEY_DATA,
    STORE_KEY_PRODUCT,
    STORE_KEY_ARTICLE,
    STORE_KEY_RATING,
    STORE_KEY_PRICE,
    STORE_KEY_NAME,
    STORE_KEY_TOTAL
)

get_async_session_context = contextlib.asynccontextmanager(get_async_session)


def get_store_url(article: int) -> str:
    return STORE_URL_GET_PRODUCT.format(settings.key_store, article)


def _get_field_from_api(data: dict[str, Any]):
    fields = {
        STORE_KEY_ARTICLE: "article",
        STORE_KEY_NAME: "name",
        STORE_KEY_PRICE: "price",
        STORE_KEY_RATING: "rating",
        STORE_KEY_TOTAL: "total",
    }

    if STORE_KEY_DATA not in data:
        raise HTTPException(500)

    data = data.get(STORE_KEY_DATA)

    if STORE_KEY_PRODUCT not in data:
        raise HTTPException(500)

    data = data.get(STORE_KEY_PRODUCT)

    if not data:
        raise HTTPException(500)

    data = data[0]

    product_values = {}
    for key, field in fields.items():
        if key not in data:
            raise HTTPException(500)

        value = data.get(key)

        if STORE_KEY_PRICE == key:
            value = float(value / 100)

        product_values[field] = value
    return product_values


async def get_data_from_store(url: str) -> dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(400)
            data: dict[str, Any] = await response.json()
    return _get_field_from_api(data)


async def create_or_update_product_from_store(
    article: int,
    repository: ProductRepository,
    perform_update: bool = False
) -> ProductSchemaDB:
    store_url = get_store_url(article)
    product_values = await get_data_from_store(url=store_url)
    if perform_update:
        product_values["perform_update"] = perform_update
    product_in = ProductSchemaCreate(**product_values)
    return await repository.create_or_update(product_in)


async def perform_update_products_from_store() -> None:
    async with get_async_session_context() as session:
        repository_product: ProductRepository = (
            await get_product_repository(session)
        )
        products: list[ProductSchemaDB] = (
            await repository_product.get_obj_for_field_arg(
                field="perform_update",
                arg=True,
                many=True
            )
        )
        for product in products:
            update_product = await create_or_update_product_from_store(
                product.article,
                repository_product
            )
