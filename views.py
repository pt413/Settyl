import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Initialize Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

# Function for sentiment analysis
def sentiment_analysis(user_input):
    sentiment = analyzer.polarity_scores(user_input)
    return sentiment['compound']

# Combined negotiation logic with sentiment analysis
def negotiation_logic(user_input):
    base_price = 3700
    min_price = 3500
    sentiment_score = sentiment_analysis(user_input)

    # Process user response
    if "hi" in user_input.lower():
        return f"Hello...you can now start negotiating with me"

    if "accept" in user_input.lower():
        return f"Great! You've accepted the price of ${base_price}."

    elif "reject" in user_input.lower():
        return "Sorry to hear that. Maybe we can negotiate another time."
    
    elif "offer" in user_input:
        user_price = int(''.join([i for i in user_input if i.isdigit()]))

        if sentiment_score > 0.5:
            return f"You seem polite! I'll accept ${user_price}."
        elif user_price >= base_price or (user_price>=min_price and user_price<=base_price):
            return f"I'll accept your offer of ${user_price}."
        elif user_price < min_price:
            return f"Sorry, I can't go below ${min_price}. How about ${min_price}?"
        else:
            res=user_price+10
            return f"Except my offer at ${res if res<150 else 150}?"

# Use Gemini API for response
def get_gemini_response(user_input):

    url = "https://api.gemini.com/v1beta/model"
    headers = {
        "Authorization": "Bearer --(your API key)--",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": user_input,
        "parameters":{
            "maxTokens": 150,
            "temperature": 0.7
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json().get("response")
    else:
        return "Sorry, I couldn't process your request."


# Handle POST requests for chatbot interaction
@csrf_exempt
def negotiate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('message', '')  # User's input message

        if not user_input:
            base_price = 3700
            initial_message = f"The starting price for the product is ${base_price}. What is your offer?"
            return JsonResponse({'response': initial_message})

        # Determine if we should use ChatGPT or negotiation logic
        if any(keyword in user_input.lower() for keyword in ["offer", "accept", "reject","hi"]):
            # Use negotiation logic
            negotiation_reply = negotiation_logic(user_input)
            return JsonResponse({'response': negotiation_reply})
        else:
            # Use ChatGPT for general conversation
            g_reply = get_gemini_response(user_input)
            return JsonResponse({'response': g_reply})

    return JsonResponse({'error': 'Invalid request method'}, status=400)