from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    if not text.strip():
        return 0.0
    scores = analyzer.polarity_scores(text)
    return scores['compound']

def calculate_stress(sleep, workload, energy, mood, sentiment):
    sleep_score = (10 - sleep) / 10
    workload_score = workload / 10
    energy_score = (10 - energy) / 10
    mood_score = (10 - mood) / 10
    sentiment_score = (1 - ((sentiment + 1) / 2))

    stress = (0.25 * sleep_score +
              0.30 * workload_score +
              0.15 * energy_score +
              0.10 * mood_score +
              0.20 * sentiment_score)

    return round(stress, 2)