import sqlite3
import RPi.GPIO as GPIO
import SimpleMFRC522
import time

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
    
def led_off():
    GPIO.output(22, False)
    GPIO.output(4, False)
    GPIO.output(26, False)
    GPIO.output(5, False)
    GPIO.output(16, False)
    GPIO.output(20, False)

def listen():
    flag = True
    auth = []
    auth_ids = curs.execute("SELECT * FROM auth").fetchall()
    
    for id in auth_ids:
        auth.append(id[0])
    
    try:
        while(flag):
            GPIO.output(16, True)
            id, text = reader.read()
            if(id in auth):
                GPIO.output(16, False)
                led_correct()
                print("Card is authorized")
                flag = False
            else:
                GPIO.output(16, False)
                led_incorrect()
                print("Card is unauthorized")
                GPIO.output(16, True)
    except Exception:
        print ("crash during listen")

def add_auth():
    admin_ids = curs.execute("SELECT * FROM admin").fetchall()
    print("Scan card to add")
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
        print("Scan admin card to confirm action")
        while(True):
            admin_id, text = reader.read()
            if(admin_id == admin_ids[0][0]):
                led_correct()
                GPIO.output(20, False)
                print("[+] Approved")
                #print(card_id)
                curs.execute("INSERT INTO auth(id) VALUES(?)", (card_id,))
                conn.commit()
                time.sleep(1)
                break
    except Exception:
        print("crash while trying to add card")

def remove_auth():
    admin_ids = curs.execute("SELECT * FROM admin").fetchall()
    print("Scan card to remove")
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
        print("Scan admin card to confirm action")
        while(True):
            admin_id, text = reader.read()
            if(admin_id == admin_ids[0][0]):
                led_correct()
                GPIO.output(20, False)
                print("[+] Approved")
                #print(card_id)
                curs.execute("DELETE FROM auth WHERE id = ?", (card_id,))
                conn.commit()
                time.sleep(1)
                break
    except Exception:
        print("crash while trying to remove card")

def run():
    action = ""
    print()
    print("[*] Commands: ")
    print("              1) Add Card")
    print("              2) Remove Card")
    print("              3) Scan Card")
    print("             99) Exit")
    print()
    
    while(action != "99"):
        action = input("root@hotel:~$ ")
        
        if(action == "1"):
           add_auth()
        
        if(action == "2"):
            remove_auth()
        
        if(action == "3"):
            listen()
        
        if(action == "admin_set"):
            curs.execute("""INSERT INTO admin(id) values(209992049463)""")
            conn.commit()
  
  
reader = SimpleMFRC522.SimpleMFRC522()

led_startup()

conn = sqlite3.connect('test.db')
curs = conn.cursor()

curs.execute("""CREATE TABLE IF NOT EXISTS auth(id INTEGER)""")
conn.commit()
curs.execute("""CREATE TABLE IF NOT EXISTS admin(id INTEGER)""")
conn.commit()

run()
led_off()
GPIO.cleanup()
    