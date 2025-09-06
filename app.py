import streamlit as st
import pandas as pd
import agent_core
import random

# --- App State Management ---
# Using session_state to hold generated pins before they are posted
if 'pins_to_review' not in st.session_state:
    st.session_state.pins_to_review = []
if 'logs' not in st.session_state:
    st.session_state.logs = []

def add_log(message):
    """Adds a message to the log display."""
    st.session_state.logs.insert(0, message)

# --- UI Layout ---
st.set_page_config(layout="wide")
st.title("📌 Pinterest Affiliate Curator & Scheduler")

# --- Sidebar for Settings ---
with st.sidebar:
    st.header("⚙️ Settings & Configuration")

    st.subheader("API Credentials")
    awin_feed_url = st.text_input("AWIN Product Feed URL", "https://productdata.awin.com/datafeed/download/apikey/...")
    pinterest_access_token = st.text_input("Pinterest Access Token", "your_pinterest_access_token", type="password")
    openai_api_key = st.text_input("OpenAI API Key (Optional)", "your_openai_key", type="password")

    st.subheader("Content Settings")
    pinterest_board_id = st.text_input("Pinterest Board ID", "your_board_id_here")
    disclaimer = st.text_area("Affiliate Disclaimer", "#Ad #CommissionsEarned")
    hashtags_str = st.text_area("Hashtag Pool (comma-separated)", "HomeDecor, InteriorDesign, DreamHome, HomeInspo, AffiliateMarketing")

    st.subheader("Behavior Settings")
    max_pins_per_run = st.number_input("Max Products to Process per Run", min_value=1, max_value=20, value=5)
    use_openai = st.checkbox("Use OpenAI for Pin Descriptions", value=True)

# --- Main App Body ---
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🚀 Step 1: Generate Pins for Review")

    if st.button("Fetch Products & Generate Pins"):
        add_log("Starting agent...")
        st.session_state.pins_to_review = [] # Clear previous pins

        # 1. Initialize Database
        with st.spinner("Initializing database..."):
            agent_core.init_database()
            add_log("Database initialized.")

        # 2. Fetch AWIN Data
        with st.spinner("Fetching product data from AWIN..."):
            hashtag_list = [h.strip() for h in hashtags_str.split(',')]
            products_df, message = agent_core.fetch_awin_product_feed(awin_feed_url)
            add_log(message)

        if not products_df.empty:
            # 3. Filter out already posted products
            unposted_products = []
            for index, product in products_df.iterrows():
                if not agent_core.is_product_posted(str(product['product_id'])):
                    unposted_products.append(product)

            if not unposted_products:
                add_log("All fetched products have already been posted. Nothing new to process.")
            else:
                add_log(f"Found {len(unposted_products)} new products to process.")

                # 4. Select a random sample to process
                products_to_process = random.sample(unposted_products, min(len(unposted_products), max_pins_per_run))

                # 5. Process each product and generate pin data
                progress_bar = st.progress(0)
                for i, product in enumerate(products_to_process):
                    with st.spinner(f"Processing: {product['product_name']}..."):
                        add_log(f"Processing product: {product['product_name']}")

                        # Enrich content
                        desc, success = agent_core.generate_pin_description(
                            product['product_name'], product['description'], product['price'],
                            use_openai, openai_api_key, disclaimer, hashtag_list
                        )
                        if not success:
                            add_log(f"Failed to generate description: {desc}")
                            continue

                        # Download and format image
                        img_path, msg = agent_core.download_and_format_image(product['product_image'])
                        add_log(msg)
                        if not img_path:
                            continue

                        # Store for review
                        pin_data = {
                            'product_id': str(product['product_id']),
                            'title': product['product_name'],
                            'description': desc,
                            'image_path': img_path,
                            'product_url': product['awin_deep_link']
                        }
                        st.session_state.pins_to_review.append(pin_data)
                        progress_bar.progress((i + 1) / len(products_to_process))

                add_log("✅ Pin generation complete. Please review the pins below and approve them for posting.")

with col2:
    st.header("📜 Agent Logs")
    log_container = st.container(height=400)
    for log in st.session_state.logs:
        log_container.write(log)

st.divider()

st.header("👀 Step 2: Review and Approve Pins")
if not st.session_state.pins_to_review:
    st.info("No pins are currently awaiting review. Generate them using the button above.")
else:
    for i, pin in enumerate(st.session_state.pins_to_review):
        st.subheader(f"Reviewing: {pin['title']}")

        review_col1, review_col2 = st.columns(2)
        with review_col1:
            st.image(pin['image_path'], caption="Formatted Pin Image", use_column_width=True)

        with review_col2:
            st.text_area("Generated Description", pin['description'], height=250, key=f"desc_{i}")
            st.write(f"**Destination Link:** `{pin['product_url']}`")

            if st.button("Approve & Post to Pinterest", key=f"post_{i}"):
                with st.spinner("Posting to Pinterest..."):
                    pin_id, message = agent_core.create_pin(
                        pinterest_access_token,
                        pinterest_board_id,
                        pin['image_path'],
                        pin['description'],
                        pin['product_url'],
                        pin['title']
                    )
                    add_log(message)
                    if pin_id:
                        agent_core.mark_product_posted(pin['product_id'], pin_id)
                        add_log(f"✅ Successfully posted and marked '{pin['title']}' as complete.")
                        # Remove from review list - this is tricky in a loop, best to rerun
                        st.success("Pin posted! It will be removed from this list on the next run.")
                    else:
                        st.error("Failed to post pin.")
        st.divider()
