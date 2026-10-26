from tkinter import *
from tkinter import messagebox
import json
import os
import hashlib

root = Tk()
root.title("Численность населения")
root.geometry("700x500")

auth_file = "auth.json"
hidden_citties = set()

start_admin_salt = "64b18493c23a422d8c2d7c296a6d71b9"
start_admin_hash = "e9a5df725f2509dd9fa1d6990f842c37eb358e6488784f8221887723942ca401"
start_moder_salt = "a1b2c3d4e5f60718293a4b5c6d7e8f90"
start_moder_password = "123"

auth = {}
role = None

data_file = "cities.json"

data = {
    "Москва": 13274285,
    "Санкт-Петербург": 5652922,
    "Новосибирск": 1637266,
    "Екатеринбург": 1548187,
    "Казань": 1329825,
    "Красноярск": 1211756,
    "Нижний Новгород": 1198245,
    "Челябинск": 1176770,
    "Уфа": 1166098,
    "Краснодар": 1154885,
    "Самара": 1154223,
    "Ростов-на-Дону": 1143123,
    "Омск": 1101367,
    "Воронеж": 1041722,
    "Пермь": 1027518,
    "Волгоград": 1012219
}
def save_data():
    load = {"cities": data, "hidden": list(hidden_citties)}
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(load, f, ensure_ascii=False, indent=2)

def load_data():
    if not os.path.exists(data_file):
        return
    try:
        with open(data_file, "r", encoding='utf-8') as f:
            loaded = json.load(f)
        if isinstance(loaded, dict) and 'cities' in loaded:
            data.clear()
            data.update(loaded["cities"])
            hidden_citties.clear()
            hidden_citties.update(loaded.get("hidden", []))
        else:
            data.clear()
            data.update(loaded)
            hidden_citties.clear()
    except Exception:
        pass


def show_admin_screen():
    if role == "admin":
        delite_button.place(relx=0.55, rely=0.80)
        status_text.place(relx=0.05, rely=0.72)
        update_stats()
        admin_title_label.config(text="Панель администратора")
    else:
        delite_button.place_forget()
        status_text.place_forget()
        admin_title_label.config(text="Панель модератора")
    search_frame.place_forget()
    admin_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

def show_search_screen():
    global role
    role = None
    admin_frame.place_forget()
    search_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def save_auth():
    with open(auth_file, 'w', encoding="utf-8") as f:
        json.dump(auth, f, ensure_ascii=False, indent=2)

def load_auth():
    global auth
    flag = False
    if os.path.exists(auth_file):
        try:
            with open(auth_file, 'r', encoding='utf-8') as f:
                auth = json.load(f)
        except Exception:
            auth = {}
    else:
        auth = {}

    if "admin" not in auth:
        auth["admin"] = {"salt": start_admin_salt, "hash": start_admin_hash}
        flag = True
    if "moderator" not in auth:
        auth["moderator"] = {"salt": start_moder_salt, "hash": hash_password(start_moder_password, start_moder_salt)}
        flag = True

    if flag:
        save_auth()

def check_password(event=None):
    global role
    enter_pas = pw.get()

    for r in ["admin", "moderator"]:
        if hash_password(enter_pas, auth[r]["salt"]) == auth[r]["hash"]:
            role = r
            pw.set("")
            pw_entry.place_forget()
            refresh_admin_list()
            show_admin_screen()
            return
    messagebox.showerror("ОШИБКА", "Неверный пароль!!!")

def show_password_entry():
    pw_entry.place(relx=0.305, rely=0.71)
    pw_entry.focus_set()

