from app.ai.tools import AI_TOOLS


def test_ai_tools_are_registered():
    names = {tool.name for tool in AI_TOOLS}

    assert "get_product" in names
    assert "get_low_stock_products" in names
    assert "get_daily_sales" in names
    assert "register_sale" in names