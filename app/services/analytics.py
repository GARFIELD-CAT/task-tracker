import pandas as pd
from sqlalchemy import func, select

from app.db.models import User, Task, TaskStatuses
from app.services.main_service import MainService


class AnalyticsService(MainService):
    async def get_visualization_data(self):
        session = self._get_async_session()

        query = (
            select(
                User.first_name.label("first_name"),
                User.last_name.label("last_name"),
                Task.status.label("status"),
                func.count(Task.id).label("count")
            ).join(User, Task.assignee_id == User.id)
            .group_by(User.id, Task.status)
        )

        async with session() as db_session:
            result = await db_session.execute(query)

        visualization_data = result.all()

        if not visualization_data:
            return None

        df_vis = pd.DataFrame(visualization_data)
        df_vis['full_name'] = df_vis['first_name'] + ' ' + df_vis['last_name']

        pivot_df = df_vis.pivot(index='full_name', columns='status',
                                values='count').fillna(0)

        column_order = [TaskStatuses.TO_DO.value,
                        TaskStatuses.IN_PROGRESS.value,
                        TaskStatuses.DONE.value, TaskStatuses.CANCELLED.value]
        ordered_cols = [col for col in column_order if col in pivot_df.columns]
        pivot_df = pivot_df[ordered_cols]

        import plotly.express as px

        fig = px.bar(
            pivot_df,
            x=pivot_df.index,
            y=pivot_df.columns,
            title="Распределение задач по исполнителям и статусам",
            labels={'full_name': 'Исполнитель', 'value': 'Количество задач',
                    'status': 'Статус'},
            color_discrete_map={
                TaskStatuses.TO_DO.value: '#FFD700',
                TaskStatuses.IN_PROGRESS.value: '#1E90FF',
                TaskStatuses.DONE.value: '#3CB371',
                TaskStatuses.CANCELLED.value: '#DC143C'
            }
        )

        fig.update_layout(
            barmode='stack',
            xaxis_title="Исполнитель",
            yaxis_title="Количество задач"
        )

        graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

        html_template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Отчет по задачам</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    .container {{ max-width: 1000px; margin: auto; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Аналитика</h1>
                    {graph_html}
                    <hr>
                </div>
            </body>
            </html>
        """

        return html_template


analytics_service = AnalyticsService()