from app.db.models import TaskStatuses


TASK_STATUSES_MAPPING = {
    TaskStatuses.TO_DO: (TaskStatuses.IN_PROGRESS.value, TaskStatuses.CANCELLED.value),
    TaskStatuses.IN_PROGRESS: (TaskStatuses.DONE.value, TaskStatuses.CANCELLED.value),
    TaskStatuses.DONE: (),
    TaskStatuses.CANCELLED: (),
}
