import re

from tools.calculator import execute_calculator as calculator_tool
from tools.weather import weather


# ============================================================
# VALID ACTIONS
# ============================================================

VALID_ACTIONS = {
    "direct",
    "calculator",
    "weather",
    "search"
}


# ============================================================
# CALCULATOR KEYWORDS
# IMPORTANT:
# Do NOT put "what is" here.
# ============================================================

CALCULATOR_KEYWORDS = [
    "calculate",
    "calculator",
    "calculation",
    "compute",
    "solve",
    "plus",
    "minus",
    "multiply",
    "divide",
    "times",
    "multiplied by",
    "divided by"
]


# ============================================================
# WEATHER KEYWORDS
# ============================================================

WEATHER_KEYWORDS = [
    "weather",
    "temperature",
    "forecast",
    "rain",
    "raining",
    "humidity",
    "wind speed",
    "climate",
    "thunderstorm",
    "snow",
    "sunny",
    "cloudy"
]


# ============================================================
# SEARCH / LIVE INFORMATION KEYWORDS
# ============================================================

SEARCH_KEYWORDS = [
    "search",
    "google",
    "find online",
    "look up",
    "search online",
    "find on the internet",

    "latest",
    "latest news",
    "latest information",
    "latest update",
    "latest updates",

    "recent",
    "recently",
    "recent news",
    "recent information",
    "recent update",
    "recent updates",

    "current",
    "currently",
    "right now",
    "at present",

    "news",
    "breaking news",
    "news update",
    "news updates",

    "what happened",
    "what happened recently",
    "what is happening",
    "what's happening",
    "what is going on",
    "what's going on",

    "today",
    "today's",
    "todays",

    "yesterday",

    "this week",
    "this month",
    "this year",

    "latest version",
    "latest release",
    "new version",
    "new release"
]


# ============================================================
# CALCULATION DETECTION
# ============================================================

def is_calculation(message: str) -> bool:

    text = message.lower().strip()

    # --------------------------------------------------------
    # Keyword based calculation
    # --------------------------------------------------------

    if any(
        keyword in text
        for keyword in CALCULATOR_KEYWORDS
    ):
        return True

    # --------------------------------------------------------
    # Pure mathematical expressions
    #
    # Examples:
    # 25 * 8
    # 100 + 50
    # 20 / 5
    # 50 - 10
    # 10 % 3
    # --------------------------------------------------------

    if re.search(
        r"\d+(?:\.\d+)?\s*[\+\-\*\/%]\s*\d+(?:\.\d+)?",
        text
    ):
        return True

    return False


# ============================================================
# WEATHER DETECTION
# ============================================================

def is_weather_request(message: str) -> bool:

    text = message.lower().strip()

    return any(
        keyword in text
        for keyword in WEATHER_KEYWORDS
    )


# ============================================================
# SEARCH DETECTION
# ============================================================

def is_search_request(message: str) -> bool:

    text = message.lower().strip()

    return any(
        keyword in text
        for keyword in SEARCH_KEYWORDS
    )


# ============================================================
# EXTRACT WEATHER LOCATION
# ============================================================

