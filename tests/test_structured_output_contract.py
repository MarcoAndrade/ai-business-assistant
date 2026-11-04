from unittest.mock import patch

from app.ai.structured_output import extract_business_request
from app.ai.structured_schemas import BusinessRequest


def test_extract_business_request_returns_schema():
    with patch(
        "app.ai.structured_output.structured_llm"
    ) as mock_llm:

        mock_llm.invoke.return_value = BusinessRequest(
            intent="inventory_query",
            items=[],
            missing_information=[],
        )

        result = extract_business_request(
            "Consulta el inventario"
        )

        assert isinstance(result, BusinessRequest)
        assert result.intent == "inventory_query"