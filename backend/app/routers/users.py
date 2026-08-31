from fastapi import APIRouter, Depends

from app.core.errors import NotFoundError
from app.core.roles import Role, require_role
from app.repositories.users import UserRepository, get_user_repository
from app.schemas.common import ItemResponse, ListResponse, PageMeta
from app.schemas.user import UserRead

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("", response_model=ListResponse[UserRead], dependencies=[Depends(require_role(*Role))])
async def list_users(
    role: Role | None = None,
    team_id: str | None = None,
    repository: UserRepository = Depends(get_user_repository),
):
    filter_ = repository.build_filter(role=role, team_id=team_id)
    docs, total = await repository.list(filter_, page=1, page_size=100, sort_field="name", sort_direction=1)
    return ListResponse(data=docs, meta=PageMeta(page=1, page_size=100, total=total))


@router.get("/{user_id}", response_model=ItemResponse[UserRead], dependencies=[Depends(require_role(*Role))])
async def get_user(user_id: str, repository: UserRepository = Depends(get_user_repository)):
    doc = await repository.get(user_id)
    if not doc:
        raise NotFoundError(f"User {user_id} not found")
    return ItemResponse(data=doc)
