import pytest

from app.schemas.analytics import MarketAnalysisRequest
from app.services import analytics
from app.services.analytics import AnalyticsService, format_ticker_symbol


def test_format_ticker_symbol():
    assert format_ticker_symbol("reliance") == "RELIANCE.NS"
    assert format_ticker_symbol("usdinr") == "USDINR=X"
    assert format_ticker_symbol("aapl") == "AAPL"


@pytest.mark.asyncio
async def test_prediction_uses_requested_timeframe(monkeypatch):
    service = AnalyticsService()

    def unavailable_market_data(*_args, **_kwargs):
        raise ValueError("market data unavailable")

    monkeypatch.setattr(analytics, "fetch_stock_data", unavailable_market_data)
    response = await service.predict_trend(MarketAnalysisRequest(ticker="AAPL", timeframe_days=90))

    assert response.status == "error"
    assert response.timeframe_days == 90