def extract_weather_location(message: str):
    """
    Extract only the city/location from a weather question.

    Supported examples:

    What is the weather in Vijayawada?
        -> Vijayawada

    Current weather in Hyderabad
        -> Hyderabad

    What is the weather present in Vijayawada?
        -> Vijayawada

    What is the present weather in Vijayawada?
        -> Vijayawada

    What is the current weather in Hyderabad?
        -> Hyderabad

    What is the temperature of Delhi?
        -> Delhi

    Will it rain in Mumbai today?
        -> Mumbai

    Weather at Chennai
        -> Chennai

    Weather right now in Bengaluru
        -> Bengaluru

    What's the weather like in Mumbai?
        -> Mumbai
    """

    original = message.strip()

    # --------------------------------------------------------
    # Weather patterns
    # --------------------------------------------------------

    patterns = [

        # ----------------------------------------------------
        # WEATHER
        # ----------------------------------------------------

        r"\bweather\s+(?:in|at|for|of)\s+(.+)",

        # weather present in Vijayawada
        r"\bweather\s+(?:present|currently|current|now|right\s+now)\s+(?:in|at|for|of)\s+(.+)",

        # present weather in Vijayawada
        r"\b(?:present|current|currently)\s+weather\s+(?:in|at|for|of)\s+(.+)",

        # current weather of Vijayawada
        r"\bcurrent\s+weather\s+(?:in|at|for|of)\s+(.+)",

        # what's the weather like in Vijayawada
        r"\bweather\s+like\s+(?:in|at|for|of)\s+(.+)",

        # weather right now in Vijayawada
        r"\bweather\s+(?:right\s+now|currently|now)\s+(?:in|at|for|of)\s+(.+)",


        # ----------------------------------------------------
        # TEMPERATURE
        # ----------------------------------------------------

        r"\btemperature\s+(?:in|at|for|of)\s+(.+)",

        r"\bcurrent\s+temperature\s+(?:in|at|for|of)\s+(.+)",

        r"\btemperature\s+(?:right\s+now|currently|now)\s+(?:in|at|for|of)\s+(.+)",


        # ----------------------------------------------------
        # FORECAST
        # ----------------------------------------------------

        r"\bforecast\s+(?:in|at|for|of)\s+(.+)",


        # ----------------------------------------------------
        # RAIN
        # ----------------------------------------------------

        r"\brain(?:ing)?\s+(?:in|at|for)\s+(.+)",

        r"\bwill\s+it\s+rain\s+(?:in|at|for)\s+(.+)",


        # ----------------------------------------------------
        # HUMIDITY
        # ----------------------------------------------------

        r"\bhumidity\s+(?:in|at|for|of)\s+(.+)",


        # ----------------------------------------------------
        # WIND
        # ----------------------------------------------------

        r"\bwind\s+(?:in|at|for|of)\s+(.+)",


        # ----------------------------------------------------
        # CLIMATE
        # ----------------------------------------------------

        r"\bclimate\s+(?:in|at|for|of)\s+(.+)"
    ]


    # --------------------------------------------------------
    # Try all patterns
    # --------------------------------------------------------

    for pattern in patterns:

        match = re.search(
            pattern,
            original,
            flags=re.IGNORECASE
        )

        if match:

            city = match.group(1).strip()

            # ------------------------------------------------
            # Remove trailing time words
            # ------------------------------------------------

            city = re.sub(
                r"\s+(today|today's|todays|"
                r"now|right\s+now|currently|"
                r"at\s+present|present)$",
                "",
                city,
                flags=re.IGNORECASE
            )

            # ------------------------------------------------
            # Remove common question endings
            # ------------------------------------------------

            city = re.sub(
                r"\s+(today|tomorrow|tonight)\s*$",
                "",
                city,
                flags=re.IGNORECASE
            )

            # ------------------------------------------------
            # Remove punctuation
            # ------------------------------------------------

            city = city.rstrip(
                "?.!, "
            )

            # ------------------------------------------------
            # Final cleanup
            # ------------------------------------------------

            city = city.strip()

            if city:
                return city


    # ========================================================
    # FALLBACK WEATHER EXTRACTION
    # ========================================================
    #
    # Handles unusual sentences such as:
    #
    # "what is weather present in vijayawada"
    # "tell me weather currently in hyderabad"
    #
    # ========================================================

    fallback_patterns = [

        r"\bweather\b.*?\b(?:in|at|for|of)\s+([A-Za-z][A-Za-z\s\-]*)",

        r"\btemperature\b.*?\b(?:in|at|for|of)\s+([A-Za-z][A-Za-z\s\-]*)",

        r"\bforecast\b.*?\b(?:in|at|for|of)\s+([A-Za-z][A-Za-z\s\-]*)",

        r"\brain\b.*?\b(?:in|at|for)\s+([A-Za-z][A-Za-z\s\-]*)"
    ]


    for pattern in fallback_patterns:

        match = re.search(
            pattern,
            original,
            flags=re.IGNORECASE
        )

        if match:

            city = match.group(1).strip()

            city = re.sub(
                r"\s+(today|tomorrow|tonight|"
                r"now|currently|present|"
                r"right\s+now)$",
                "",
                city,
                flags=re.IGNORECASE
            )

            city = city.rstrip(
                "?.!, "
            )

            city = city.strip()

            if city:
                return city


    # --------------------------------------------------------
    # Nothing found
    # --------------------------------------------------------

    return None


# ============================================================
# LOCAL ROUTER
# ============================================================

def local_decision(message: str) -> str:

    # --------------------------------------------------------
    # 1. WEATHER FIRST
    #
    # Weather questions containing words such as:
    # current, today, now, present
    # must remain weather requests.
    # --------------------------------------------------------

    if is_weather_request(message):
        return "weather"


    # --------------------------------------------------------
    # 2. CALCULATOR
    # --------------------------------------------------------

    if is_calculation(message):
        return "calculator"


    # --------------------------------------------------------
    # 3. LIVE WEB SEARCH
    # --------------------------------------------------------

    if is_search_request(message):
        return "search"


    # --------------------------------------------------------
    # 4. NORMAL AI
    # --------------------------------------------------------

    return "direct"


# ============================================================
# MAIN DECISION
# ============================================================

def decide_action(message: str) -> str:

    action = local_decision(
        message
    )

    print(
        f"Agent local decision: {action}"
    )

    print(
        f"Final agent action: {action}"
    )

    return action


# ============================================================
# CALCULATOR
# ============================================================

