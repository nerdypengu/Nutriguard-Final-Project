import json
import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import core and services
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.supabase import supabase_service_client, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
from services.embeddings import generate_embedding

# Debug: Check if credentials are loaded
if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("ERROR: Supabase credentials not loaded from .env file!")
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_SERVICE_ROLE_KEY: {'loaded' if SUPABASE_SERVICE_ROLE_KEY else 'NOT LOADED'}")
    sys.exit(1)

async def verify_connection():
    """Verify connection to Supabase and the RPC function"""
    try:
        print("Verifying connection to Supabase...")
        
        # Try calling the RPC function with an empty array to verify it exists
        response = supabase_service_client.rpc("insert_food_items", {"items": []}).execute()
        
        print("✓ Successfully connected to Supabase")
        print("✓ RPC function 'insert_food_items' is accessible")
        return True
        
    except Exception as e:
        print(f"✗ Failed to connect to Supabase or access RPC function")
        print(f"Error: {e}")
        return False

async def import_gizi_json():
    """Import food data from gizi.json to Supabase food_items table"""
    
    # Verify connection first
    if not await verify_connection():
        print("Aborting import due to connection failure")
        return
    
    # Load the gizi.json file
    gizi_path = Path(__file__).parent.parent.parent / "gizi.json"
    
    with open(gizi_path, 'r', encoding='utf-8') as f:
        food_data = json.load(f)
    
    print(f"Found {len(food_data)} food items to import")
    
    food_items_to_insert = []
    
    for item in food_data:
        try:
            # Map fields from gizi.json to food_items schema
            food_item = {
                "name": item.get("nama"),
                "calories": float(item.get("energi", 0)),
                "protein": float(item.get("protein", 0)),
                "fat": float(item.get("lemak", 0)),
                "carbs": float(item.get("karbohidrat", 0)),
                "base_serving_size": "100g",
                "is_user_contributed": False,
            }
            
            # Generate embedding for semantic search
            food_item["embedding"] = generate_embedding(food_item["name"])
            
            food_items_to_insert.append(food_item)
            
        except Exception as e:
            print(f"Error processing item {item.get('nama')}: {e}")
    
    # Insert in batches to avoid timeout
    batch_size = 100
    for i in range(0, len(food_items_to_insert), batch_size):
        batch = food_items_to_insert[i:i + batch_size]
        try:
            response = supabase_service_client.rpc("insert_food_items", {"items": batch}).execute()
            print(f"Inserted batch {i // batch_size + 1}: Success")
        except Exception as e:
            print(f"Error inserting batch {i // batch_size + 1}: {e}")
    
    print(f"\nImport complete! Total items inserted: {len(food_items_to_insert)}")

if __name__ == "__main__":
    asyncio.run(import_gizi_json())
