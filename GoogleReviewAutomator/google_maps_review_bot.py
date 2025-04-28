from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import pandas as pd
from gemini_module import summarize_reviews, generate_comment  # Your LLM functions


# -------------- Setup Chrome Options --------------
options = Options()
options.add_argument("--start-maximized")
# Uncomment below if you want to use an existing Chrome profile
# options.add_argument("user-data-dir=C:\\Users\\User\\AppData\\Local\\Google\\Chrome\\User Data")
# options.add_argument("profile-directory=Profile 1")  # Use your correct profile name
driver = webdriver.Chrome(options=options)

# -------------- Session Log --------------
session_logs = []

# -------------- Functions --------------

def initialize_browser(url):
    """Open the browser and navigate to the provided URL."""
    driver.get(url)
    time.sleep(5)


def get_all_reviews_button():
    """Click the 'All reviews' button if available."""
    try:
        all_reviews_button = driver.find_element(By.XPATH, '//button[contains(text(), "All reviews")]')
        all_reviews_button.click()
        time.sleep(3)
        print("✅ Navigated to 'All reviews' page...")
    except:
        print("ℹ️ 'All reviews' button not found. Maybe already on the reviews page.")


def extract_reviews():
    """Extract all visible reviews from the page."""
    review_elements = driver.find_elements(By.XPATH, '//div[@class="MyEned"]')
    reviews = [r.text.strip() for r in review_elements if r.text.strip()]
    return reviews


def post_comment(comment):
    """Click 'Write a review', enter comment, and submit."""
    print("\n🔵 Waiting for you to confirm page is ready. Press ENTER when ready...")
    input("Press ENTER when ready..")

    try:
        # Find the span with "Write a review"
        write_review_span = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Write a review")]'))
        )
        # Click its parent button
        parent_button = write_review_span.find_element(By.XPATH, './ancestor::button')
        parent_button.click()
        print("✅ Clicked 'Write a review' button.")
        
        # Wait for the textarea to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//textarea'))
        )
        
        review_textarea = driver.find_element(By.XPATH, '//textarea')
        review_textarea.send_keys(comment)
        time.sleep(1)

        # Wait for the submit button
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@jsaction="click:TiglPc"]'))
        )
        submit_button.click()
        print("✅ Review comment posted successfully!\n")
        time.sleep(3)

    except Exception as e:
        print(f"⚠️ Could not post review: {e}")


def save_to_csv(data, filename="maps_review_log.csv"):
    """Save review data to a CSV file."""
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(data)


def prepare_and_print_logs():
    """Display session logs neatly."""
    global session_logs
    df = pd.DataFrame(session_logs)
    print("\n📋 Session Summary:")
    print(df.to_string(index=False))


# -------------- Main Loop --------------

def main():
    global session_logs
    while True:
        url = input("\n\n🌐 Enter Google Maps URL (or 'exit' to quit): ").strip()
        if url.lower() == "exit":
            break

        # Step 1: Open the URL
        initialize_browser(url)

        # Step 2: Click "All reviews" if available
        get_all_reviews_button()

        # Step 3: Extract reviews
        reviews = extract_reviews()

        if reviews:
            print(f"\n📑 Found {len(reviews)} reviews. Generating summary...\n")
            summary = summarize_reviews(reviews)
            comment = generate_comment(summary)

            print("\n🔹 LLM Summary:", summary)
            print("\n💬 LLM Auto-Generated Comment:", comment)

            # Step 4: Post the comment
            post_comment(comment)

            # Step 5: Save the session
            save_to_csv([url, summary, comment])
            session_logs.append({"URL": url, "Summary": summary, "Comment": comment})

            # Step 6: Show summary
            prepare_and_print_logs()

        else:
            print("⚠️ No reviews found on the page.")

    print("\n✅ Done. Closing browser.")
    driver.quit()


if __name__ == "__main__":
    main()
