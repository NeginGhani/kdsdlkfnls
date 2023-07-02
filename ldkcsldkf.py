from copy import deepcopy
import random
import socket
import threading
import tkinter as tk

'''character settings'''


class Characters:

    def __init__(self, initial_hp: int, initial_magic_amount: int, magic_dmg: int, magic_rate: float,
                 magic_consumption: int, atk_dmg: int, atk_rate: float, magic_recharge: int,
                 defense_rate: float, name: str):
        self.initial_hp = initial_hp
        self.hp = deepcopy(initial_hp)
        self.initial_magic_amount = initial_magic_amount
        self.magic_amount = deepcopy(initial_magic_amount)
        self.magic_dmg = magic_dmg
        self.magic_rate = magic_rate
        self.magic_consumption = magic_consumption
        self.atk_dmg = atk_dmg
        self.atk_rate = atk_rate
        self.defense_rate = defense_rate
        self.magic_recharge = magic_recharge
        self.name = name

    def dealing_normal_damage(self):
        possible_damages = [0, self.atk_dmg]
        return random.choices(possible_damages, weights=(1-self.atk_rate, self.atk_rate), k=1)

    def dealing_magic_damage(self):
        possible_damages = [0, self.magic_dmg]
        magic_attack_result = random.choices(possible_damages, weights=(1-self.magic_rate, self.magic_rate), k=1)
        self.magic_amount -= self.magic_consumption
        if magic_attack_result != 0:
            self.magic_amount = sorted([0, self.magic_amount+self.magic_recharge, self.initial_magic_amount])[1]
        return magic_attack_result

    def taking_damage(self, hp_loss):
        self.hp = sorted([0, self.hp-hp_loss])[1]

    def defence(self, damage_dealt_by_opponent):
        possible_defense = [0, 1]
        defense_result = random.choices(possible_defense, weights=(self.defense_rate, 1-self.defense_rate), k=1)
        return defense_result*damage_dealt_by_opponent


Geralt = Characters(23000, 400, 900, 0.7, 50, 2200, 0.9, 40, 0.6, "Geralt of Rivia")
Yennefer = Characters(19500, 1000, 2900, 0.7, 100, 700, 0.3, 60, 0.4, "Yennefer of Vengerberg")
Ciri = Characters(25000, 300, 400, 0.5, 75, 2900, 80, 40, 0.5, "Cirilla Fiona Elen Riannon")
Eredin = Characters(36300, 800, 1800, 0.8, 80, 900, 0.4, 60, 0.3, "Eredin Breacc Glas")
characters_list = [Geralt, Yennefer, Ciri, Eredin]
my_char: Characters
opponent_char: Characters
my_name: str
run_arena = False
'''connection settings'''

port = 61000
host = '127.0.0.1'
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))


def send_data_to_server(data):
    client_socket.send(bytes(data, 'utf-8'))


def get_data_from_server():
    data = client_socket.recv(1024).decode("utf-8")
    return data


'''gui settings'''
'''login page creation part'''


def create_login_page():
    def login_btn():
        global my_name
        my_name = get_name_entry.get()
        if len(my_name) == 0:
            tk.Label(master=result_frame, text="please enter a name", bg="red").place(y=150, x=550)
        else:
            login_window.destroy()
            client_socket.send(bytes(my_name, 'utf-8'))

    login_window = tk.Tk()
    login_window.title("Login page")
    login_window.geometry('1200x600')
    result_frame = tk.Frame(height=300, width=1200)
    result_frame.pack(side=tk.BOTTOM, expand=True)
    get_name_entry = tk.Entry()
    get_name_label = tk.Label(text="Welcome!\nplease enter a name to proceed")
    login_button = tk.Button(text="login", command=login_btn, bg="gray")
    get_name_label.pack(side=tk.TOP, pady=15)
    get_name_entry.pack(side=tk.TOP, pady=15)
    login_button.pack(side=tk.TOP, pady=15)
    login_window.mainloop()


'''menu creation part'''


