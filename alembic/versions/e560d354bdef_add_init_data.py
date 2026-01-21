"""Add init data

Revision ID: e560d354bdef
Revises: eeb66860687c
Create Date: 2026-01-21 22:25:08.928032

"""
import random
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'e560d354bdef'
down_revision: Union[str, Sequence[str], None] = 'eeb66860687c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Вставка начальных пользователей
    op.execute(
        text(
            "INSERT INTO users (email, password, first_name, last_name, is_active, created_at, role) VALUES "
            "('admin@example.com', '$2b$12$zXneSGKuiys5ax1Hup/2CeH5I.vOazuw/akeYKd7Qu2EC1UGrdm76', 'Admin', 'Admin', true, NOW(), 'ADMIN'), " # hashedPassword1
            "('user1@example.com', '$2b$12$zXneSGKuiys5ax1Hup/2CeH5I.vOazuw/akeYKd7Qu2EC1UGrdm76', 'John', 'Doe', true, NOW(), 'USER'), " # hashedPassword1
            "('user2@example.com', '$2b$12$D3EDr0tzT7OmuroDgYR4a.Asv9hulAFkfNNCYqhnUknBCWROrlroq', 'Jane', 'Smith', true, NOW(), 'USER'), " # hashedPassword2
            "('user3@example.com', '$2b$12$D3EDr0tzT7OmuroDgYR4a.Asv9hulAFkfNNCYqhnUknBCWROrlroq', 'Jane', 'Smith', true, NOW(), 'USER')" # hashedPassword2
        )
    )

    # Вставка 100 начальных задач
    USER_IDS = [1, 2, 3, 4]
    TASK_STATUSES = ['To Do', 'In Progress', 'Done', 'Cancelled']

    tasks = []
    for i in range(1, 101):
        assignee_id = random.choice(USER_IDS)
        status = random.choice(TASK_STATUSES)
        created_at = 'null'
        updated_at = 'null'
        closed_at = 'null'
        started_work_at = 'null'

        match status:
            case 'To Do':
                created_at = "NOW() - INTERVAL '5 DAY'"
                updated_at = "NOW() - INTERVAL '4 DAY'"
            case 'In Progress':
                created_at = "NOW() - INTERVAL '5 DAY'"
                updated_at = "NOW() - INTERVAL '2 DAY'"
                started_work_at = "NOW() - INTERVAL '2 DAY'"
            case 'Done':
                created_at = "NOW() - INTERVAL '5 DAY'"
                started_work_at = random.choice(["NOW() - INTERVAL '3 DAY'", "NOW() - INTERVAL '2 DAY'", "NOW() - INTERVAL '2 DAY'"])
                updated_at = "NOW()"
                closed_at = "NOW()"
            case 'Cancelled':
                created_at = "NOW() - INTERVAL '5 DAY'"
                updated_at = "NOW()"
                closed_at = "NOW()"

        tasks.append(f"('Test task {i}', 'Description for task {i}', {assignee_id}, '{status}', {created_at}, {updated_at}, {closed_at}, {started_work_at})")

    op.execute(
        text(
            f"INSERT INTO tasks (title, description, assignee_id, status, created_at, updated_at, closed_at, started_work_at) VALUES "
            + ', '.join(tasks)
        )
    )

def downgrade() -> None:
    """Downgrade schema."""
    # Удаление начальных задач
    op.execute("DELETE FROM tasks WHERE title LIKE 'Test task %'")

    # Удаление начальных пользователей
    op.execute("DELETE FROM users WHERE email IN ('user1@example.com', 'user2@example.com', 'user3@example.com', 'admin@example.com')")
