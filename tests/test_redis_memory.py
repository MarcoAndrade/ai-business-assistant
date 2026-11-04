import os
import uuid

import pytest

from dotenv import load_dotenv
from langgraph.checkpoint.redis import RedisSaver
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

load_dotenv()

class MemoryState(TypedDict, total=False):
    user_message: str
    history: list[str]


def echo_node(state: MemoryState) -> dict:
    history = state.get("history", [])

    return {
        "history": history + [state["user_message"]]
    }


def build_test_graph(checkpointer):
    builder = StateGraph(MemoryState)

    builder.add_node("echo", echo_node)
    builder.add_edge(START, "echo")
    builder.add_edge("echo", END)

    return builder.compile(checkpointer=checkpointer)


@pytest.mark.integration
def test_redis_checkpoint_persists_between_invocations():
    redis_url = os.getenv("REDIS_URL")

    if not redis_url:
        pytest.skip("REDIS_URL no está configurado")

    thread_id = f"test-{uuid.uuid4()}"

    with RedisSaver.from_conn_string(redis_url) as saver:
        saver.setup()
        graph = build_test_graph(saver)

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        first = graph.invoke(
            {
                "user_message": "primer mensaje",
                "history": [],
            },
            config,
        )

        assert first["history"] == ["primer mensaje"]

        second = graph.invoke(
            {"user_message": "segundo mensaje"},
            config,
        )

        assert second["history"] == [
            "primer mensaje",
            "segundo mensaje",
        ]


def test_different_threads_do_not_share_history():
    redis_url = os.getenv("REDIS_URL")

    if not redis_url:
        pytest.skip("REDIS_URL no está configurado")

    with RedisSaver.from_conn_string(redis_url) as saver:
        saver.setup()
        graph = build_test_graph(saver)

        config_a = {
            "configurable": {
                "thread_id": f"user-a-{uuid.uuid4()}"
            }
        }

        config_b = {
            "configurable": {
                "thread_id": f"user-b-{uuid.uuid4()}"
            }
        }

        graph.invoke(
            {
                "user_message": "mensaje privado A",
                "history": [],
            },
            config_a,
        )

        result_b = graph.invoke(
            {
                "user_message": "mensaje privado B",
                "history": [],
            },
            config_b,
        )

        assert result_b["history"] == ["mensaje privado B"]
