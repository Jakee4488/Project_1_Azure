from langchain_core.prompts.chat import ChatPromptTemplate

def create_chat_prompt(user_query, relevant_context):
        return [
        # Define the chat prompt template
        ChatPromptTemplate.from_messages
        (
                
        [{"role": "system", "content": "You are an AI assistant that helps people find information efficiently."},
        {"role": "user", "content": f"{user_query} {relevant_context[0]}"}]

        )
        
        ]