def create_stats(character):
    stt = ""
    stt += f'{character.name}\n\n'
    stt += f'hp: {character.hp}\n'
    stt += f'atk dmg: {character.atk_dmg}\n'
    stt += f'atk rate: {character.atk_rate * 100}%\n'
    stt += f'mgc amount: {character.initial_magic_amount}\n'
    stt += f'mgc dmg: {character.magic_dmg}\n'
    stt += f'mgc rate: {character.magic_rate * 100}%\n'
    stt += f'mgc consumption: {character.magic_consumption}\n'
    stt += f'mgc recharge: {character.magic_recharge}\n'
    stt += f'defense rate: {character.defense_rate * 100}%'
    return stt


def insert_stats(character, master_frame):
    tk.Label(master=master_frame, text=f'{create_stats(character)}').place(x=75, y=380)


def insert_btn(bttn):
    bttn.place(x=100, y=570)


def create_menu_window():

    def choosing_geralt():
        global my_char
        client_socket.send(bytes(Geralt.name, 'utf-8'))
        my_char = deepcopy(Geralt)
        character_menu_window.destroy()

    def choosing_yennefer():
        global my_char
        client_socket.send(bytes(Yennefer.name, 'utf-8'))
        my_char = deepcopy(Yennefer)
        character_menu_window.destroy()

    def choosing_ciri():
        global my_char
        client_socket.send(bytes(Ciri.name, 'utf-8'))
        my_char = deepcopy(Ciri)
        character_menu_window.destroy()

    def choosing_eredin():
        global my_char
        client_socket.send(bytes(Eredin.name, 'utf-8'))
        my_char = deepcopy(Eredin)
        character_menu_window.destroy()

    character_menu_window = tk.Tk()
    character_menu_window.title("characters")
    character_menu_window.geometry('1200x600')
    geralt_frame = tk.Frame(master=character_menu_window, height=600, width=300, bg="gray")
    yennefer_frame = tk.Frame(master=character_menu_window, height=600, width=300, bg="#71597d")
    ciri_frame = tk.Frame(master=character_menu_window, height=600, width=300, bg="#d2d2ee")
    eredin_frame = tk.Frame(master=character_menu_window, height=600, width=300, bg="#9C7872")
    geralt_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    yennefer_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    ciri_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    eredin_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    geralt_pfp = tk.PhotoImage(file="GERALT.png")
    geralt_pfp.image = geralt_pfp
    tk.Label(master=geralt_frame, image=geralt_pfp).place(x=50, y=50)
    yennefer_pfp = tk.PhotoImage(file="YENNEFER.png")
    yennefer_pfp.image = yennefer_pfp
    tk.Label(master=yennefer_frame, image=yennefer_pfp).place(x=50, y=50)
    ciri_pfp = tk.PhotoImage(file="CIRI.png")
    ciri_pfp.image = ciri_pfp
    tk.Label(master=ciri_frame, image=ciri_pfp).place(x=50, y=50)
    eredin_pfp = tk.PhotoImage(file="EREDIN.png")
    eredin_pfp.image = eredin_pfp
    tk.Label(master=eredin_frame, image=eredin_pfp).place(x=50, y=50)

    pick_geralt_btn = tk.Button(master=geralt_frame, command=choosing_geralt, text="Geralt")
    pick_yennefer_btn = tk.Button(master=yennefer_frame, command=choosing_yennefer, text="Yennefer")
    pick_ciri_btn = tk.Button(master=ciri_frame, command=choosing_ciri, text="Ciri")
    pick_eredin_btn = tk.Button(master=eredin_frame, command=choosing_eredin, text="Eredin")
    btn_list = [pick_geralt_btn, pick_yennefer_btn, pick_ciri_btn, pick_eredin_btn]
    frame_list = [geralt_frame, yennefer_frame, ciri_frame, eredin_frame]

    for btn in btn_list:
        insert_btn(btn)
    for i in range(0, 4):
        insert_stats(characters_list[i], frame_list[i])

    character_menu_window.mainloop()


