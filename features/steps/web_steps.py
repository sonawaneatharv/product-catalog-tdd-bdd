"""
Web Steps for BDD using Selenium WebDriver.
"""
import logging
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions


ID_PREFIX = "product_"


@when('I press the "{button}" button')
def step_impl(context, button):
    """Click a button by its text."""
    button_id = button.lower().replace(" ", "_")
    context.driver.find_element(By.ID, button_id).click()


@then('I should see "{name}" in the results')
def step_impl(context, name):
    """Verify a specific name or text is present in the results."""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), name
        )
    )
    assert found, f"'{name}' was not found in the results"


@then('I should not see "{name}" in the results')
def step_impl(context, name):
    """Verify a specific name or text is NOT present in the results."""
    element = context.driver.find_element(By.ID, "search_results")
    assert name not in element.text, f"'{name}' was found in the results when it should not be"


@then('I should see the message "{message}"')
def step_impl(context, message):
    """Verify a specific flash message is present."""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found, f"Message '{message}' was not found"
