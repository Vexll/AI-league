from main import EmergencyReportingBot


def main():
    print("🚨 Welcome to Emergency Reporting Bot (type 'exit' to quit) 🚨")
    bot = EmergencyReportingBot()
    conversation_history = []

    while True:
        user_message = input("👤 You: ").strip()
        if user_message.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        result = bot.process_message(
            user_message, conversation_history=conversation_history
        )

        # Update conversation history for context
        conversation_history = result["conversation"]

        print(f"🤖 Bot: {result['response']}")
        print("📝 Report saved at:", result["report_path"])
        print("-" * 50)


if __name__ == "__main__":
    main()
