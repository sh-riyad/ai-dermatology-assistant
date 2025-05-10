from langgraph.checkpoint.postgres import PostgresSaver
from app.core.config import settings


from psycopg_pool import ConnectionPool

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

pool = ConnectionPool(
    conninfo=settings.DATABASE_URL,
    min_size=1,  # Ensure at least one connection is available
    max_size=10, # Prevent connection exhaustion
    kwargs=connection_kwargs,
)

checkpointer = PostgresSaver(pool)
checkpointer.setup()
