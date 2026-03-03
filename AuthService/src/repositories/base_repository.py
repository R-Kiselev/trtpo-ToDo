from typing import Generic, Optional, Type, TypeVar
from uuid import UUID

from fastapi import Request
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import BaseModel
from auth.schemas import PageResponseSchema
from auth.utils import create_page_url
from exceptions import (
    AlreadyExistsError,
    NotFoundError,
)

ModelType = TypeVar("ModelType", bound=BaseModel)
ModelGetSchema = TypeVar("ModelGetSchema", bound=PydanticBaseModel)
ModelCreationSchema = TypeVar("ModelCreationSchema", bound=PydanticBaseModel)
ModelUpdateSchema = TypeVar("ModelUpdateSchema", bound=PydanticBaseModel)


class BaseRepository(Generic[ModelType, ModelGetSchema, ModelCreationSchema, ModelUpdateSchema]):
    def __init__(
        self,
        model: Type[ModelType],
        get_schema: Type[ModelGetSchema],
        creation_schema: Type[ModelCreationSchema],
        update_schema: Type[ModelUpdateSchema],
        session: AsyncSession,
    ):
        self._session = session
        self.model = model
        self.get_schema = get_schema
        self.creation_schema = creation_schema
        self.update_schema = update_schema

    async def get_all_with_filter_sort_pagination(
        self,
        request: Request,
        page_number: int,
        page_size: int,
        role: str,
        sort_by: str,
        sort_order: str,
    ) -> PageResponseSchema:
        query = select(self.model)

        if role:
            query = query.where(self.model.role.in_([role]))

        if sort_by:
            if sort_order == "asc":
                query = query.order_by(getattr(self.model, sort_by).asc())
            else:
                query = query.order_by(getattr(self.model, sort_by).desc())

        offset = (page_number - 1) * page_size

        count_query = select(func.count()).select_from(query.subquery())
        total_items = (await self._session.execute(count_query)).scalar_one()
        total_pages = (total_items + page_size - 1) // page_size

        query = query.offset(offset).limit(page_size)
        result = await self._session.execute(query)
        items = result.scalars().all()

        prev_page_number = page_number - 1 if page_number > 1 else 1
        prev_page = create_page_url(request, prev_page_number)
        next_page = create_page_url(request, page_number + 1)

        page_response = PageResponseSchema(
            total=total_items,
            pages=total_pages,
            results=[self.get_schema.model_validate(item) for item in items],
            prev_page=prev_page,
            next_page=next_page,
        )

        return page_response

    async def get_model_by_id(self, id: UUID) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self._session.execute(query)
        item = result.scalars().first()

        if not item:
            raise NotFoundError("Resource not found")

        return item

    async def get_by_id(self, id: UUID) -> Optional[ModelGetSchema]:
        item = await self.get_model_by_id(id)

        return self.get_schema.model_validate(item)

    async def save(self, data: ModelCreationSchema) -> ModelGetSchema:
        data_dict = data.model_dump()
        item = self.model(**data_dict)
        self._session.add(item)

        try:
            await self._session.flush([item])
        except IntegrityError:
            raise AlreadyExistsError("Resource already exists")

        return self.get_schema.model_validate(item)

    async def update_item(self, item: ModelType, new_data: ModelUpdateSchema) -> ModelType:
        new_data_dict = new_data.model_dump(exclude_unset=True)

        for key, value in new_data_dict.items():
            setattr(item, key, value)

        await self._session.flush(
            [
                item,
            ]
        )

        return item

    async def update_by_id(self, id: UUID, new_data: ModelUpdateSchema) -> Optional[ModelGetSchema]:
        item = await self.get_model_by_id(id)

        updated_item = await self.update_item(item, new_data)
        return self.get_schema.model_validate(updated_item)

    async def delete_by_id(self, id: UUID) -> Optional[ModelGetSchema]:
        item = await self.get_model_by_id(id)

        pydantic_item = self.get_schema.model_validate(item)
        await self._session.delete(item)
        return pydantic_item
