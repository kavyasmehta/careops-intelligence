"""Shared response envelopes and list-query parameters used by every router."""
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int


class ListResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PageMeta


class ItemResponse(BaseModel, Generic[T]):
    data: T


class ListParams:
    """Common pagination/sort query params, reused across every list endpoint."""

    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        sort: str | None = Query(
            default=None,
            description="Field to sort by; prefix with '-' for descending, e.g. '-created_at'.",
        ),
        q: str | None = Query(default=None, description="Free-text search term"),
    ):
        self.page = page
        self.page_size = page_size
        self.q = q
        if sort:
            self.sort_field = sort.lstrip("-")
            self.sort_direction = -1 if sort.startswith("-") else 1
        else:
            self.sort_field = "created_at"
            self.sort_direction = -1
