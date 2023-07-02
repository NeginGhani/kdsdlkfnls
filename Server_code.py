from copy import deepcopy
import random
import threading
import socket

'''character settings'''


class Characters:

    def __init__(self, initial_hp: int, initial_magic_amount: int, magic_dmg: int, magic_rate: float,
                 magic_consumption: int, atk_dmg: int, atk_rate: float, magic_recharge: int,
                 defense_rate: float, name: str, talent_explained: str):
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
        self.talent_explained = talent_explained

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


geralt_talent_def = "Loses 30% of total hp\nAll dmg, mgc rate +20%"
yennefer_talent_def = "Loses 250 mgc energy\nmgc rate, opponent mgc energy:0"
ciri_talent_def = "Loses 15% hp\nOpponent loses 20% of total hp"
eredin_talent_def = "def_rate:0, atk dmg -20%\nHeals for 10% of total hp"
Geralt = Characters(23000, 400, 900, 0.7, 50, 2200, 0.9, 40, 0.6, "Geralt of Rivia", geralt_talent_def)
Yennefer = Characters(19500, 1000, 2900, 0.7, 100, 700, 0.3, 60, 0.4, "Yennefer of Vengerberg", yennefer_talent_def)
Ciri = Characters(25000, 300, 400, 0.5, 75, 2900, 80, 40, 0.5, "Cirilla Fiona Elen Riannon", ciri_talent_def)
Eredin = Characters(36300, 800, 1800, 0.8, 80, 900, 0.4, 60, 0.3, "Eredin Breacc Glas", eredin_talent_def)
characters_list = [Geralt, Yennefer, Ciri, Eredin]


def player_chose_atk(player):
    return Characters.dealing_normal_damage(player)


def player_chose_mgc(player):
    return Characters.dealing_magic_damage(player)


def player_chose_def(player, damage_dealt_by_opponent):
    Characters.defence(player, damage_dealt_by_opponent)


def talent_for_geralt(player: Characters, opponent: Characters):
    player.hp -= player.initial_hp*0.3
    player.magic_dmg *= 1.2
    player.atk_dmg *= 1.2
    player.magic_rate = 0.9


def talent_for_yennefer(player: Characters, opponent: Characters):
    player.magic_amount -= 250
    player.magic_rate = 0
    opponent.magic_amount = 0


def talent_for_ciri(player: Characters, opponent: Characters):
    player.hp *= 0.85
    opponent.hp -= opponent.initial_hp*0.2


def talent_for_eredin(player: Characters, opponent: Characters):
    player.defense_rate = 0
    player.atk_dmg *= 0.8
    player.hp += player.initial_hp*0.1


def player_chose_talent(player, opponent):
    if player.name == "Geralt of Rivia":
        talent_for_geralt(player, opponent)
    elif player.name == "Yennefer of Vengerberg":
        talent_for_yennefer(player, opponent)
    elif player.name == "Cirilla Fiona Elen Riannon":
        talent_for_ciri(player, opponent)
    else:
        talent_for_eredin(player, opponent)


command_list = [player_chose_atk, player_chose_mgc, player_chose_def, player_chose_talent]

'''connection settings'''

host = "127.0.0.1"
port = 61000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host, port))
server_socket.listen(2)

conn_list = []
address_list = []


def socket_accept():
    for i in range(0, 2):
        conn, address = server_socket.accept()
        # address[0]: ip   address[1]: port
        conn_list.append(conn)
        address_list.append(address)


connection_thread = threading.Thread(target=socket_accept)
connection_thread.start()
connection_thread.join()
print("connection with both clients has been established")
clients_choice_dic = dict()
name_and_conn_dic = dict()
''' pl = {'pl_conn_obj': player_name}    '''
pl1 = dict()
pl2 = dict()
player1_character: Characters
player2_character: Characters
pl1_conn_obj = conn_list[0]
pl2_conn_obj = conn_list[1]


'''note for myself: this func waits for both clients to send their data
then it'll take the next step which means the lines after calling the func'''


def get_data_from_both_clients():

    def socket_receive_thread_target(conn):
        global clients_choice_dic
        player_choice = conn.recv(1024)
        clients_choice_dic[str(conn)] = (player_choice.decode('utf-8'))

    receive_thread_list = []
    for conn in conn_list:
        receive_thread = threading.Thread(target=socket_receive_thread_target, args=[conn])
        receive_thread_list.append(receive_thread)
        receive_thread.start()
    for receive_thread in receive_thread_list:
        receive_thread.join()


def send_data_to_clients(data):
    for conn in conn_list:
        conn.send(bytes(data, 'utf-8'))


'''each player has a dic {conn_obj: player_name}'''


def get_name_from_players():
    global name_and_conn_dic
    global pl1
    global pl2
    global pl1_conn_obj
    global pl2_conn_obj
    get_data_from_both_clients()
    name_and_conn_dic = deepcopy(clients_choice_dic)
    pl1[str(pl1_conn_obj)] = name_and_conn_dic[str(pl1_conn_obj)]
    pl2[str(pl1_conn_obj)] = name_and_conn_dic[str(pl1_conn_obj)]


def assign_character_to_players():
    global player1_character
    global player2_character
    get_data_from_both_clients()
    for char in characters_list:
        if clients_choice_dic[str(conn_list[0])] == char.name:
            print(clients_choice_dic[str(conn_list[0])])
            player1_character = deepcopy(char)
        if clients_choice_dic[str(conn_list[1])] == char.name:
            print(clients_choice_dic[str(conn_list[1])])
            player2_character =deepcopy(char)


def process_data_from_clients():
    i = int(clients_choice_dic[pl1_conn_obj])
    j = int(clients_choice_dic[pl2_conn_obj])
    if i < 3:
        command_list[i](player2_character)
    else:
        command_list[i](player1_character, player2_character)
    if j < 3:
        command_list[j](player1_character)
    else:
        command_list[j](player2_character, player1_character)


def prepare_and_send_data():

    ee = f'{pl1[pl1_conn_obj]}...{player1_character.hp}...{player1_character.magic_amount}|'
    oo = f'{pl2[pl2_conn_obj]}...{player2_character.hp}...{player2_character.magic_amount}'
    data = ee+oo
    for conn in conn_list:
        conn.send(bytes(data, 'utf-8'))


def get_index_for_clients(opposite_char: Characters):
    for char in characters_list:
        if char.name == opposite_char.name:
            return characters_list.index(char)


def main():
    get_name_from_players()
    assign_character_to_players()
    print(f'p1: {player1_character.name}')
    print(f"p2: {player2_character.name}")

    pl1_conn_obj.send(bytes(str(get_index_for_clients(player2_character)), 'utf-8'))
    pl2_conn_obj.send(bytes(str(get_index_for_clients(player1_character)), 'utf-8'))

    while player1_character.hp != 0 or player2_character.hp != 0:
        get_data_from_both_clients()
        process_data_from_clients()
        prepare_and_send_data()


main()
