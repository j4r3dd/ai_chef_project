import os 
import firebase_admin
from firebase_admin import credentials, firestore
from google import genai
from google.genai import types
from dotenv import load_dotenv
from google.cloud.firestore_v1.base_query import FieldFilter

load_dotenv()

#1 firebase setup

cred = credentials.Certificate("chef-project-4fd61-firebase-adminsdk-fbsvc-c88f2e7584.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

client = genai.Client()

#3 the function tool 
def update_inventory(action: str, item: str, quantity: float, unit: str) -> str:

    """
    Updates the kitchen inventory database.
    
    Args:
        action: Either "add" (bought new food) or "remove" (used food).
        item: The name of the food ingredient (singular form, e.g., "apple", "chicken").
        quantity: The amount of the item.
        unit: The unit of measurement (e.g., "kg", "grams", "liters", "pieces").
    """
    
    # 1. Define the references FIRST
    collection_ref = db.collection("inventory")
    doc_ref = collection_ref.document(item)


    # 2. Fetch the document from Firestore
    doc_snapshot = doc_ref.get()

    # 3. Check if it exists and calculate the new quantity
    if doc_snapshot.exists:
        # The item is already in the database!
        doc_data = doc_snapshot.to_dict()
        current_quantity = doc_data.get("quantity", 0)

        if action == "add":
            current_quantity = current_quantity + quantity
        elif action == "remove":
            current_quantity = current_quantity - quantity

    else:
        # The item is NOT in the database yet.
        print(f"Adding {item} for the first time!")
        current_quantity = quantity

        # (Bonus question for you to think about: What should happen if the action is "remove" but the item doesn't exist?)

    # 4. Finally, save the data back to Firestore
    # Remember: Firestore needs a dictionary!
    doc_ref.set({
        "quantity": current_quantity,
        "unit": unit
    })

    return f"Database updated: {action} {quantity} {unit} of {item}."

def check_inventory() -> str:
    """Returns a list of all ingredients currently available in the kitchen."""
    docs = (
    db.collection("inventory")
    .where(filter=FieldFilter("quantity", ">=", 0))
    .stream()
    )
    inventory_list = []

    for doc in docs:
        item_name = doc.id
        item_data = doc.to_dict()
        quantity = item_data.get("quantity", 0)
        unit = item_data.get("unit", "")
        formatted_string = f"{item_name}: {quantity} {unit}"
        inventory_list.append(formatted_string)

    if not inventory_list:
        return "The fridge is completly empty"
    return ", ".join(inventory_list)

        

    





def process_inventory_message(user_text: str):

    chat = client.chats.create(
        model='gemini-3.5-flash-lite',
        config=types.GenerateContentConfig(
            tools=[update_inventory, check_inventory]
        )
    )
    try:
        response = chat.send_message(user_text)
        return response.text
    except Exception as e:
        return (f"Agent Reply: Sorry, my AI brain is currently overloaded! Please try again in a minute. (Error: {e})")

if __name__ == "__main__":
    # Let's test it!
    test_message = """Here is what I managed to load up on for the month
        * Black Beans 20 kg total 
        * White Rice: 10 kg 
        * Vegetable Oil: 3 large jugs (5L each)
        * Eggs: 360 eggs total, let's hope nothing breaks!
        * Milk: 12 cartons of UHT milk 
        * Corn Tortillas: 4 kg 
        * Chicken: 15 kg total
        * Produce: 5 Tomatoes, 4 onions, 5 chiles, 5 potatoes, and 10 limes """


    print(f"Testing with: {test_message}")
    process_inventory_message(test_message)