def create_loading_window():
    loading_window = tk.Tk()
    loading_window.title("waiting for players")
    loading_window.geometry('1200x600')
    loading_window.configure(bg='#589e7f')
    wait_str = "please wait for your opponent to choose their character"
    waiting_for_opponent_label = tk.Label(master=loading_window, text=wait_str, bg='#589e7f')
    waiting_for_opponent_label.pack(pady=200)

    def close_loading_window():
        global run_arena
        global opponent_char
        opponent_char_index = int(client_socket.recv(1024).decode('utf-8'))
        opponent_char = deepcopy(characters_list[opponent_char_index])
        print(opponent_char.name)
        loading_window.destroy()
        run_arena = True

    waiting_window_thread = threading.Thread(target=close_loading_window)
    waiting_window_thread.start()
    loading_window.mainloop()


def normal_atk():
    client_socket.send(bytes("0", 'utf-8'))


def magic_atk():
    client_socket.send(bytes("1", 'utf-8'))


def defense():
    client_socket.send(bytes("2", 'utf-8'))


def talent():
    client_socket.send(bytes("3", 'utf-8'))

#arena


arena = tk.Tk()
arena.title("Fight!")
arena.geometry('1200x600')
my_frame = tk.Frame(master=arena, height=600, width=600, bg="#587A54")
opponent_frame = tk.Frame(master=arena, height=600, width=600, bg="#7A524E")
my_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
opponent_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
my_info = tk.Canvas(master=my_frame, height=150, width=600, bg="#6A7A6C")  # canvas for bars
opponent_info = tk.Canvas(master=opponent_frame, height=150, width=600, bg="#773449")
my_info.pack(side=tk.TOP, fill=tk.X)
opponent_info.pack(side=tk.TOP, fill=tk.X)

btns_frame = tk.Frame(master=my_frame, height=100, width=600, bg="#6A7A6C")
atk_btn = tk.Button(master=btns_frame, text="Normal attack")
mgc_btn = tk.Button(master=btns_frame, text="Magic attack")
defense_btn = tk.Button(master=btns_frame, text="Defense")
talent_btn = tk.Button(master=btns_frame, text="Special attack", bg="gold")
atk_btn.pack(side=tk.LEFT, pady=30, padx=10)
mgc_btn.pack(side=tk.LEFT, pady=30, padx=10)
defense_btn.pack(side=tk.LEFT, pady=30, padx=10)
talent_btn.pack(side=tk.LEFT, pady=30, padx=10)
btns_frame.pack(side=tk.BOTTOM, fill=tk.X)


def process_battle_data():
    data = get_data_from_server()
    split_data: list
    split_data = data.split("|")
    split_data[0] = split_data[0].split("...")
    split_data[1] = split_data[1].split("...")
    for item in split_data:

        if item[0] == my_name:
            my_char.hp = item[1]
            my_char.magic_amount = item[2]
        else:
            opponent_char.hp = item[1]
            opponent_char.magic_amount = item[2]


def set_bars():
    while True:
        process_battle_data()
        my_hp_scale = (my_char.hp * 370 / my_char.initial_hp) + 210
        my_mgc_scale = (my_char.magic_amount * 370 / my_char.initial_magic_amount) + 210
        my_info.create_rectangle(210, 20, 580, 95, fill="#731F1C")
        my_info.create_rectangle(210, 20, my_hp_scale, 95, fill="#1E7A10")
        my_info.create_rectangle(210, 105, 580, 135, fill="black")
        my_info.create_rectangle(210, 105, my_mgc_scale, 135, fill="#E2C276")
        opponent_hp_scale = (opponent_char.hp * 370 / opponent_char.initial_hp) + 210
        opponent_mgc_scale = (opponent_char.magic_amount * 370 / opponent_char.initial_magic_amount) + 210
        opponent_info.create_rectangle(210, 20, 580, 95, fill="#731F1C")
        opponent_info.create_rectangle(210, 20, opponent_hp_scale, 95, fill="#1E7A10")
        opponent_info.create_rectangle(210, 105, 580, 135, fill="black")
        opponent_info.create_rectangle(210, 105, opponent_mgc_scale, 135, fill="#E2C276")


hopefully_itll_work_thread = threading.Thread(target=set_bars)
create_login_page()
create_menu_window()
hopefully_itll_work_thread.start()
create_loading_window()
