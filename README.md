# Pinterest Affiliate Curator & Scheduler

This project is a Streamlit application that functions as an intelligent curation and marketing assistant for Pinterest. It helps automate the process of creating and posting affiliate product pins from an AWIN data feed.

The agent is designed with a "human-in-the-loop" approach, where it generates pin content for your review and approval before anything is posted to your Pinterest account.

## Features

- **AWIN Integration**: Fetches product data directly from your AWIN product data feed URL.
- **Content Generation**: Automatically generates engaging pin descriptions using either templates or the OpenAI GPT-4 API.
- **Image Formatting**: Downloads product images and formats them to the optimal 2:3 aspect ratio for Pinterest.
- **Review & Approve Workflow**: Presents generated pins in a user-friendly interface for you to review and approve before posting.
- **Duplicate Prevention**: Keeps track of posted products in a local SQLite database to avoid posting the same item twice.
- **Logging**: Provides real-time logs of its activities.

## How to Set Up and Run

### 1. Installation

First, clone this repository to your local machine. Then, navigate to the project directory and install the required Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 2. Running the Application

Once the dependencies are installed, you can run the Streamlit application with the following command:

```bash
streamlit run app.py
```

This will open the application in a new tab in your web browser.

### 3. Configuration

All settings are managed directly within the Streamlit application's sidebar:

- **AWIN Product Feed URL**: Your unique URL for an AWIN product data feed.
- **Pinterest Access Token**: Your access token for the Pinterest API.
- **OpenAI API Key**: Your API key for OpenAI (optional, only needed if you enable AI-powered descriptions).
- **Pinterest Board ID**: The ID of the Pinterest board where you want to post the pins.
- **Affiliate Disclaimer**: The affiliate disclosure text to be appended to each pin description.
- **Hashtag Pool**: A comma-separated list of hashtags to be randomly sampled for each pin.
- **Max Products to Process per Run**: The number of new products to fetch and process each time you run the agent.
- **Use OpenAI for Pin Descriptions**: A checkbox to enable or disable the use of OpenAI for generating descriptions.

### Important Note on Pinterest API v5 and Image Hosting

The current version of the Pinterest API (v5) requires that images be accessible via a public URL. This application downloads and processes images locally, but it does not host them publicly.

To make this application fully functional for **real posting**, you would need to extend the `create_pin` function in `agent_core.py` to upload the processed image to a public hosting service (like AWS S3, Google Cloud Storage, or a free service like Imgur) and use the resulting public URL.

For demonstration purposes, the application **simulates** the pin creation process and logs the action without actually posting to Pinterest.
