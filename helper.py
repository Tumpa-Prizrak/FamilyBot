import datetime
import json
import sqlite3
from time import sleep

import discord

json_data = json.load(open("config.json"))


def embed_builder(title: str, *, desc: str = None,
                  color: discord.Colour = discord.Colour.green()): return discord.Embed(title=title, description=desc,
                                                                                        color=color)


def do_to_database(command: str, *options, if_short: bool = True):
    dbFilename = json_data["db"]
    while True:
        try:
            conn = sqlite3.connect(dbFilename, timeout=1)
            cursor = conn.cursor()
            if not options:
                returnStr = list(cursor.execute(command))
            else:
                returnStr = list(cursor.execute(command, options))
            conn.commit()
            cursor.close()
            conn.close()
            return returnStr[0] if if_short and len(returnStr) == 1 else returnStr
        except sqlite3.OperationalError as e:
            create_log(e, code="error")
            sleep(1)
            continue


def get_profile_info(person: int):
    if not do_to_database("SELECT * FROM profile WHERE name = ?", person.id):
        do_to_database("INSERT INTO profile values (?, ?, ?)", person.id, None, None)
    return do_to_database("SELECT * FROM profile WHERE name = ?", person.id)


def create_log(message: str, code: str = "ok", logged: bool = True):
    out = f"[{code.upper()}][{str(datetime.datetime.now())[:19]}]: {message}"
    print(out)

    if logged:
        with open(f"logs/log_{datetime.date.today()}.txt", "a", encoding="UTF-8") as file:
            file.write("\n" + out)


def get_max_from_value(variant: dict):
    out = []
    while len(variant) != 0:
        max_value = list(variant.keys())[0]
        for i in variant.keys():
            if variant[i] > variant[max_value]:
                max_value = i
        out.append(max_value)
        variant.pop(max_value)
    return out

minify_text = lambda txt: f'{txt[:-900]}...\n# ...и ещё {len(txt.replace(txt[:-900], ""))} символов' if len(
    txt) >= 1024 else txt