from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from json import dump
import csv

# set Chrome driver
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
options.add_argument(f'user-agent={user_agent}')
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(service=service, options=options)

main_url = 'http://ufcstats.com/statistics/events/completed?page=all'


def get_all_links(url: str) -> list:
    """from the main link collects all fight_day links"""
    print('wait a sec')
    driver.get(url=url)
    sleep(2)
    all_links = []
    all_lk = driver.find_elements(By.CLASS_NAME, value='b-statistics__table-content')
    for link in all_lk:
        all_links.append(link.find_element(By.TAG_NAME, value='a').get_attribute('href'))
    return all_links


def get_fight_link(all_links: list) -> list:
    """collect link for every fight at fight_day link """
    all_fights = []
    for link in all_links[1:3]:
        print(f'Fight Day -- {link}')
        driver.get(url=link)
        sleep(2)
        for numb_fight in range(1, 21):
            xpath = f'/html/body/section/div/div/table/tbody/tr[{numb_fight}]/td[1]/p/a'
            try:
                fight = driver.find_element(By.XPATH, value=xpath).get_attribute('href')
                all_fights.append(fight)
                print(f'{numb_fight} fight -- {fight}')
            except:
                break
    return all_fights

def set_headers_csv() -> None:
    """set header row"""
    with open('data/ufcstats.csv', 'w', newline='') as f:
        headers = (
            'FIGHT URL', 'FIGHTER 1', 'FIGHTER 2', 'METHOD', 'DETAILS', 'ROUND', 'TIME', 'TIME FORMAT', 'REFEREE')
        writer = csv.writer(f)
        writer.writerow(headers)

def add_to_csv(info: list) -> None:
    """add row with data"""
    with open('data/ufcstats.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(info)


def gather_info(all_fights) -> None:
    """gather all information
       represent data in json and csv"""
    # final dict that will convert in json
    result_dict = {}

    # get specific fight link
    count = 1
    for fight_url in all_fights:
        driver.get(fight_url)
        sleep(2)

        fight_info = {'URL': fight_url}

        # ---------------------GATHER INFORMATION FROM FIGHT--------------------------------------------
        fighter_day = driver.find_element(By.XPATH, value='/html/body/section/div/h2/a').text

        fighter_1 = driver.find_element(By.XPATH, value='/html/body/section/div/div/div[1]/div[1]/div/h3/a').text
        fighter_2 = driver.find_element(By.XPATH, value='/html/body/section/div/div/div[1]/div[2]/div/h3/a').text
        fight_info['fighter_1'] = fighter_1
        fight_info['fighter_2'] = fighter_2

        try:
            method = driver.find_element(By.CLASS_NAME, value='b-fight-details__text-item_first').text
            fight_info[method.split(': ')[0]] = method.split(': ')[1]
            method = method.split(': ')[1]
        except Exception:
            method = 'no info'

        #collect info about ROUND, TIME, TIME FORMAT, REFEREE and save it in list
        round_time_ref = []
        try:
            for inf in range(2, 6):
                some_info = driver.find_element(By.XPATH, value=f'/html/body/section/div/div/div[2]/div[2]/p[1]/i[{inf}]').text
                fight_info[some_info.split(': ')[0]] = some_info.split(': ')[1]
                round_time_ref.append(some_info.split(': ')[1])
        except Exception:
            round_time_ref.append('no info')

        try:
            details = driver.find_element(By.XPATH, value='/html/body/section/div/div/div[2]/div[2]/p[2]').text
            fight_info[details.split(': ')[0]] = details.split(': ')[1]
            details = details.split(': ')[1]
        except Exception:
            details = 'no info'

        add_to_csv([fight_url, fighter_1, fighter_2, method, details] + round_time_ref)

        result_dict[f'{fighter_day} ({count})'] = fight_info

        # for a beautiful output
        print(f'from {count} info was received')
        count += 1
    # ------------------------convert in json-----------------------------------------------------------
    with open('data/ufcstats.json', 'w') as f:
        dump(result_dict, f, indent=4, ensure_ascii=False)

    print('scraping successfully ended')


def main():
    all_links = get_all_links(main_url)
    all_fights = get_fight_link(all_links)
    set_headers_csv()
    gather_info(all_fights)


if __name__ == '__main__':
    main()
