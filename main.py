import requests
import json
import secrets
import string
import time
import re
import webbrowser
import threading

import pyperclip
import customtkinter


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Account Generator")
        self.geometry("360x110")

        self.email_label = customtkinter.CTkLabel(
            self, text="Почта: ", width=200, height=30)
        self.email_label.place(x=10, y=10)

        self.email_copy_button = customtkinter.CTkButton(
            self, text="📄", width=25, height=25, 
            command=lambda: pyperclip.copy(self.email))
        self.email_copy_button.place(x=320, y=10)

        self.password_label = customtkinter.CTkLabel(
            self, text="Пароль: ",)
        self.password_label.place(x=10, y=40)

        self.confirm_button = customtkinter.CTkButton(
            self, text="Подтвердить", width=340, height=30,
            command=lambda: webbrowser.open_new(self.url))
        self.confirm_button.place(x=10, y=70)

        self.reload_button = customtkinter.CTkButton(
            self, text="🔄", width=25, height=25,
            command=self.reload)
        self.reload_button.place(x=320, y=40)

        self.create_email()

        threading.Thread(target=self.get_messages).start()

    def create_email(self):
        self.confirm_button.configure(state=customtkinter.DISABLED)

        alphabet = string.ascii_lowercase + string.digits
        address = ''.join(secrets.choice(alphabet) for _ in range(12))
        address = "matswuuu_" + address

        account = {
            "address": f"{address}@internetkeno.com",
            "password": "123"
        }

        requests.post("https://api.mail.tm/accounts", json=account)

        r = requests.post("https://api.mail.tm/token", json=account)
        self.token = {
            "authorization": "Bearer " + json.loads(r.text)["token"]
        }
        
        self.email = account["address"] 
        self.password = account["password"]

        pyperclip.copy(self.email)
        
        self.email_label.configure(text=f"Почта: {self.email}")
        self.password_label.configure(text=f"Пароль: {self.password}")
        self.reload_button.configure(state=customtkinter.NORMAL)

    def get_messages(self):
        while True:
            r = requests.get("https://api.mail.tm/messages?page=1", headers=self.token)
            mail = json.loads(r.text)

            if mail["hydra:member"] != []:
                id = mail["hydra:member"][0]["id"]
                r = requests.get(f"https://api.mail.tm/messages/{id}", headers=self.token)
                index = json.loads(r.text)["text"]
                
                nick = index.split(" ")[1].replace("РЕГИСТРАЦИИ", "").replace("\n", "")
                self.url = re.findall(r'(https?://[^\s]+)', index)[3].replace("]", "")

                self.confirm_button.configure(state=customtkinter.NORMAL, 
                                              text=f"Подтвердить {nick}")

                break

            time.sleep(10)

    def reload(self):
        self.reload_button.configure(state=customtkinter.DISABLED)
        threading.Thread(target=self.create_email).start()

if __name__ == "__main__":
    app = App()
    app.mainloop()
