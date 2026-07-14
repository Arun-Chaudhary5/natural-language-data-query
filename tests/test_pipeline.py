from app.pipeline import TextToSQLPipeline


class FakeSQLGenerator:
    def __init__(self, sql):
        self.sql = sql

    def generate(self, question, history):
        return self.sql


def test_pipeline_success():
    pipeline = TextToSQLPipeline()

    pipeline.generator = FakeSQLGenerator(
        "SELECT * FROM customers WHERE city = 'Delhi';"
    )

    output = pipeline.run(
        "Show customers from Delhi."
    )

    assert output["success"] is True
    assert output["error"] is None
    assert output["result"]["row_count"] == 2

    assert len(pipeline.memory.get_history()) == 1


def test_pipeline_validation_failure():
    pipeline = TextToSQLPipeline(max_retries=0)

    pipeline.generator = FakeSQLGenerator(
        "DELETE FROM customers;"
    )

    output = pipeline.run(
        "Delete all customers."
    )

    assert output["success"] is False
    assert output["result"] is None

    # Failed turns must not enter conversation memory.
    assert pipeline.memory.get_history() == []

class FakeCorrectingSQLGenerator:
    def __init__(self):
        self.correction_calls = 0

    def generate(self, question, history):
        return "SELECT * FROM nonexistent_table;"

    def correct(
        self,
        question,
        previous_sql,
        error,
        history,
    ):
        self.correction_calls += 1

        return "SELECT * FROM customers WHERE city = 'Delhi';"


def test_pipeline_corrects_failed_sql():
    pipeline = TextToSQLPipeline(max_retries=1)

    fake_generator = FakeCorrectingSQLGenerator()
    pipeline.generator = fake_generator

    output = pipeline.run(
        "Show customers from Delhi."
    )

    assert output["success"] is True
    assert output["retries"] == 1
    assert output["result"]["row_count"] == 2
    assert fake_generator.correction_calls == 1

    assert len(pipeline.memory.get_history()) == 1