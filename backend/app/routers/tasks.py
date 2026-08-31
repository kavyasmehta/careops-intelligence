from fastapi import APIRouter, Depends

from app.core.roles import Role, get_current_user_name, require_role
from app.models.task import TaskStatus
from app.repositories.tasks import TaskRepository, get_task_repository
from app.schemas.common import ItemResponse, ListParams, ListResponse, PageMeta
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.tasks import TaskService

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


def get_task_service(repository: TaskRepository = Depends(get_task_repository)) -> TaskService:
    return TaskService(repository)


@router.get("", response_model=ListResponse[TaskRead], dependencies=[Depends(require_role(*Role))])
async def list_tasks(
    client_id: str | None = None,
    status: TaskStatus | None = None,
    assigned_employee_id: str | None = None,
    params: ListParams = Depends(),
    service: TaskService = Depends(get_task_service),
):
    docs, total = await service.list(
        client_id=client_id, status=status, assigned_employee_id=assigned_employee_id,
        page=params.page, page_size=params.page_size, sort_field=params.sort_field, sort_direction=params.sort_direction,
    )
    return ListResponse(data=docs, meta=PageMeta(page=params.page, page_size=params.page_size, total=total))


@router.get("/{task_id}", response_model=ItemResponse[TaskRead], dependencies=[Depends(require_role(*Role))])
async def get_task(task_id: str, service: TaskService = Depends(get_task_service)):
    return ItemResponse(data=await service.get(task_id))


@router.post(
    "", response_model=ItemResponse[TaskRead], status_code=201,
    dependencies=[Depends(require_role(Role.OPERATIONS_MANAGER))],
)
async def create_task(
    payload: TaskCreate,
    user: str = Depends(get_current_user_name),
    service: TaskService = Depends(get_task_service),
):
    return ItemResponse(data=await service.create(payload, user=user))


@router.patch("/{task_id}", response_model=ItemResponse[TaskRead], dependencies=[Depends(require_role(*Role))])
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    user: str = Depends(get_current_user_name),
    service: TaskService = Depends(get_task_service),
):
    return ItemResponse(data=await service.update(task_id, payload, user=user))
