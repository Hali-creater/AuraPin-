import pandas as pd
import requests
from datetime import datetime
import random
import sqlite3
from PIL import Image
import io
import openai  # Optional, for AI-generated descriptions
import os
import uuid

# ==============================
# 1. DATABASE MODULE (Avoid Duplicates)
# ==============================
def init_database(db_file='pinterest_agent.db'):
    """Initializes a simple SQLite database to track posted products."""
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posted_products
                 (product_id TEXT PRIMARY KEY,
                  post_date TIMESTAMP,
                  pin_id TEXT)''')
    conn.commit()
    conn.close()

def is_product_posted(product_id, db_file='pinterest_agent.db'):
    """Checks if a product has already been posted to avoid duplicates."""
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT product_id FROM posted_products WHERE product_id=?", (product_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def mark_product_posted(product_id, pin_id, db_file='pinterest_agent.db'):
    """Marks a product as posted in the database."""
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("INSERT INTO posted_products (product_id, post_date, pin_id) VALUES (?, ?, ?)",
              (product_id, datetime.now(), pin_id))
    conn.commit()
    conn.close()

# ==============================
# 2. DATA FETCHING MODULE (AWIN)
# ==============================
def fetch_awin_product_feed(awin_feed_url):
    """Downloads and parses the AWIN product feed CSV/XML."""
    if not awin_feed_url or '...' in awin_feed_url:
        return pd.DataFrame(), "Please provide a valid AWIN Product Feed URL in the settings."
    try:
        response = requests.get(awin_feed_url)
        response.raise_for_status()
        # Use on_bad_lines to handle potential CSV errors. Also, try to guess the delimiter.
        try:
            df = pd.read_csv(io.StringIO(response.text), sep=',')
        except Exception:
             df = pd.read_csv(io.StringIO(response.text), sep='\t')

        # Basic cleaning - check for essential columns
        required_cols = ['product_name', 'awin_deep_link', 'product_image', 'description', 'price', 'product_id']
        if not all(col in df.columns for col in required_cols):
             return pd.DataFrame(), f"Feed is missing one of the required columns: {required_cols}"

        return df, f"Successfully fetched and parsed {len(df)} products from the feed."

    except requests.exceptions.RequestException as e:
        return pd.DataFrame(), f"Error fetching AWIN feed: {e}"
    except Exception as e:
        return pd.DataFrame(), f"An error occurred while parsing the feed: {e}. Check if it's a valid CSV."

# ==============================
# 3. CONTENT ENRICHMENT MODULE
# ==============================
def generate_pin_description(product_title, product_desc, price, use_openai, openai_api_key, disclaimer, hashtag_list):
    """Generates a unique and engaging description for the pin."""
    base_description = ""
    # OPTION B: AI-Generated (Sophisticated)
    if use_openai:
        if not openai_api_key or '...' in openai_api_key:
            return "OpenAI API key is missing. Please provide it in the settings.", False
        try:
            openai.api_key = openai_api_key
            prompt = f"Write a catchy, 2-sentence Pinterest description for a product called '{product_title}', described as '{product_desc[:100]}...'. It costs {price}. Frame it in a lifestyle context."
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            base_description = response.choices[0].message['content'].strip()
        except Exception as e:
            return f"Error with OpenAI: {e}. Falling back to template.", False

    # OPTION A: Template-based (Fallback)
    if not base_description:
        descriptions = [
            f"Loving this {product_title}! Perfect for my home. 🛍️",
            f"Just found this amazing {product_title}. What do you think?",
            f"Great deal alert! 🚨 {product_title} for only {price}!",
        ]
        base_description = random.choice(descriptions)

    # Add hashtags and disclaimer
    try:
        num_hashtags = min(len(hashtag_list), 3)
        selected_hashtags = ' '.join('#' + tag.strip() for tag in random.sample(hashtag_list, num_hashtags))
    except (ValueError, TypeError): # Handle empty or non-list hashtag_list
        selected_hashtags = ""

    final_description = f"{base_description}\n\n{selected_hashtags}\n{disclaimer}"

    return final_description, True

def download_and_format_image(image_url):
    """Downloads the product image, ensures it's optimized, and returns the image object."""
    try:
        # Create a temporary directory for images if it doesn't exist
        if not os.path.exists('temp_images'):
            os.makedirs('temp_images')

        response = requests.get(image_url)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content))

        # Convert to RGB if it's not
        if img.mode != 'RGB':
            img = img.convert('RGB')

        ideal_size = (1000, 1500)
        img.thumbnail(ideal_size, Image.Resampling.LANCZOS)

        # Save to a unique path
        save_path = os.path.join('temp_images', f"{uuid.uuid4()}.jpg")
        img.save(save_path, "JPEG", quality=85)

        return save_path, f"Image downloaded and formatted from {image_url}"
    except Exception as e:
        return None, f"Error processing image {image_url}: {e}"

# ==============================
# 4. PINTEREST API MODULE
# ==============================
def create_pin(pinterest_access_token, board_id, image_path, description, product_url, title="Awesome Product Find"):
    """Posts a pin to Pinterest using the official API."""
    if not pinterest_access_token or '...' in pinterest_access_token:
        return None, "Pinterest Access Token is missing. Please provide it in the settings."
    if not board_id or '...' in board_id:
        return None, "Pinterest Board ID is missing. Please provide it in the settings."

    # This is a placeholder. Pinterest API v5 requires a public URL for the image.
    # A local file path won't work. For a real application, you would need to
    # upload the processed image to a hosting service (e.g., AWS S3, Imgur)
    # and get a public URL before calling this function.

    # SIMULATING the API call for this Streamlit app
    print(f"--- SIMULATION: Pretending to post to Pinterest ---")
    print(f"Board ID: {board_id}")
    print(f"Product URL: {product_url}")
    print(f"Description: {description[:100]}...")
    print(f"Image Path: {image_path}")
    print(f"-------------------------------------------------")

    simulated_pin_id = f"simulated_{uuid.uuid4()}"
    return simulated_pin_id, f"Pin (simulated) created for {product_url} with Pin ID {simulated_pin_id}. NOTE: Real posting requires image hosting."