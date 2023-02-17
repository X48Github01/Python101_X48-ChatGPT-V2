import tkinter as tk
import openai
import os
import configparser
from configparser import ConfigParser
import logging
from logging.handlers import RotatingFileHandler

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a rotating file handler
handler = RotatingFileHandler("answers.log", maxBytes=1000000, backupCount=5)
handler.setLevel(logging.INFO)

# Create a formatter and add it to the handler
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


dbconf = ConfigParser()
dbconf.read_file(open("config.ini"))

API_KEY = dbconf.get("SETTING","API_KEY")
# Set up your API key
# #! สามารถขอ API_KEY เพื่อเชื่อมต่อได้ที่ Website OpenAi.com
openai.api_key = API_KEY

# Set up the initial prompt and context
# #! ตั้งค่าการแสดงผลเบื้องต้น OpenAI ตอนที่ผมคุยด้วย เขามีชื่อเล่นว่า Sydney
prompt = "Hello, my name is Sydney. What can I help you with today?"

# Define a function to get the AI's response
# #! การตั้งค่าสำหรับ OpenAI : Davinci 001-003 โปรดศึกษาเรื่อง Engine ใน Official Website ของ OpenAI อีกทีครับ ล่าสุดใช้ Davinci-003
#! temperature คือ ตัวแปรการตอบคำถามของ Sydney ChatGPT ค่าปกติคือ 0.5 หากใช้เกิน 1 ขึ้นไป (สูงสุด 2) คำตอบจะนอกเหนือจากจินตนาการมากขึ้น (อาจตอบไม่ตรงคำถามมากขึ้น) เหมาะสำหรับการเขียนบทความ จะร่ายยาวขึ้น
#! ยิ่งร่ายยาว คำตอบจะรอนานมากยิ่งขึ้น โปรแกรมไม่ได้ค้างระหว่างรอคำตอบ แต่รอการพิมพ์ทีละตัวจากเซิฟเวอร์ แล้วมาตอบกลับทีเดียว
def get_response(input_text):
    prompt_with_context = f"{prompt} {input_text}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_with_context,
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.5
    )
    logger.info(response.choices[0].text)
    return response.choices[0].text.strip()

# Define a function to handle user input
# #! เป็นการตั้งค่าส่วนที่พูดคุยใน Log History กับ Sydney สามารถตั้งค่า Font และ Font Color ได้
def send_message(event=None):
    user_message = my_message.get()
    if user_message.strip() == "":
        return
    my_message.set("")
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "You : " + user_message + "\n")
    chat_log.tag_add("user", "end-5c", "end")
    chat_log.tag_config("user", foreground="#442265")
    ai_response = get_response(user_message)
    chat_log.insert(tk.END, "Sydney : " + ai_response + "\n\n")
    chat_log.tag_add("ai", "end-8c", "end")
    chat_log.tag_config("ai", foreground="#442265")
    chat_log.config(state=tk.DISABLED)
    chat_log.yview(tk.END)

# Set up the GUI
# #! ตั้งค่า Default Size เพื่อนๆสามารถตั้งมากกว่านี้ได้ โดยผมเลือก 800x600 อันเล็กๆเพื่อเปิดใช้งานพิมพ์ถามคำถามง่ายๆ ไม่รกหน้าจอ
root = tk.Tk()
root.title("Sydney Chat (ChatGPT) by X4815162342")
root.geometry("800x600")
#root.geometry("500x400")
#root.geometry("1280x960")
#root.geometry("1920x1080")
#! สำหรับ Fix Windows Size : resizeable จะไม่สามารถขยายจอได้
#root.resizable(0, 0)

# Set up the chat log
# #! ส่วนนี้เป็นการตั้งค่า Chat Log โดยเพื่อนๆสามารถแก้ไข Font และ สีของ Background ได้
chat_log = tk.Text(root, bd=0, bg="#ffffff", height="8", width="50", font="Arial", wrap=tk.WORD)
chat_log.config(state=tk.DISABLED)
chat_log.place(x=6, y=6, height=386, width=370)
scrollbar = tk.Scrollbar(chat_log)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar.config(command=chat_log.yview)
chat_log.config(yscrollcommand=scrollbar.set, background="#ffffff", font=("Arial", 12))

# Set up the scrollbar
# #! ส่วนนี้เป็น Scrollbar เนื่องจาก Version นี้สามารถเห็น History Log ย้อนหลังที่พูดคุยได้ ทำให้เพื่อนๆสามารถย้อนอ่านข้างบนโดยใช้ Scrollbar Mouse เลื่อนขึ้นไป สามารถแก้ไข cusror = xx รูปแบบอื่นได้
scrollbar = tk.Scrollbar(root, command=chat_log.yview, cursor="heart")
chat_log["yscrollcommand"] = scrollbar.set

# Set up the message box
#! ส่วนนี้เป็นการตั้งค่า Message Box สำหรับพิมพ์คำถาม แก้ไข Font และ Background ได้
my_message = tk.StringVar()
my_message.set("")
message_box = tk.Entry(root, textvariable=my_message, bd=0, bg="#ffffff", font="Arial")
message_box.bind("<Return>", send_message)
message_box.place(x=10, y=410, height=80, width=280)
message_box.focus_set()  # Set focus on the message box


# Set up the send button
#! ส่วนนี้เป็นการตั้งค่าปุ่มกดส่ง Send Button สีเขียวๆใหญ่ๆ หรือกด Enter ก็ได้ครับ สามารถแก้ไขขนาดและ font สีพื้นหลังได้
send_button = tk.Button(root, font=("Verdana", 12, "bold"), text="Send", width="10", height=4,
                        bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff',
                        command=send_message)
send_button.place(x=372, y=400)

# Place all the components on the screen
#! เป็นการตั้งค่าการวางตำแหน่งบนหน้าจอตามตาราง
chat_log.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
scrollbar.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")
message_box.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
send_button.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="nsew")

# Configure the root window to resize properly
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Set the background color of the chat log
chat_log.configure(bg="#ffffff")
# Start the GUI main loop
root.mainloop()
