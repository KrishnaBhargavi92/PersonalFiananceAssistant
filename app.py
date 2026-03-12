from agent import personalFinanaceAssistant

def main():

    while True:
        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Assistant: Goodbye!")
            break

        response = personalFinanaceAssistant(user_input)
        print("Assistant:", response)

if __name__ == "__main__":
    main()