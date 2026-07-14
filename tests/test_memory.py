from app.memory import ConversationMemory


def test_memory_keeps_only_latest_turns():
    memory = ConversationMemory(window_size=2)

    memory.add_turn("Q1", "SQL1")
    memory.add_turn("Q2", "SQL2")
    memory.add_turn("Q3", "SQL3")

    history = memory.get_history()

    assert len(history) == 2
    assert history[0]["question"] == "Q2"
    assert history[1]["question"] == "Q3"


def test_clear_memory():
    memory = ConversationMemory(window_size=3)

    memory.add_turn("Q1", "SQL1")
    memory.clear()

    assert memory.get_history() == []