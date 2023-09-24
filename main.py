import openai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from decouple import Config, Csv


config = Config()
# Чтение API ключа
api_key = config.get('API_KEY')

# Функция для получения задачи с LeetCode
def fetch_problem(url):
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    # Открываем URL
    driver.get(url)

    try:
        # Ждем, пока содержимое страницы полностью загрузится
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "xFUwe"))
        )

        # Преобразовываем содержимое страницы в BeautifulSoup объект
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Ищем блок с проблемой
        problem_content = soup.find('div', class_='xFUwe')

        # Получаем текст проблемы
        problem_text = problem_content.text if problem_content else "Problem not found"

        return problem_text

    except TimeoutException as te:
        print(f"TimeoutException: {te}")
        return "TimeoutException: Problem not found"

    except Exception as e:
        print(f"Exception: {e}")
        return "Problem not found"

    finally:
        # Закрываем браузер
        driver.quit()

# Функция для отправки задачи в GPT-3.5 и получения ответа
def generate_response(prompt):
    try:
        openai.api_key = api_key
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=150  # Максимальное количество токенов в ответе (можете изменить по вашему усмотрению)
        )

        if response.choices:
            return response.choices[0].text.strip()
        else:
            return "No response from GPT-3.5"

    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while generating a response"

if __name__ == '__main__':
    # URL задачи на LeetCode
    url = 'https://leetcode.com/problems/search-insert-position/'

    # Получаем текст задачи
    problem_text = fetch_problem(url)

    # Генерируем ответ с использованием GPT-3.5
    response = generate_response(problem_text)

    # Выводим ответ
    print(response)
