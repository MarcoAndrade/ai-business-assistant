import os
from contextlib import contextmanager

from dotenv import load_dotenv
from langgraph.checkpoint.redis import RedisSaver

from app.ai.graph import build_graph

load_dotenv()

@contextmanager
def open_memory_graph():
    redis_url = os.getenv("REDIS_URL")

    if not redis_url:
        raise RuntimeError("Falta la variable REDIS_URL.")

    with RedisSaver.from_conn_string(
        redis_url,
        ttl={
            "default_ttl": 1440,
            "refresh_on_read": True,
        },
    ) as checkpointer:
        checkpointer.setup()
        graph = build_graph(checkpointer=checkpointer)
        yield graph
