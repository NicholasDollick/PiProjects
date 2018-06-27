import sqlite3
import RPi.GPIO as GPIO
import SimpleMFRC522
import time
import os
import ascii

def led_startup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(22, GPIO.OUT)
    GPIO.setup(4, GPIO.OUT)
    GPIO.setup(26, GPIO.OUT)
    GPIO.setup(5, GPIO.OUT)
    GPIO.setup(16, GPIO.OUT)
    GPIO.setup(20, GPIO.OUT)

def led_correct():
    for i in range(3):
        GPIO.output(26, True)
        GPIO.output(5, True)
        time.sleep(.1)
        GPIO.output(26, False)
        GPIO.output(5, False)
        time.sleep(.1)

def led_incorrect():
    for i in range(3):
        GPIO.output(22, True)
        GPIO.output(4, True)
        time.sleep(.1)
        GPIO.output(22, False)
        GPIO.output(4, False)
        time.sleep(.1)
        
def led_notif_flicker():
    for i in range(2):
        GPIO.output(16, True)
        time.sleep(.1)
        GPIO.output(16, False)
        time.sleep(.1)
        GPIO.output(20, True)
        time.sleep(.1)
        GPIO.output(20, False)
        
def unlock_cycle():
    GPIO.output(20, True)
    time.sleep(.1)
    GPIO.output(20, False)
    GPIO.output(16, True)
    time.sleep(.1)
    GPIO.output(16, False)
    GPIO.output(5, True)
    time.sleep(.1)
    GPIO.output(5, False)
    GPIO.output(26, True)
    time.sleep(.1)
    GPIO.output(26, False)
    GPIO.output(4, True)
    time.sleep(.1)
    GPIO.output(4, False)
    GPIO.output(22, True)
    time.sleep(.1)
    GPIO.output(22, False)
    
def led_off():
    GPIO.output(22, False)
    GPIO.output(4, False)
    GPIO.output(26, False)
    GPIO.output(5, False)
    GPIO.output(16, False)
    GPIO.output(20, False)

def listen():
    auth = []
    auth_ids = curs.execute("SELECT * FROM auth").fetchall()
    
    for id in auth_ids:
        auth.append(id[0])
    
    print("[*] Scan card")
    try:
        while(True):
            GPIO.output(16, True)
            id, text = reader.read()
            if(id in auth):
                GPIO.output(16, False)
                led_correct()
                print("[+] Card is authorized")
                time.sleep(.1)
                unlock_cycle()
                break
            else:
                GPIO.output(16, False)
                led_incorrect()
                print("[-] Card is unauthorized")
                GPIO.output(16, True)
    except Exception:
        print ("crash during listen")

def update_auth(query):
    admin_ids = curs.execute("SELECT * FROM admin").fetchall()
    print("[*] Scan card now")
    card_id = 0
    try:
        GPIO.output(20, True)
        while(True):
            card_id, text = reader.read()
            if(card_id != 0):
                GPIO.output(20, False)
                led_notif_flicker()
                GPIO.output(20, True)
                break
        print("[*] Scan admin card to confirm action")
        while(True):
            admin_id, text = reader.read()
            if(admin_id == admin_ids[0][0]):
                led_correct()
                GPIO.output(20, False)
                print("[+] Approved")
                curs.execute(query, (card_id,))
                conn.commit()
                time.sleep(1)
                break
    except Exception:
        print("crash while trying to update card")

def run():
    action = ""
    ascii.splash()
    print()
    print("[*] Commands: ")
    print("           1) Add Card")
    print("           2) Remove Card")
    print("           3) Scan Card")
    print("          99) Exit")
    print()
    
    while(action != "99"):
        action = input("root@hotel:~$ ")
        
        if(action == "1"):
           update_auth("INSERT INTO auth(id) VALUES(?)")
        
        if(action == "2"):
            update_auth("DELETE FROM auth WHERE id = ?")
        
        if(action == "3"):
            listen()
        
        if(action == "admin_set"):
            curs.execute("""INSERT INTO admin(id) values(209992049463)""")
            conn.commit()
  
def initialize_db():    
    curs.execute("""CREATE TABLE IF NOT EXISTS auth(id INTEGER)""")
    conn.commit()
    curs.execute("""CREATE TABLE IF NOT EXISTS admin(id INTEGER)""")
    conn.commit()
  
reader = SimpleMFRC522.SimpleMFRC522()

conn = sqlite3.connect('test.db')
curs = conn.cursor()

initialize_db()
led_startup()
run()
led_off()
GPIO.cleanup()
    