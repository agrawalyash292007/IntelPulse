from nltk.sentiment.vader import SentimentIntensityAnalyzer
import yfinance as yf


def get_news_sentiment(ticker: str) -> float:
    """
    Fetches recent news headlines for a ticker using yfinance
    and computes a normalized sentiment score between -1.0 and +1.0.
    """
    try:
        stock = yf.Ticker(ticker)
        news_items = stock.news
        
        if not news_items:
            return 0.0  # Neutral if no news found

        sia = SentimentIntensityAnalyzer()
        scores = []

        for item in news_items[:10]:  # Analyze up to 10 recent headlines
            title = item.get("title", "")
            if title:
                sentiment = sia.polarity_scores(title)
                scores.append(sentiment["compound"])

        if not scores:
            return 0.0

        return float(sum(scores) / len(scores))
    except Exception:
        return 0.0  # Fallback to neutral on network/API failure
