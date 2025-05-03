import os
import sys
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load credentials
load_dotenv()
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
    print("❌ LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be in .env")
    sys.exit(1)

async def connect_with_message(profile_url, message):
    print("🚀 Starting LinkedIn automation...")

    async with async_playwright() as p:
        browser = None
        page = None

        try:
            browser = await p.chromium.launch(
                channel="chrome",  # Use system Chrome
                headless=False,
                slow_mo=100,
                args=["--no-sandbox", "--disable-gpu"]
            )

            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )

            page = await context.new_page()
            await page.set_default_navigation_timeout(90000)
            await page.set_default_timeout(45000)

            # LinkedIn login
            print("🔐 Going to LinkedIn login page...")
            await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            print("👤 Logging in...")
            await page.fill("input#username", LINKEDIN_EMAIL)
            await page.fill("input#password", LINKEDIN_PASSWORD)
            await page.click("button[type='submit']")

            try:
                await page.wait_for_selector("text=Feed", timeout=10000)
                print("✅ Logged in to LinkedIn")
            except:
                print("⚠️ Feed not detected, assuming login still succeeded")

            await page.screenshot(path="linkedin_home.png")
            await page.wait_for_timeout(3000)

            # Navigate to profile
            print(f"🌐 Navigating to profile: {profile_url}")
            await page.goto(profile_url, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(4000)
            await page.screenshot(path="profile_page.png")

            # Click Connect
            print("🔍 Finding Connect button...")
            connect_found = False
            connect_selectors = [
                "button:has-text('Connect')",
                "button[aria-label*='Connect']",
                ".pvs-profile-actions__action button:has-text('Connect')"
            ]
            for sel in connect_selectors:
                try:
                    btn = await page.query_selector(sel)
                    if btn is None:
                        print(f"❌ {sel} returned None")
                        continue
                    if await btn.is_visible():
                        await btn.click()
                        print(f"✅ Clicked Connect using: {sel}")
                        connect_found = True
                        break
                    else:
                        print(f"❌ {sel} not visible")
                except Exception as e:
                    print(f"❌ Error with Connect selector {sel}: {e}")

            if not connect_found:
                await page.screenshot(path="no_connect.png")
                return "❌ Connect button not found."

            await page.wait_for_timeout(2000)

            # Click Add a note
            print("💬 Looking for 'Add a note' button...")
            try:
                note_btn = await page.query_selector("button:has-text('Add a note')")
                if note_btn is None:
                    print("❌ Selector returned None: note_btn")
                elif not await note_btn.is_visible():
                    print("❌ 'Add a note' not visible")
                else:
                    await note_btn.click()
                    await page.wait_for_timeout(1000)
                    print("✅ Clicked 'Add a note'")
            except Exception as e:
                print(f"❌ Exception while clicking 'Add a note': {e}")

            # Fill message
            print("✍️ Trying to fill message...")
            try:
                textarea = await page.query_selector("textarea[name='message']")
                if textarea is None:
                    print("❌ Selector returned None: textarea")
                elif not await textarea.is_visible():
                    print("❌ Textarea not visible")
                else:
                    await textarea.fill(message)
                    print(f"📝 Message filled: {message}")
                    await page.screenshot(path="message_filled.png")
            except Exception as e:
                print(f"❌ Exception while filling message: {e}")
                await page.screenshot(path="no_textarea.png")
                return "❌ Failed to fill message."

            # Click Send
            print("📤 Looking for Send button...")
            try:
                send_btn = await page.query_selector("button:has-text('Send')")
                if send_btn is None:
                    print("❌ Selector returned None: send_btn")
                elif not await send_btn.is_visible():
                    print("❌ Send button not visible")
                else:
                    await send_btn.click()
                    print("✅ Connection request sent!")
                    await page.screenshot(path="after_send.png")
                    return "✅ Connection request sent!"
            except Exception as e:
                print(f"❌ Exception while clicking Send: {e}")
                await page.screenshot(path="no_send.png")
                print("⚠️ Waiting 30s before manual exit...")
                await page.wait_for_timeout(30000)
                return "⚠️ Please click Send manually"

            print("⏳ Waiting 30s before closing browser...")
            await page.wait_for_timeout(30000)
            return "✅ Message filled. Please click Send manually."

        except Exception as e:
            print(f"❌ Top-level error: {e}")
            if page:
                await page.screenshot(path="error.png")
            return f"❌ Exception occurred: {e}"

        finally:
            if browser:
                print("🛑 Closing browser...")
                await browser.close()


# For direct CLI test
if __name__ == "__main__":
    async def main():
        url = input("Enter LinkedIn profile URL: ")
        msg = input("Enter connection message: ")
        result = await connect_with_message(url, msg)
        print(result)

    asyncio.run(main())
