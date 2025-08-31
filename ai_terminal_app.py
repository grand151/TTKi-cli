import openai

def chat_with_ai(prompt):
    openai.api_key = "YOUR_OPENAI_API_KEY" # This will be replaced by the actual key from environment variables
    openai.api_base = "YOUR_OPENAI_API_BASE" # This will be replaced by the actual base from environment variables
    try:
        response = openai.chat.completions.create(
            model="Qwen/Qwen3-Coder-480B-A35B",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    print("AI Terminal Chatbot (Type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        ai_response = chat_with_ai(user_input)
        print(f"AI: {ai_response}")


