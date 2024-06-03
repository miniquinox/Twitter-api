import json
import pandas as pd
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from textblob import TextBlob
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import matplotlib.colors as mcolors
from collections import defaultdict
from apify_client import ApifyClient
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

# Define stop words for filtering
stop_words = set(stopwords.words('english'))

# Define the main functions
def data_processing(text):
    """
    Clean and preprocess text data.
    
    Parameters:
    text (string): The input text to be processed.
    
    Returns:
    string: The cleaned and processed text.
    """
    # Convert text to lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r"https\S+|www\S+https\S+", '', text, flags=re.MULTILINE)
    # Remove mentions and hashtags
    text = re.sub(r'\@w+|\#','', text)
    # Remove punctuation
    text = re.sub(r'[^\w\s]','', text)
    # Tokenize text
    text_tokens = word_tokenize(text)
    # Filter out stop words
    filtered_text = [w for w in text_tokens if not w in stop_words]
    return " ".join(filtered_text)

def sentiment(label):
    """
    Determine sentiment based on polarity score.
    
    Parameters:
    label (float): Polarity score.
    
    Returns:
    string: Sentiment category ("Negative", "Neutral", or "Positive").
    """
    if label < 0:
        return "Negative"
    elif label == 0:
        return "Neutral"
    elif label > 0:
        return "Positive"
    
def stemming(data):
    """
    Apply stemming to the data.
    
    Parameters:
    data (list): List of words to be stemmed.
    
    Returns:
    list: List of stemmed words.
    """
    stemmer = PorterStemmer()
    return [stemmer.stem(word) for word in data]

def polarity(text):
    """
    Compute the polarity of the text.
    
    Parameters:
    text (string): The input text.
    
    Returns:
    float: Polarity score.
    """
    return TextBlob(text).sentiment.polarity

def sentimental_analysis(df):
    """
    Perform sentiment analysis on the text data.
    
    Parameters:
    df (DataFrame): DataFrame containing the text data.
    
    Returns:
    DataFrame: DataFrame with sentiment analysis results.
    """
    # Create a DataFrame for text data
    df_text = pd.DataFrame()
    df_text['text'] = df['text']
    # Apply text processing
    df_text['text'] = df_text['text'].apply(data_processing)
    # Remove duplicate texts
    text_df = df_text.drop_duplicates()
    # Apply stemming
    text_df['text'] = text_df['text'].apply(lambda x: stemming(x))
    # Compute polarity
    text_df['polarity'] = text_df['text'].apply(polarity)
    # Determine sentiment
    text_df['sentiment'] = text_df['polarity'].apply(sentiment)
    
    return text_df

def plots(df, df_2):
    """
    Plot average views count per hashtag and sentiment distribution.
    
    Parameters:
    df (DataFrame): DataFrame containing hashtag and views count data.
    df_2 (DataFrame): DataFrame containing sentiment analysis results.
    
    Returns:
    None
    """
    # Plotting Average views count per Hashtag
    df = df.dropna(subset=['hashtag'])
    plt.bar(df['hashtag'], df['views_count'], color='skyblue')

    # Adding title and labels
    plt.title('Average views count per Hashtag')
    plt.xlabel('Hashtag')
    plt.ylabel('Average views count')

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Display the plot
    plt.tight_layout()
    hashtag_plot_filename = 'hashtag_plot.png'
    plt.savefig(hashtag_plot_filename)
    plt.clf()
    plt.show()

    # Plotting Distribution of sentiments
    fig = plt.figure(figsize=(7,7))
    colors = ("yellowgreen", "gold", "red")
    wp = {'linewidth': 2, 'edgecolor': "black"}
    tags = df_2['sentiment'].value_counts()
    explode = (0.1, 0.1, 0.1)
    tags.plot(kind='pie', autopct='%1.1f%%', shadow=True, colors=colors,
              startangle=90, wedgeprops=wp, explode=explode, label='')
    plt.title('Distribution of sentiments')
    plt.show()
    
def wordcloud(extract_data):
    """
    Generate a word cloud with color indicating sentiment.
    
    Parameters:
    extract_data (DataFrame): DataFrame containing text and polarity data.
    
    Returns:
    None
    """
    # Tokenize the text and calculate the average polarity for each word
    word_sentiment = defaultdict(list)
    for _, row in extract_data.iterrows():
        words = row['text'].split()
        for word in words:
            word_sentiment[word].append(row['polarity'])

    # Calculate average sentiment for each word
    word_avg_sentiment = {word: sum(sentiments) / len(sentiments) for word, sentiments in word_sentiment.items()}

    # Define a function to determine the color of words in the word cloud
    def color_func(word, **kwargs):
        sentiment = word_avg_sentiment.get(word, 0)
        # Normalize the sentiment score to be between 0 and 1 for the color map
        norm_sentiment = (sentiment + 1) / 2
        # Get the color from the RdYlGn color map
        rgba_color = plt.cm.RdYlGn(norm_sentiment)
        # Convert the RGBA color to hex format
        return mcolors.rgb2hex(rgba_color)

    # Generate word cloud
    text = ' '.join(extract_data['text'])
    wordcloud = WordCloud(width=800, height=400, color_func=color_func).generate(text)

    # Display the generated image
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