def reset_password():
    dlg = Toplevel(root)
    dlg.title("Смена пароля")
    dlg.geometry("320x220")
    dlg.transient(root)
    dlg.grab_set()

    target= StringVar(value=role)

    if role == "admin":
        Radiobutton(dlg, text="Своего", variable=target, value="admin").place(relx=0.1, rely=0.1)
        Radiobutton(dlg, text="Модератора", variable=target, value="moderator").place(relx=0.48, rely=0.1)

    Label(dlg, text="Новый пароль: ").place(relx=0.1, rely=0.2)
    new_var1 = StringVar()
    Entry(dlg, textvariable=new_var1, show="*", width=35).place(relx=0.1, rely=0.32)

    Label(dlg, text="Повторите: ").place(relx=0.1, rely=0.45)
    new_var2 = StringVar()
    Entry(dlg, textvariable=new_var2, show="*", width=35).place(relx=0.1, rely=0.57)

    msg = StringVar()
    Label(dlg, textvariable=msg, fg="red").place(relx=0.1, rely=0.68)

    def apply():
        n1, n2 = new_var1.get(), new_var2.get()
        t = target.get()

        if n1 =="":
            msg.set("Пустой пароль")
            return
        if n1!=n2:
            msg.set("Пароли не совпадают!!!!")
            return

        auth[t]["salt"] = os.urandom(16).hex()
        auth[t]["hash"] = hash_password(n1, auth[t]["salt"])
        save_auth()
        dlg.destroy()
        messagebox.showinfo("ОК", "Пароль успешно изменен")
    Button(dlg, text="ОК", width=10, command=apply).place(relx=0.15, rely=0.82)
    Button(dlg, text="Отмена", width=10, command=dlg.destroy).place(relx=0.55, rely=0.82)



def on_search_change(*args):
    q = search.get().strip().lower()
    if len(q) < 3:
        list_of_variants.place_forget()
        return
    matches = sorted(city for city in data if q in city.lower() and city not in hidden_citties)

    if not matches:
        list_of_variants.place_forget()
        return

    list_of_variants.delete(0, END)
    for match in matches:
        list_of_variants.insert(END, match)
    list_of_variants.place(relx=0.05, rely=0.28)

def on_variant_select(event=None):
    sel = list_of_variants.curselection()
    if not sel: return

    city = list_of_variants.get(sel[0])
    if city in hidden_citties or city not in data:
        list_of_variants.place_forget()
        return

    population = f"{data[city]:,}".replace(",", " ")
    res.set(f"{city} - {population} человек")

    list_of_variants.place_forget()
    search_entry.focus_set()

def refresh_admin_list():
    admin_list.delete(0, END)
    for city in sorted(data):
        population = f"{data[city]:,}".replace(",", " ")
        admin_list.insert(END, f"{city} - {population} чел")
    update_stats()

def change_city_status():
    city = get_selected_city()
    if not city or city not in data:
        status_var.set("Выберите город из списка")
        return

    if city in hidden_citties:
        hidden_citties.remove(city)
        admin_status_var.set("нет особого статуса")
        status_var.set(f"{city}: статус снят")
    else:
        hidden_citties.add(city)
        admin_status_var.set("особый статус")
        status_var.set(f"{city}: особый статус присовен")

    save_data()
    update_stats()
    on_search_change()

def admin_add():
    city = admin_city_var.get().strip()
    pop = admin_pop_var.get().strip()

    if not city or not pop:
        status_var.set("Заполните оба поля")
        return
    if not pop.isdigit():
        status_var.set("Численность - только цифры")
        return
    if city in data:
        status_var.set("Такой город уже есть")
        return

    data[city] = int(pop)
    save_data()
    refresh_admin_list()
    admin_city_var.set("")
    admin_pop_var.set("")
    status_var.set(f"Добавлено: {city}")
    on_search_change()

def admin_edit():
    city = get_selected_city()
    pop = admin_pop_var.get().strip()

    if city is None:
        return
    if not pop:
        status_var.set("Введите новую численность")
        return
    if not pop.isdigit():
        status_var.set("Численность - только цифры")
        return

    data[city] = int(pop)
    save_data()
    refresh_admin_list()
    admin_pop_var.set("")
    status_var.set(f"Обновлено: {city}")
    on_search_change()

def admin_delete():
    city = get_selected_city()
    if city is None:
        return
    if not messagebox.askyesno("Удаление", f"Удалить {city}?"):
        return

    del data[city]
    hidden_citties.discard(city)
    save_data()
    refresh_admin_list()
    admin_status_var.set("")
    status_var.set(f"Удалено: {city}")
    on_search_change()

