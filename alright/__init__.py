"""
Alright is unofficial Python wrapper for whatsapp web made as an inspiration from PyWhatsApp
allowing you to send messages, images, video and documents programmatically using Python
"""


import os
import sys
import time
import logging
from typing import Optional
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    NoSuchElementException,
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

LOGGER = logging.getLogger()


class WhatsApp(object):
    def __init__(self, driver=None, time_out=600):
        # CJM - 20220419: Added time_out=600 to allow the call with less than 600 sec timeout
        # web.open(f"https://web.whatsapp.com/send?phone={phone_no}&text={quote(message)}")

        self.BASE_URL = "https://web.whatsapp.com/"
        self.suffix_link = "https://web.whatsapp.com/send?phone={mobile}&text&type=phone_number&app_absent=1"

        if not driver:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(
                service=service,
                options=self.chrome_options,
            )

            handles = driver.window_handles
            for _, handle in enumerate(handles):
                if handle != driver.current_window_handle:
                    driver.switch_to.window(handle)
                    driver.close()

        self.driver = driver
        # CJM - 20220419: Added time_out=600 to allow the call with less than 600 sec timeout
        self.wait = WebDriverWait(self.driver, time_out)
        self.cli()
        self.login()
        self.mobile = ""

    @property
    def chrome_options(self):
        chrome_options = Options()
        if sys.platform == "win32":
            chrome_options.add_argument("--profile-directory=Default")
            chrome_options.add_argument("--user-data-dir=C:/Temp/ChromeProfile")
        else:
            chrome_options.add_argument("start-maximized")
            chrome_options.add_argument("--user-data-dir=./User_Data")
        return chrome_options

    def cli(self):
        """
        LOGGER settings  [nCKbr]
        """
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s -- [%(levelname)s] >> %(message)s"
            )
        )
        LOGGER.addHandler(handler)
        LOGGER.setLevel(logging.INFO)

    def login(self):
        self.driver.get(self.BASE_URL)
        self.driver.maximize_window()

        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="pane-side"]')
            )
        )

    def find_user(self, mobile):
        """find_user()
        Makes a user with a given mobile a current target for the wrapper

        Args:
            mobile ([type]): [description]
        """
        try:
            self.mobile = mobile
            link = self.get_phone_link(mobile)
            self.driver.get(link)
            time.sleep(3)
        except UnexpectedAlertPresentException as bug:
            LOGGER.exception(f"An exception occurred: {bug}")
            time.sleep(1)
            self.find_user(mobile)

        # This is the XPath of the message textbox
        inp_xpath = (
            '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[2]'
        )
        # This is the XPath of the "ok button" if the number was not found
        nr_not_found_xpath = (
            '//*[@id="app"]/div/span[2]/div/span/div/div/div/div/div/div[2]/div/button'
        )

        # If the number is NOT a WhatsApp number then there will be an OK Button, not the Message Textbox
        # Test for both situations -> find_elements returns a List
        ctrl_element = self.wait.until(
            lambda ctrl_self: ctrl_self.find_elements(By.XPATH, nr_not_found_xpath)
            or ctrl_self.find_elements(By.XPATH, inp_xpath)
        )

        find = True
        if ctrl_element[0].aria_role == "button":
            # Number Invalid
            find = False

        return find

    def send_message(self, message, timeout=1.0):
        """send_message ()
        Sends a message to a target user

        Args:
            message ([type]): [description]
            :param message: message
            :param timeout:
        """
        try:
            inp_xpath = '//*[@id="main"]/footer/div/div/span[2]/div/div[2]/div/div/div'
            input_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, inp_xpath))
            )
            for line in message.split("\n"):
                input_box.send_keys(line)
                ActionChains(self.driver).key_down(Keys.SHIFT).key_down(
                    Keys.ENTER
                ).key_up(Keys.ENTER).key_up(Keys.SHIFT).perform()
            input_box.send_keys(Keys.ENTER)
            if timeout:
                time.sleep(timeout)
            LOGGER.info(f"Message sent successfuly to {self.mobile}")
        except (NoSuchElementException, Exception) as bug:
            LOGGER.exception(f"Failed to send a message to {self.mobile} - {bug}")
            LOGGER.info("send_message() finished running!")

    def send_file(self, filename: Path, message: Optional[str] = None):
        """send_file()

        Sends a file to target user

        Args:
            filename ([type]): [description]
        """
        try:
            filename = os.path.realpath(filename)
            self.find_attachment()
            document_button = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/span/div/ul/div/div[1]/li/div/input',
                    )
                )
            )
            document_button.send_keys(filename)
            if message:
                self.add_caption(message, media_type="file")
            self.send_attachment()
        except (NoSuchElementException, Exception) as bug:
            LOGGER.exception(f"Failed to send a file to {self.mobile} - {bug}")
        finally:
            LOGGER.info("send_file() finished running!")

    def send_picture(self, picture: Path, message: Optional[str] = None):
        """send_picture ()

        Sends a picture to a target user

        Args:
            picture ([type]): [description]
            :param picture:
            :param message:
        """
        try:
            filename = os.path.realpath(picture)
            self.find_attachment()
            # To send an Image
            img_btn = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/span/div/ul/div/div[2]/li/div/input',
                    )
                )
            )
            img_btn.send_keys(filename)
            if message:
                self.add_caption(message, media_type="image")
            self.send_attachment()
            LOGGER.info(f"Picture has been successfully sent to {self.mobile}")
        except (NoSuchElementException, Exception) as bug:
            LOGGER.exception(f"Failed to send a message to {self.mobile} - {bug}")
        finally:
            LOGGER.info("send_picture() finished running!")

    def send_video(self, video: Path, message: Optional[str] = None):
        """send_video ()
        Sends a video to a target user
        CJM - 2022/06/10: Only if file is less than 14MB (WhatsApp limit is 15MB)

        Args:
            video ([type]): the video file to be sent.
        """
        try:
            filename = os.path.realpath(video)
            f_size = os.path.getsize(filename)
            x = self.convert_bytes_to(f_size, "MB")
            if x < 14:
                # File is less than 14MB
                self.find_attachment()
                # To send a Video
                video_button = self.wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/span/div/ul/div/div[2]/li/div/input',
                        )
                    )
                )

                video_button.send_keys(filename)
                if message:
                    self.add_caption(message, media_type="video")
                self.send_attachment()
                LOGGER.info(f"Video has been successfully sent to {self.mobile}")
            else:
                LOGGER.info(f"Video larger than 14MB")
        except (NoSuchElementException, Exception) as bug:
            LOGGER.exception(f"Failed to send a message to {self.mobile} - {bug}")
        finally:
            LOGGER.info("send_video() finished running!")


    def find_attachment(self):
        clipButton = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="main"]/footer//*[@data-icon="attach-menu-plus"]/..',
                )
            )
        )
        clipButton.click()

    def add_caption(self, message: str, media_type: str = "image"):
        xpath_map = {
            "image": "//*[@id='app']/div/div[2]/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[1]/div[3]/div/div/div/div[1]/div[1]/p",
            "video": "//*[@id='app']/div/div[2]/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[1]/div[3]/div/div/div[1]/div[1]/p",
            "file":  "//*[@id='app']/div/div[2]/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[1]/div[3]/div/div/div[1]/div[1]/p",
        }
        inp_xpath = xpath_map[media_type]
        input_box = self.wait.until(
            EC.presence_of_element_located((By.XPATH, inp_xpath))
        )
        for line in message.split("\n"):
            input_box.send_keys(line)
            ActionChains(self.driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(
                Keys.ENTER
            ).key_up(Keys.SHIFT).perform()

    def send_attachment(self):
        sendButton = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "span[data-icon='send']",
                )
            )
        )
        sendButton.click()

        time.sleep(3)

        # Waiting for the pending clock icon to disappear again - workaround for large files or loading videos.
        self.wait.until_not(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')
            )
        )



    #########################################################################################################


    def get_phone_link(self, mobile) -> str:
        """get_phone_link (), create a link based on whatsapp (wa.me) api

        Args:
            mobile ([type]): [description]

        Returns:
            str: [description]
        """
        return self.suffix_link.format(mobile=mobile)

    def find_by_username(self, username):
        """find_user_by_name ()

        locate existing contact by username or number

        Args:
            username ([type]): [description]
        """
        search_box = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[@id='side']/div[1]/div/div[2]/div[2]/div/div[1]/p"
                )
            )
        )
        search_box.clear()
        search_box.send_keys(username)
        search_box.send_keys(Keys.ENTER)
        try:
            opened_chat = self.driver.find_elements(
                By.XPATH, '//*[@id="main"]/header/div[2]/div/div/div/span'
            )
            if len(opened_chat):
                title = opened_chat[0].text
                if title.upper() == username.upper():
                    LOGGER.info(f'Successfully fetched chat "{username}"')
                return True
            else:
                LOGGER.info(f'It was not possible to fetch chat "{username}"')
                return False
        except NoSuchElementException:
            LOGGER.exception(f'It was not possible to fetch chat "{username}"')
            return False

    def get_list_of_messages(self):
        """get_list_of_messages()

        gets the list of messages in the page
        """
        messages = self.wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//*[@id="pane-side"]/div[2]/div/div/child::div')
            )
        )

        clean_messages = []
        for message in messages:
            _message = message.text.split("\n")
            if len(_message) == 2:
                clean_messages.append(
                    {
                        "sender": _message[0],
                        "time": _message[1],
                        "message": "",
                        "unread": False,
                        "no_of_unread": 0,
                        "group": False,
                    }
                )
            elif len(_message) == 3:
                clean_messages.append(
                    {
                        "sender": _message[0],
                        "time": _message[1],
                        "message": _message[2],
                        "unread": False,
                        "no_of_unread": 0,
                        "group": False,
                    }
                )
            elif len(_message) == 4:
                clean_messages.append(
                    {
                        "sender": _message[0],
                        "time": _message[1],
                        "message": _message[2],
                        "unread": _message[-1].isdigit(),
                        "no_of_unread": int(_message[-1])
                        if _message[-1].isdigit()
                        else 0,
                        "group": False,
                    }
                )
            elif len(_message) == 5:
                clean_messages.append(
                    {
                        "sender": _message[0],
                        "time": _message[1],
                        "message": "",
                        "unread": _message[-1].isdigit(),
                        "no_of_unread": int(_message[-1])
                        if _message[-1].isdigit()
                        else 0,
                        "group": True,
                    }
                )
            elif len(_message) == 6:
                clean_messages.append(
                    {
                        "sender": _message[0],
                        "time": _message[1],
                        "message": _message[4],
                        "unread": _message[-1].isdigit(),
                        "no_of_unread": int(_message[-1])
                        if _message[-1].isdigit()
                        else 0,
                        "group": True,
                    }
                )
            else:
                LOGGER.info(f"Unknown message format: {_message}")
        return clean_messages

    def check_if_given_chat_has_unread_messages(self, query):
        """check_if_given_chat_has_unread_messages() [nCKbr]

        identifies if a given chat has unread messages or not.

        Args:
            query (string): query value to be located in the chat name
        """
        try:
            list_of_messages = self.get_list_of_messages()
            for chat in list_of_messages:
                if query.upper() == chat["sender"].upper():
                    if chat["unread"]:
                        LOGGER.info(
                            f'Yup, {chat["no_of_unread"]} new message(s) on chat <{chat["sender"]}>.'
                        )
                        return True
                    LOGGER.info(f'There are no new messages on chat "{query}".')
                    return False
            LOGGER.info(f'Could not locate chat "{query}"')

        except Exception as bug:
            LOGGER.exception(f"Exception raised while getting first chat: {bug}")

    def fetch_all_unread_chats(self, limit=True, top=50):
        """fetch_all_unread_chats()  [nCKbr]

        retrieve all unread chats.

        Args:
            limit (boolean): should we limit the counting to a certain number of chats (True) or let it count it all (False)? [default = True]
            top (int): once limiting, what is the *approximate* number of chats that should be considered? [generally, there are natural chunks of 10-22]

        DISCLAIMER: Apparently, fetch_all_unread_chats functionallity works on most updated browser versions
        (for example, Chrome Version 102.0.5005.115 (Official Build) (x86_64)). If it fails with you, please
        consider updating your browser while we work on an alternative for non-updated broswers.

        """
        try:
            counter = 0
            pane = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@id="pane-side"]/div[2]')
                )
            )
            list_of_messages = self.get_list_of_messages()
            read_names = []
            names = []
            names_data = []

            while True:
                last_counter = counter
                for item in list_of_messages:
                    name = item["sender"]
                    if name not in read_names:
                        read_names.append(name)
                        counter += 1
                    if item["unread"]:
                        if name not in names:
                            names.append(name)
                            names_data.append(item)

                pane.send_keys(Keys.PAGE_DOWN)
                pane.send_keys(Keys.PAGE_DOWN)

                list_of_messages = self.get_list_of_messages()
                if (
                    last_counter == counter
                    and counter
                    >= int(
                        self.wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//div[@id="pane-side"]/div[2]')
                            )
                        ).get_attribute("aria-rowcount")
                    )
                    * 0.9
                ):
                    break
                if limit and counter >= top:
                    break

                LOGGER.info(f"The counter value at this chunk is: {counter}.")

            if limit:
                LOGGER.info(
                    f"The list of unread chats, considering the first {counter} messages, is: {names}."
                )
            else:
                LOGGER.info(f"The list of all unread chats is: {names}.")
            return names_data

        except Exception as bug:
            LOGGER.exception(f"Exception raised while getting first chat: {bug}")
            return []


    # def logout(self):
    #     prefix = "//div[@id='side']/header/div[2]/div/span/div[3]"
    #     dots_button = self.wait.until(
    #         EC.presence_of_element_located(
    #             (
    #                 By.XPATH,
    #                 f"{prefix}/div[@role='button']",
    #             )
    #         )
    #     )
    #     dots_button.click()
    #
    #     logout_item = self.wait.until(
    #         EC.presence_of_element_located(
    #             (
    #                 By.XPATH,
    #                 f"{prefix}/span/div[1]/ul/li[last()]/div[@role='button']",
    #             )
    #         )
    #     )
    #     logout_item.click()


    def convert_bytes(self, size) -> str:
        # CJM - 2022/06/10:
        # Convert bytes to KB, or MB or GB
        for x in ["bytes", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return "%3.1f %s" % (size, x)
            size /= 1024.0

    def convert_bytes_to(self, size, to):
        # CJM - 2022 / 06 / 10:
        # Returns Bytes as 'KB', 'MB', 'GB', 'TB'
        conv_to = to.upper()
        if conv_to in ["BYTES", "KB", "MB", "GB", "TB"]:
            for x in ["BYTES", "KB", "MB", "GB", "TB"]:
                if x == conv_to:
                    return size
                size /= 1024.0