from pypdf import PdfReader

# Importing your brilliant tools!
from rag_proccesor import RAGProcessor
from prompt import build_chef_prompt
from agent import check_inventory, client 

def run_chef_agent(user_request: str, processor: RAGProcessor):

    print("\n2. Checking the Fridge...")
    # [YOUR TURN 1: Call your imported function to get the inventory string]
    inventory_data = check_inventory()
    print(f"Found inventory: {inventory_data}")
    
    print("\n3. Finding Relevant Recipes...")

    augmented_query = f"{user_request} Ingredients available: {inventory_data}"
    # [YOUR TURN 2: Search the processor for the user's request (e.g., top_k=3)]
    recipe_chunks = processor.search(augmented_query, top_k=3)
    print(f"DEBUG - FAISS found these recipes: {recipe_chunks}")
    # We need to join the list of chunks into one massive string for the prompt
    recipe_data = "\n\n".join(recipe_chunks) 
    
    print("\n4. Building the Prompt...")
    # [YOUR TURN 3: Call your prompt builder with the 3 variables]
    final_prompt = build_chef_prompt(user_request, inventory_data, recipe_data)
    
    print("\n5. Asking Gemini...")
    # Because we injected everything into the text, we don't need function calling here!
    # We just do a standard text generation.
    response = client.models.generate_content(
        model='gemini-3.5-flash-lite', # Or whichever model version you prefer
        contents=final_prompt,
    )
    
    print("\n🍽️ CHEF SAYS:")
    return response.text

if __name__ == "__main__":
    test_request = "I am craving something with chicken. What can I make?"
    print(f"User Request: {test_request}")
    run_chef_agent(test_request)