def get_selected_city():
    sel = admin_list.curselection()
    if not sel:
        status_var.set("Ничего не выбрано!")
        return None
    text = admin_list.get(sel[0])
    return text.split(' - ')[0]

def on_admin_select(event=None):
    city = get_selected_city()
    if city is None:
        return
    admin_city_var.set(city)
    admin_pop_var.set(str(data[city]))

    if city in hidden_citties:
        admin_status_var.set("особый статус")
    else:
        admin_status_var.set("нет особого статуса")

def update_stats():
    total = len(data)
    hidden = len(hidden_citties)
    million = sum(1 for p in data.values() if p>=1000000)
    small = sum(1 for p in data.values() if p<20000)
    other = sum(1 for p in data.values() if 20000 <= p < 1000000)

    text=f"Всего городов: {total}\nСкрытых городов: {hidden}\nМиллионники: {million}\nМенее 20000: {small}\nДругие: {other}"
    status_text.config(state="normal")
    status_text.delete(1.0, END)
    status_text.insert(1.0, text)
    status_text.config(state="disabled")



search_frame = Frame(root)

Label(search_frame, text="Введите название города").place(relx=0.05, rely=0.1)

search = StringVar()
search_entry = Entry(search_frame, width=50, textvariable=search)
search_entry.place(relx=0.05, rely=0.2)

list_of_variants = Listbox(search_frame, width=30, height=6)

res = StringVar()
res_entry = Entry(search_frame, width=50, textvariable=res, state="readonly")
res_entry.place(relx=0.05, rely=0.6)

admin_button = Button(search_frame, width=18, text="Редакторская панель", command=show_password_entry)
admin_button.place(relx=0.05, rely=0.7)

pw = StringVar()
pw_entry = Entry(search_frame, width=20, textvariable=pw, show="*")
pw_entry.bind("<Return>", check_password)

search.trace_add("write", on_search_change)
list_of_variants.bind("<<ListboxSelect>>", on_variant_select)



admin_frame = Frame(root)

admin_title_label = Label(admin_frame, text="Панель администратора")
admin_title_label.place(relx=0.05, rely=0.05)

back_button = Button(admin_frame, width=18, text="Назад", command=show_search_screen)
back_button.place(relx=0.05, rely=0.15)

admin_list = Listbox(admin_frame, width=45, height=12)
admin_list.place(relx=0.05, rely=0.22)
admin_list.bind("<<ListboxSelect>>", on_admin_select)

status_text = Text(admin_frame, width=40, height=6, state="disabled")

Label(admin_frame, text="Название города:").place(relx=0.55, rely=0.22)
admin_city_var = StringVar()
Entry(admin_frame, width=25, textvariable=admin_city_var).place(relx=0.55, rely=0.28)

Label(admin_frame, text="Численность:").place(relx=0.55, rely=0.36)
admin_pop_var = StringVar()
Entry(admin_frame, width=25, textvariable=admin_pop_var).place(relx=0.55, rely=0.42)

Label(admin_frame, text="Статус города:").place(relx=0.55, rely=0.48)
admin_status_var = StringVar()
Entry(admin_frame, width=25, textvariable=admin_status_var, state="readonly").place(relx=0.55, rely=0.54)

status_change_button = Button(admin_frame, width=22, text="Переключить статус", command=change_city_status)
status_change_button.place(relx=0.55, rely=0.60)

add_button = Button(admin_frame, width=22, text="Добавить", command=admin_add)
add_button.place(relx=0.55, rely=0.665)

edit_button = Button(admin_frame, width=22, text="Изменить выбранный", command=admin_edit)
edit_button.place(relx=0.55, rely=0.73)

delite_button = Button(admin_frame, width=22, text="Удалить выбранный", command=admin_delete)
delite_button.place(relx=0.55, rely=0.795)

reset_pw_button = Button(admin_frame, width=22, text="Сменить пароль", command=reset_password)
reset_pw_button.place(relx=0.55, rely=0.86)

status_var = StringVar()
Label(admin_frame, textvariable=status_var, fg="red").place(relx=0.55, rely=0.925)




load_auth()
load_data()
show_search_screen()

root.mainloop()
