from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = None
open_tabs = {}  # site_name -> window_handle


def start_browser():
    global driver

    if driver is None:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

    return driver


# ------------------------------
# OPEN WEBSITE
# ------------------------------
def open_generic_website(site_name):
    global open_tabs

    driver = start_browser()

    site_key = site_name.strip().lower().replace(" ", "")

    if not site_key.startswith("http"):
        if "." not in site_key:
            url = f"https://www.{site_key}.com"
        else:
            url = f"https://{site_key}"
    else:
        url = site_key

    driver.execute_script(f"window.open('{url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])

    open_tabs[site_key] = driver.current_window_handle
    print("[OPENED TAB]", site_key)


# ------------------------------
# CLOSE SPECIFIC TAB
# ------------------------------
def close_specific_tab(site_name):
    global open_tabs, driver

    site_key = site_name.strip().lower().replace(" ", "")

    if site_key in open_tabs:
        handle = open_tabs[site_key]
        driver.switch_to.window(handle)
        driver.close()

        del open_tabs[site_key]

        if driver.window_handles:
            driver.switch_to.window(driver.window_handles[0])

        print("[CLOSED TAB]", site_key)
        return True

    return False


# ------------------------------
# SWITCH TAB
# ------------------------------
def switch_to_tab(site_name):
    global open_tabs, driver

    site_key = site_name.strip().lower().replace(" ", "")

    if site_key in open_tabs:
        handle = open_tabs[site_key]
        driver.switch_to.window(handle)
        print("[SWITCHED TO TAB]", site_key)
        return True

    return False


# ------------------------------
# CLOSE ALL TABS
# ------------------------------
def close_all_tabs():
    global driver, open_tabs

    if driver:
        driver.quit()
        driver = None
        open_tabs.clear()
        print("[ALL TABS CLOSED]")


# ------------------------------
# LIST OPEN TABS
# ------------------------------
def list_open_tabs():
    global open_tabs
    return list(open_tabs.keys())


# ------------------------------
# GOOGLE SEARCH
# ------------------------------
def search_google(query):
    driver = start_browser()

    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    driver.execute_script(f"window.open('{search_url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])

    print("[GOOGLE SEARCH]", query)