def execute_calculation(message: str) -> str:

    expression = message.strip()

    # --------------------------------------------------------
    # Remove calculation-related words
    # --------------------------------------------------------

    expression = re.sub(
        r"\b(calculate|calculator|calculation|compute|solve)\b",
        "",
        expression,
        flags=re.IGNORECASE
    )


    # --------------------------------------------------------
    # Convert word operators
    # --------------------------------------------------------

    expression = re.sub(
        r"\bplus\b",
        "+",
        expression,
        flags=re.IGNORECASE
    )

    expression = re.sub(
        r"\bminus\b",
        "-",
        expression,
        flags=re.IGNORECASE
    )

    expression = re.sub(
        r"\b(times|multiply|multiplied by)\b",
        "*",
        expression,
        flags=re.IGNORECASE
    )

    expression = re.sub(
        r"\b(divided by|divide)\b",
        "/",
        expression,
        flags=re.IGNORECASE
    )


    expression = expression.strip(
        " ?."
    )


    # --------------------------------------------------------
    # Execute calculator
    # --------------------------------------------------------

    try:

        result = calculator_tool(
            expression
        )

        return str(result)

    except Exception as error:

        print(
            "Calculator error:",
            repr(error)
        )

        return (
            "Sorry, I couldn't calculate "
            "that expression. Please provide "
            "a valid mathematical expression."
        )


# ============================================================
# WEATHER
# ============================================================

def execute_weather(message: str) -> str:

    try:

        # ----------------------------------------------------
        # Extract city
        # ----------------------------------------------------

        city = extract_weather_location(
            message
        )


        # ----------------------------------------------------
        # If no city was mentioned
        # ----------------------------------------------------

        if not city:

            return (
                "🌤️ I can provide live weather information. "
                "Please mention the city, for example: "
                "\"What is the current weather in Vijayawada?\""
            )


        print(
            f"Weather location extracted: {city}"
        )


        # ----------------------------------------------------
        # Send ONLY the city to weather tool
        # ----------------------------------------------------

        result = weather(
            city
        )

        return str(result)


    except Exception as error:

        print(
            "Weather error:",
            repr(error)
        )

        return (
            "Sorry, I couldn't get the live weather "
            "information right now."
        )


# ============================================================
# GEMINI / OLLAMA
# ============================================================

def execute_direct(message: str) -> str:

    try:

        from backend.llm import generate_response

        result = generate_response(
            message
        )

        return str(result)

    except Exception as error:

        print(
            "Gemini/Ollama error:",
            repr(error)
        )

        return (
            "Sorry, I couldn't generate an AI "
            "response right now."
        )


# ============================================================
# LIVE WEB SEARCH
# ============================================================

def execute_search(message: str) -> str:

    try:

        from backend.llm import generate_search_response

        result = generate_search_response(
            message
        )

        return str(result)

    except Exception as error:

        print(
            "Search error:",
            repr(error)
        )

        return (
            "Sorry, I could not access live web "
            "information right now."
        )


# ============================================================
# RUN AGENT
# ============================================================

def run_agent(message: str) -> dict:

    message = message.strip()


    # --------------------------------------------------------
    # Empty message
    # --------------------------------------------------------

    if not message:

        return {
            "action": "direct",
            "response": "Please enter a message."
        }


    # --------------------------------------------------------
    # DECIDE ACTION
    # --------------------------------------------------------

    action = decide_action(
        message
    )


    print()
    print("=" * 60)
    print("INTELLIVOICE AI AGENT")
    print("=" * 60)

    print(
        f"User message: {message}"
    )

    print(
        f"Agent action: {action}"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # EXECUTE TOOL
    # --------------------------------------------------------

    if action == "calculator":

        response = execute_calculation(
            message
        )


    elif action == "weather":

        response = execute_weather(
            message
        )


    elif action == "search":

        response = execute_search(
            message
        )


    else:

        response = execute_direct(
            message
        )


    # --------------------------------------------------------
    # RETURN RESPONSE
    # --------------------------------------------------------

    return {
        "action": action,
        "response": response
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("INTELLIVOICE AI - AGENT TEST")
    print("=" * 60)


    test_messages = [

        # Normal AI
        "What is artificial intelligence?",

        "What is Python?",


        # Calculator
        "Calculate 25 * 8",

        "25 + 25",

        "100 divided by 5",


        # Weather
        "What is the weather in Vijayawada?",

        "What is the current weather in Vijayawada?",

        "What is weather present in Vijayawada?",

        "What is the present weather in Vijayawada?",

        "Current weather in Hyderabad",

        "What is the weather in Hyderabad today?",

        "What is the weather right now in Chennai?",

        "What's the weather like in Mumbai?",

        "What is the temperature of Delhi?",

        "Will it rain in Mumbai today?",


        # Live search
        "What happened recently in Nepal?",

        "What are the latest AI news?",

        "What is happening in India right now?",

        "What is the latest Python version?"
    ]


    for message in test_messages:

        print()
        print("-" * 60)

        print(
            f"User message: {message}"
        )


        action = decide_action(
            message
        )


        print(
            f"Selected action: {action}"
        )