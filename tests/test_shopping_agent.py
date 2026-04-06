import pytest
from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from src.tools.shopping_tools import search_products, get_discount, calc_final_price


class TestShoppingTools:
    """Test shopping tools."""
    
    def test_search_products_no_filter(self):
        """Search without price filter."""
        result = search_products("tai nghe")
        assert len(result) > 0
        assert "name" in result[0]
        assert "price" in result[0]
    
    def test_search_products_with_budget(self):
        """Search with max_price filter."""
        result = search_products("tai nghe", max_price=2000000)
        for product in result:
            if "price" in product:
                assert product["price"] <= 2000000
    
    def test_get_discount_valid(self):
        """Test valid discount code."""
        result = get_discount("FIRST20")
        assert result["valid"] is True
        assert result["value"] == 20
        assert result["type"] == "percent"
    
    def test_get_discount_invalid(self):
        """Test invalid discount code."""
        result = get_discount("INVALID")
        assert result["valid"] is False
        assert "error" in result
    
    def test_calc_final_price_percent_discount(self):
        """Test percentage discount calculation."""
        result = calc_final_price(1000000, discount_percent=20)
        assert result["final_price_per_unit"] == 800000
        assert result["total_savings"] == 200000
    
    def test_calc_final_price_fixed_discount(self):
        """Test fixed amount discount."""
        result = calc_final_price(1000000, discount_fixed=100000)
        assert result["final_price_per_unit"] == 900000
    
    def test_calc_final_price_quantity(self):
        """Test with quantity."""
        result = calc_final_price(1000000, discount_percent=10, quantity=2)
        assert result["total_final_price"] == 1800000  # 900000 * 2


class TestReActAgent:
    """Test ReAct Agent."""
    
    @pytest.fixture
    def agent(self):
        llm = GeminiProvider()
        return ReActAgent(llm=llm, max_steps=5)
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.max_steps == 5
        assert agent.llm is not None
    
    def test_system_prompt(self, agent):
        """Test system prompt contains tool info."""
        prompt = agent.get_system_prompt()
        assert "search_products" in prompt
        assert "get_discount" in prompt
        assert "calc_final_price" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])