def extract_tweets(api_token, actor_id, searchhashtag):
    '''
    Extract tweets using Apify API.
    
    Parameters:
    api_token (string): Personal API token obtained from Apify.
    actor_id (string): Scraper ID provided by Apify.
    searchhashtag (string): Hashtag to search for tweets.

    Returns:
    None
    '''
    # Initialize Apify client
    client = ApifyClient(api_token)

    # Define input for the Apify actor run
    run_input = {
        "searchTerms": [searchhashtag],
        "searchMode": "live",
        "addUserInfo": True,
        "scrapeTweetReplies": True,
        "urls": ["https://twitter.com/search?q=gpt&src=typed_query&f=live"],
    }

    # Run the actor and get the dataset ID
    run = client.actor(actor_id).call(run_input=run_input)
    dataset_id = run["defaultDatasetId"]
    
    # Fetch dataset items
    dataset_items = []
    for item in client.dataset(dataset_id).iterate_items():
        dataset_items.append(item)

    # Save dataset items to a JSON file
    result_file_path = 'tweets.json'
    with open(result_file_path, 'w') as file:
        json.dump(dataset_items, file, ensure_ascii=False, indent=4)

    print(f"Dataset items stored in '{result_file_path}'.")

def filter_dataset_items(input_path, output_path, desired_fields, hashtag_filter):
    """
    Filter dataset items to include only the desired fields and specified hashtag.
    
    Parameters:
    input_path (string): Path to the input JSON file containing the original dataset items.
    output_path (string): Path to save the filtered dataset items as a JSON file.
    desired_fields (list): List of fields to be included in the filtered dataset items.
    hashtag_filter (string): The specific hashtag to filter by (lowercase).
    
    Returns:
    None
    """
    # Load data from the input JSON file
    with open(input_path, 'r') as file:
        data = json.load(file)

    # Filter and extract desired fields from data
    filtered_data = []
    for item in data:
        filtered_item = {field: item[field] for field in desired_fields if field in item}
        hashtags = item.get('entities', {}).get('hashtags', [])
        filtered_item['hashtags'] = [{'text': hashtag['text']} for hashtag in hashtags]
        filtered_data.append(filtered_item)

    # Save the filtered data to a new JSON file
    with open(output_path, 'w') as file:
        json.dump(filtered_data, file, indent=4)

    print(f'Filtered data has been saved to {output_path}')

def data_cleaning():
    """
    Clean and transform tweet data for analysis.
    
    Returns:
    top_10 (DataFrame): DataFrame containing the top 10 hashtags by average views count.
    extracted_df (DataFrame): DataFrame containing the cleaned tweet data.
    """
    # Load the filtered tweet content JSON file into a DataFrame
    df = pd.read_json('required_tweet_content.json')

    # Check if the DataFrame has the required columns
    if 'user_id_str' in df.columns and 'views_count' in df.columns and 'full_text' in df.columns and 'hashtags' in df.columns:
        # Initialize an empty list to store the extracted data
        extracted_data = []

        # Iterate over each row in the DataFrame
        for index, row in df.iterrows():
            username = row['user_id_str']
            views_count = row['views_count']
            text = row['full_text']
            
            # Ensure hashtags are in a list format
            if isinstance(row['hashtags'], list):
                hashtag_texts = [hashtag['text'] for hashtag in row['hashtags'] if 'text' in hashtag]
            else:
                hashtag_texts = []  # No hashtags or not in expected format

            # Append data to the list
            for hashtag_text in hashtag_texts:
                extracted_data.append({
                    'username': username,
                    'views_count': views_count,
                    'text': text,
                    'hashtag': hashtag_text
                })

        # Create a DataFrame from the extracted data
        extracted_df = pd.DataFrame(extracted_data)

    else:
        print("DataFrame does not have the required columns.")
        return None, None

    # Calculate average views count per hashtag
    average_likes_per_hashtag = extracted_df.groupby('hashtag')['views_count'].mean().reset_index()

    # Get the top 10 hashtags by average views count
    top_10 = average_likes_per_hashtag.sort_values(by='views_count', ascending=False).head(20)

    return top_10, extracted_df

# Main execution block
if __name__ == "__main__":
    api_token = 'Apify Api token'
    actor_id = "heLL6fUofdPgRXZie"
    searchterm = "#informs2023"

    # Extract tweets
    extract_tweets(api_token, actor_id, searchterm)

    # File paths for input and output
    input_file_path = 'tweets.json'
    output_file_path = 'required_tweet_content.json'

    # Desired fields for filtering
    desired_fields = [
        "full_text", "lang", "reply_count", "retweet_count", "retweeted",
        "user_id_str", "id_str", "url", "views_count", "created_at"
    ]

    # Filter dataset items
    filter_dataset_items(input_file_path, output_file_path, desired_fields, 'businessanalysts')

    # Clean and process data
    top_10, extracted_data = data_cleaning()
    extract_data = sentimental_analysis(extracted_data)

    # Create and show the plots
    plots(top_10, extract_data)
    wordcloud(extract_data)

    # Send the sentiment plot via email
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

    # Authenticate and build the Gmail API service
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)

    # Create a MIMEMultipart message
    message = MIMEMultipart()
    message['to'] = 'himanishprakash23@gmail.com, himprakash@ucdavis.edu'
    message['subject'] = 'Test Mail with Image Attachment'
    message.attach(MIMEText('Yayy, first attempt successful with image!'))

    # Attach the image to the email
    with open("hashtag_plot.png", "rb") as image_file:
        img_data = image_file.read()
    image = MIMEImage(img_data)
    image.add_header('Content-ID', '<image1>')  
    message.attach(image)

    # Encode the message in base64
    encoded_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    # Send the email
    try:
        sent_message = service.users().messages().send(userId="me", body=encoded_message).execute()
        print(f'Sent message to {message["to"]}. Message Id: {sent_message["id"]}')
    except HTTPError as error:
        print(f'An error occurred: {error}')
