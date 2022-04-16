import re
import time
import os
import glob
from time import sleep
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# このファイルがあるディレクトリ
dir_base = os.path.dirname(os.path.abspath(__file__))
# URLの設定
root_url = "https://ncode.syosetu.com/"
root_novel_info_url = "https://ncode.syosetu.com/novelview/infotop/ncode/"
# Chrome起動オプション
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)
# 要素が見つかるまでの最大待機時間の設定
driver.implicitly_wait(10)
wait = WebDriverWait(driver, 20)


def get_novel(setvalues):
    """長編小説のダウンロード処理

    Args:
        setvalues(dict): 設定値
    """
    novels = []
    for i in range(setvalues["start"], setvalues["num_parts"]):
        url = f"{setvalues['novel_url']}/{str(i + 1)}/"

        error_msg = None
        for _ in range(3):
            try:
                driver.get(url)
                time.sleep(3)
                wait.until(EC.visibility_of_element_located(
                    (By.ID, "novel_honbun")))
            except TimeoutException as e:
                error_msg = e
            except Exception as e:
                error_msg = e
            else:
                html_text = BeautifulSoup(
                    driver.page_source, "html.parser")
                subtitle = html_text.find(
                    "p", class_="novel_subtitle").text
                a_subtitle = f"［＃３字下げ］{subtitle}［＃「{subtitle}」は中見出し］"
                honbun = html_text.select_one("#novel_honbun").text
                novels.append(f"{a_subtitle}\n\n{honbun}")

                name = os.path.join(
                    setvalues["novel_dir"], f"{setvalues['title']}_{str(i + 1)}.txt")
                with (open(name, mode='w', encoding='utf_8', errors='ignore') as f):
                    f.writelines(novels)
                novels.clear()
                # 進捗を表示
                print(
                    f"{str(i + 1)} / {setvalues['num_fetch_rest']} downloaded")
                break
        else:
            # リトライがすべて失敗した場合
            if type(error_msg) == TimeoutException:
                print("TimeoutException.")
            if type(error_msg) == Exception:
                print("Exception.")
            driver.quit()
    else:
        print("Complete!")
        # ブラウザを閉じる
        driver.quit()


def get_short_story(setvalues):
    """短編小説のダウンロード処理

    Args:
        setvalues(dict): 設定値
    """
    novels = []
    url = setvalues["novel_url"]
    error_msg = None
    for _ in range(3):
        try:
            driver.get(url)
            time.sleep(3)
            wait.until(EC.visibility_of_element_located(
                (By.ID, "novel_honbun")))
        except TimeoutException as e:
            error_msg = e
        except Exception as e:
            error_msg = e
        else:
            html_text = BeautifulSoup(driver.page_source, "html.parser")
            subtitle = html_text.find("p", class_="novel_title").text
            a_subtitle = f"［＃３字下げ］{subtitle}［＃「{subtitle}」は中見出し］"
            honbun = html_text.select_one("#novel_honbun").text
            novels.append(f"{a_subtitle}\n\n{honbun}")

            name = os.path.join(
                setvalues["novel_dir"], f"{setvalues['title']}.txt")
            with (open(name, mode='w', encoding='utf_8', errors='ignore') as f):
                f.writelines(novels)

            print("Complete!")
            # ブラウザを閉じる
            driver.quit()
            break
    else:
        # リトライがすべて失敗した場合
        if type(error_msg) == TimeoutException:
            print("TimeoutException.")
        if type(error_msg) == Exception:
            print("Exception.")
        driver.quit()


def main():
    print("Please enter Ncode.")
    ncode = input()
    setvalues = {}
    # NcodeをURLに設定
    setvalues["novel_url"] = root_url + ncode
    setvalues["novel_info_url"] = root_novel_info_url + ncode
    # 掲載話数の取得
    driver.get(setvalues["novel_info_url"])
    wait.until(EC.visibility_of_element_located((By.ID, "pre_info")))
    html_text = BeautifulSoup(driver.page_source, "html.parser")
    pre_info = html_text.select_one("#pre_info").text
    result = re.search(r"全([0-9]+)部分", pre_info)
    num_parts = 0
    if result != None:
        # 長編小説の場合
        num_parts = int(re.search(r"全([0-9]+)部分", pre_info).group(1))
    setvalues["num_parts"] = num_parts
    # 小説タイトルの取得
    title = html_text.find("h1").find("a").text
    setvalues["title"] = html_text.find("h1").find("a").text

    # 小説を保存するディレクトリがなければ作成
    setvalues["novel_dir"] = os.path.normpath(
        os.path.join(dir_base, f"{ncode}_{title}"))
    if not os.path.exists(setvalues["novel_dir"]):
        os.mkdir(setvalues["novel_dir"])
    # 取得済みファイル数の確認
    num_files = len(glob.glob(f"{setvalues['novel_dir']}/*.txt"))
    # 続きの小説を取得する場合を考慮
    setvalues["start"] = 0 if num_files == 0 else num_files
    setvalues["num_fetch_rest"] = num_parts

    if result:
        get_novel(setvalues)
    else:
        get_short_story(setvalues)


if __name__ == '__main__':
    main()
