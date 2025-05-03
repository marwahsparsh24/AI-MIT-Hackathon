import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from serpapi import GoogleSearch
from openai import OpenAI

load_dotenv()

# Setup OpenAI
client = OpenAI()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")


def search_linkedin_profile(name, company):
    query = f'site:linkedin.com/in "{name}" "{company}"'
    search = GoogleSearch({
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 1
    })
    results = search.get_dict()
    return results["organic_results"][0]["link"] if results.get("organic_results") else None


def generate_message(name, company, event_name):
    prompt = f"""
    Write a LinkedIn connection message to {name} from {company}.
    Mention that you met them at {event_name}.
    Be concise, polite, and professional (under 200 words).
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def send_connection_request(linkedin_url, message, headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        wait = WebDriverWait(driver, 10)
        driver.get("https://www.linkedin.com/login")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(LINKEDIN_EMAIL)
        driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        wait.until(EC.url_contains("/feed"))  # Wait for login to redirect

        driver.get(linkedin_url)
        time.sleep(5)

        # Try to find visible Connect button
        connect_button = None
        try:
            connect_button = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//button[@aria-label='Connect']"
            )))
        except:
            try:
                # If not directly visible, try More > Connect
                more_button = wait.until(EC.element_to_be_clickable((
                    By.XPATH, "//button[contains(., 'More') or @aria-label='More actions']"
                )))
                more_button.click()
                connect_button = wait.until(EC.element_to_be_clickable((
                    By.XPATH, "//span[text()='Connect']/ancestor::button"
                )))
            except:
                driver.quit()
                return  # silently return without error message


        connect_button.click()

        # Wait for modal and Add Note
        add_note_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[contains(., 'Add a note')]"
        )))
        add_note_btn.click()

        # Type message (max 300 chars)
        message_box = wait.until(EC.presence_of_element_located((By.ID, "custom-message")))
        message_box.clear()
        message_box.send_keys(message[:299])

        # Click Send
        send_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[@aria-label='Send now']"
        )))
        send_button.click()

        driver.quit()
        return "✅ Connection request sent with personalized message."

    except Exception as e:
        driver.save_screenshot("error_debug.png")
        driver.quit()
        return f"❌ Failed: {str(e)}"


def connect_and_send(name, company, event_name, headless=True):
    profile_url = search_linkedin_profile(name, company)
    if not profile_url:
        return {"error": "LinkedIn profile not found."}

    message = generate_message(name, company, event_name)
    status = send_connection_request(profile_url, message, headless)
    return {
        "profile": profile_url,
        "message": message,
        "status": status
    }