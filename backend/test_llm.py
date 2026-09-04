from backend.llm import generate_response


def main():
    question = "Explain artificial intelligence in simple terms."

    print("\nUser:")
    print(question)

    print("\nAI:")
    
    response = generate_response(question)

    print(response)


if __name__ == "__main__":
    main()