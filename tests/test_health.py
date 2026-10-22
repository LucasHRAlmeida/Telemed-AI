from backend.app.api.routes import health
from backend.app.config import EMBEDDING_MODEL, LLM_MODEL


def test_health_reports_application_status():
    response = health()

    assert response.status == "ok"
    assert response.llm_model == LLM_MODEL
    assert response.embedding_model == EMBEDDING_MODEL
    assert isinstance(response.graph_loaded, bool)
    assert isinstance(response.vector_store_loaded, bool)
