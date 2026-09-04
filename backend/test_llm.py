from backend.llm import generate_response


def main():
    question = "Explain artificial intelligence in simple terms."

    print("\nUser:")
    print(question)

    response = generate_response(question)

    print("\nAI:")
    print(response)


if __name__ == "__main__":
    main()