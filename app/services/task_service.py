"""
app/services/task_service.py — Business logic for task management and assignment.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.team import ProjectTeam, TeamMember
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate


class TaskService:
    @staticmethod
    async def create_task(
        project_id: UUID,
        data: TaskCreate,
        current_user: User,
        db: AsyncSession,
    ) -> TaskOut:
        """Create a new task within a project and assign it to a team member."""
        # 1. Verify project exists
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id={project_id} not found.",
            )

        # 2. Verify assigned_to user is a member of that project's team
        member_stmt = (
            select(TeamMember.user_id)
            .join(ProjectTeam, ProjectTeam.team_id == TeamMember.team_id)
            .where(
                ProjectTeam.project_id == project_id,
                TeamMember.user_id == data.assigned_to,
            )
        )
        member_result = await db.execute(member_stmt)
        if not member_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with id={data.assigned_to} is not a member of any team assigned to project {project_id}.",
            )

        # 3. Create task with default status and priority
        task_priority = data.priority if data.priority is not None else TaskPriority.Medium

        task = Task(
            title=data.title,
            description=data.description,
            status=TaskStatus.Todo,
            priority=task_priority,
            project_id=project_id,
            assigned_to=data.assigned_to,
            assigned_by=current_user.id,
            deadline=data.deadline,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)

        return TaskOut.model_validate(task)

    @staticmethod
    async def get_all_tasks(
        project_id: UUID,
        db: AsyncSession,
    ) -> List[TaskOut]:
        """Fetch all tasks for a project ordered by created_at descending."""
        # 1. Verify project exists
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id={project_id} not found.",
            )

        # 2. Query tasks ordered by created_at desc
        result = await db.execute(
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(Task.created_at.desc())
        )
        tasks = result.scalars().all()
        return [TaskOut.model_validate(t) for t in tasks]

    @staticmethod
    async def get_task_by_id(
        project_id: UUID,
        task_id: UUID,
        db: AsyncSession,
    ) -> TaskOut:
        """Fetch a single task by ID within a project."""
        # 1. Verify project exists
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id={project_id} not found.",
            )

        # 2. Query specific task
        result = await db.execute(
            select(Task).where(
                Task.task_id == task_id,
                Task.project_id == project_id,
            )
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id={task_id} not found in project {project_id}.",
            )

        return TaskOut.model_validate(task)

    @staticmethod
    async def update_task(
        project_id: UUID,
        task_id: UUID,
        data: TaskUpdate,
        db: AsyncSession,
        current_user: Optional[User] = None,
    ) -> TaskOut:
        """Update an existing task in a project using PATCH semantics."""
        _ = current_user

        # 1. Verify project exists
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id={project_id} not found.",
            )

        # 2. Verify task exists in that project
        result = await db.execute(
            select(Task).where(
                Task.task_id == task_id,
                Task.project_id == project_id,
            )
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id={task_id} not found in project {project_id}.",
            )

        # 3. Filter explicitly sent fields
        update_data = data.model_dump(exclude_unset=True)

        # Ensure project_id and assigned_by are never updatable
        update_data.pop("project_id", None)
        update_data.pop("assigned_by", None)
        update_data.pop("task_id", None)
        update_data.pop("created_at", None)
        update_data.pop("updated_at", None)

        # 4. If assigned_to is being updated, verify new user is still a member of the project team
        if "assigned_to" in update_data and update_data["assigned_to"] is not None:
            new_assigned_to = update_data["assigned_to"]
            member_stmt = (
                select(TeamMember.user_id)
                .join(ProjectTeam, ProjectTeam.team_id == TeamMember.team_id)
                .where(
                    ProjectTeam.project_id == project_id,
                    TeamMember.user_id == new_assigned_to,
                )
            )
            member_result = await db.execute(member_stmt)
            if not member_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with id={new_assigned_to} is not a member of any team assigned to project {project_id}.",
                )

        # 5. Apply only explicitly sent fields
        for field, value in update_data.items():
            setattr(task, field, value)

        await db.commit()
        await db.refresh(task)

        return TaskOut.model_validate(task)


# Module-level aliases
create_task = TaskService.create_task
get_all_tasks = TaskService.get_all_tasks
get_task_by_id = TaskService.get_task_by_id
update_task = TaskService.update_task
