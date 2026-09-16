import re


def calculate_expression(expression: str):
    """
    Safely calculate a basic mathematical expression.
    Supports +, -, *, /, %, ** and parentheses.
    """

    expression = expression.strip()

    # Allow only numbers and basic mathematical operators
    if not re.fullmatch(
        r"[0-9+\-*/%().\s]+",
        expression
    ):
        raise ValueError(
            "Invalid mathematical expression."
        )

    try:
        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return result

    except Exception as e:
        raise ValueError(
            "Unable to calculate the expression."
        ) from e


def execute_calculator(user_message: str) -> str:
    """
    Extract a mathematical expression from
    the user's message and calculate it.
    """

    message = user_message.lower().strip()

    prefixes = [
        "calculate",
        "what is",
        "what's",
        "compute",
        "solve"
    ]

    expression = message

    for prefix in prefixes:

        if expression.startswith(prefix):

            expression = expression[
                len(prefix):
            ].strip()

            break

    expression = expression.rstrip("?").strip()

    # Convert words into operators
    expression = expression.replace(
        " multiplied by ",
        "*"
    )

    expression = expression.replace(
        " times ",
        "*"
    )

    expression = expression.replace(
        " divided by ",
        "/"
    )

    expression = expression.replace(
        " plus ",
        "+"
    )

    expression = expression.replace(
        " minus ",
        "-"
    )

    expression = expression.replace(
        " percent ",
        "%"
    )

    try:

        result = calculate_expression(
            expression
        )

        if isinstance(result, float) and result.is_integer():
            result = int(result)

        return f"The answer is {result}."

    except Exception as e:

        print("=" * 60)
        print("CALCULATOR ERROR")
        print(f"Message    : {user_message}")
        print(f"Expression : {expression}")
        print(f"Error      : {repr(e)}")
        print("=" * 60)

        return (
            "Sorry, I could not calculate that. "
            "Please provide a valid mathematical expression."
        )