from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, timedelta
import time

# -----------------------
# Open Chrome
# -----------------------

driver = webdriver.Chrome()
driver.maximize_window()

wait = WebDriverWait(driver, 10)

# -----------------------
# Login
# -----------------------

driver.get("http://127.0.0.1:8000/")

wait.until(
    EC.presence_of_element_located(
        (By.NAME, "username")
    )
).send_keys("amisha")

driver.find_element(
    By.NAME,
    "password"
).send_keys("amisha123")

driver.find_element(
    By.TAG_NAME,
    "button"
).click()

wait.until(
    EC.title_contains("Patient Dashboard")
)

print("Logged in successfully.")

# -----------------------
# Open Doctor Directory
# -----------------------

wait.until(
    EC.element_to_be_clickable(
        (By.ID, "book-appointment-btn")
    )
).click()

print("Doctor Directory opened.")

# -----------------------
# Open Dr. Ram Pradhan
# -----------------------

wait.until(
    EC.element_to_be_clickable(
        (By.ID, "book-doctor-8")
    )
).click()

print("Doctor profile opened.")

# -----------------------
# Calculate next Monday
# -----------------------

today = date.today()

days_until_monday = (7 - today.weekday()) % 7

if days_until_monday == 0:
    days_until_monday = 7

next_monday = today + timedelta(days=days_until_monday)

test_date = next_monday.strftime("%Y-%m-%d")

print("Booking Date:", test_date)

# -----------------------
# Select appointment date
# -----------------------

date_box = wait.until(
    EC.presence_of_element_located(
        (By.ID, "appointment-date")
    )
)

driver.execute_script(
    """
    arguments[0].value = arguments[1];
    arguments[0].dispatchEvent(new Event('change'));
    """,
    date_box,
    test_date
)

print("Date selected.")

# -----------------------
# Wait for slots
# -----------------------

wait.until(
    EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "time-slot")
    )
)

print("Time slots loaded.")

# -----------------------
# Select first slot
# -----------------------

slot = wait.until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "input.time-slot")
    )
)

driver.execute_script(
    "arguments[0].click();",
    slot
)

time.sleep(1)

print("Radio selected:", slot.is_selected())

assert slot.is_selected(), "Time slot was not selected."

print("First slot selected.")

# -----------------------
# Click Continue
# -----------------------

continue_button = wait.until(
    EC.element_to_be_clickable(
        (By.ID, "continue-booking")
    )
)

driver.execute_script(
    "arguments[0].scrollIntoView({block:'center'});",
    continue_button
)

time.sleep(1)

driver.execute_script(
    "arguments[0].click();",
    continue_button
)

print("Continue clicked.")

# -----------------------
# Wait for Confirm Page
# -----------------------

wait.until(
    EC.title_contains("Confirm Appointment")
)

print("Confirm page opened.")

# -----------------------
# Confirm Appointment
# -----------------------

confirm_button = wait.until(
    EC.element_to_be_clickable(
        (By.ID, "confirm-appointment")
    )
)

driver.execute_script(
    "arguments[0].scrollIntoView({block:'center'});",
    confirm_button
)

time.sleep(1)

driver.execute_script(
    "arguments[0].click();",
    confirm_button
)

print("Appointment confirmed.")

# -----------------------
# Debug Redirect
# -----------------------

time.sleep(3)

print("Current URL:", driver.current_url)
print("Current Title:", driver.title)

time.sleep(5)

driver.quit()