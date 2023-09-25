import openai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

# Ваш API ключ от OpenAI
api_key = ''

# Функция для получения текста задачи с LeetCode
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
def generate_response(problem_text, programming_language):
    try:
        openai.api_key = api_key

        # Создаем шаблон кода на указанном языке программирования
        prompt = f"Solve the following problem in {programming_language}:\n\n{problem_text}\n\nSolution:"

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=2000  # Максимальное количество токенов в ответе (можете изменить по вашему усмотрению)
        )

        if response.choices:
            return response.choices[0].text.strip()
        else:
            return "No response from GPT-3.5"

    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while generating a response"

# Основная функция
if __name__ == '__main__':
    # URL задачи на LeetCode
    url = 'https://leetcode.com/problems/valid-anagram/'

    # Получаем текст задачи
    problem_text = fetch_problem(url)

    # Указываем язык программирования
    programming_language = 'Python'  # Замените на нужный вам язык

    # Генерируем ответ с использованием GPT-3.5
    response = generate_response(problem_text, programming_language)

    # Открываем браузер и переходим на страницу входа
    driver = webdriver.Chrome()
    driver.get('https://leetcode.com/accounts/login/')

    try:
        # Находим поля для ввода логина и пароля
        username_input = driver.find_element(By.NAME, 'login')
        password_input = driver.find_element(By.NAME, 'password')

        # Вводим учетные данные
        username_input.send_keys('')
        password_input.send_keys('')

        # Нажимаем Enter, чтобы выполнить вход
        password_input.send_keys(Keys.RETURN)

        # После успешного входа переходим на страницу задачи
        driver.get(url)

        # Находим поле для ввода кода
        wait = WebDriverWait(driver, 30)
        code_input = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@data-cy='code-editor']")))

        # Вставляем сгенерированный код
        code_input.send_keys(response)

        # Нажимаем Ctrl + Enter, чтобы выполнить код
        code_input.send_keys(Keys.CONTROL, Keys.RETURN)

    except Exception as e:
        print(f"An error occurred while submitting the code: {e}")

    finally:
        # Закрываем браузер
        driver.quit()