import tkinter as tk
from tkinter import messagebox, scrolledtext
import time, os, threading, re, json, sys  # Додано sys
import pygame


# --- ФУНКЦІЯ ДЛЯ ШЛЯХІВ (Для роботи ресурсів у .exe) ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class PetGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Pet Evolution: Neon Stable")

        # --- ВСТАНОВЛЕННЯ ІКОНКИ ---
        try:
            # Використовуємо .ico файл через метод iconbitmap
            self.root.iconbitmap(default=resource_path("icon.ico"))
        except Exception as e:
            print(f"Icon error: {e}")

        # --- CONFIGURATION ---
        self.bg_color = "#0f0c29"
        self.accent_color = "#00d2ff"
        self.db_file = "users.json"
        self.session_file = "session.txt"
        self.lang = "UA"
        self.music_on = False
        self.current_user = None
        self.paused = False
        self.ui_elements = {}
        self.species_data = {
            "Neon Rabbit": (0.001, 0.003, "#ff007f", "Вухань: П'є часто.",
                            "Bunny: Thirsty one.",
                            ["(\\_/)\n( •_•)\n/ >💧", "(\\_/)\n( o.o)\n/ >💧"]),
            "Cyber Shark": (0.003, 0.001, "#00ffcc", "Акула: Завжди голодна.",
                            "Shark: Always hungry.",
                            [" /\\ \n <* )))<\n \\/ ", " /\\ \n <* )))<\n \\/ "]),
            "Plasma Cat": (0.0015, 0.0015, "#bc13fe", "Кіт: Збалансований.",
                           "Cat: Balanced.",
                           [" /\\_/\\\n( o.o )\n > ^ < ", " /\\_/\\\n( -.- )\n > ^ < "])
        }
        self.text = {
            "UA": {
                "login": "🔑 ВХІД", "reg": "📝 РЕЄСТРАЦІЯ", "set": "⚙️", "rules": "📜 ПРАВИЛА",
                "back": "↩ НАЗАД", "eat": "🍖 ГОДУВАТИ", "drink": "💧 НАПОЇТИ",
                "health": "❤️ ЖИТТЯ", "food": "🍖 СИТНІСТЬ", "water": "💧 СПРАГА", "age": "ВІК",
                "mail_h": "Приклад: user@mail.com", "pass_h": "8+ симв, A-Z, 0-9, !", "conf": "ПОВТОР ПАРОЛЯ",
                "rule_txt": "📜 ПРАВИЛА ГРИ:\n1. 1 рік = 1 день реального часу.\n2. Вихованець хоче їсти навіть коли додаток вимкнено.\n3. Слідкуйте за шкалами, щоб вихованець не загинув.",
                "size": "ЕКРАН", "lang_btn": "МОВА: UA", "logout": "🚪 ВИХІД", "select": "ОБРАТИ",
                "admin_title": "АДМІН ПАНЕЛЬ (Email | Pass | Pet)", "y": "рік", "m": "міс."
            },
            "EN": {
                "login": "🔑 LOGIN", "reg": "📝 REGISTER", "set": "⚙️", "rules": "📜 RULES",
                "back": "↩ BACK", "eat": "🍖 FEED", "drink": "💧 DRINK",
                "health": "❤️ HEALTH", "food": "🍖 FOOD", "water": "💧 THIRST", "age": "AGE",
                "mail_h": "Ex: user@mail.com", "pass_h": "8+ chars, A-Z, 0-9, !", "conf": "CONFIRM PASS",
                "rule_txt": "📜 GAME RULES:\n1. 1 pet year = 1 real day.\n2. Stats drop offline.\n3. Keep bars full or the pet will die.",
                "size": "SCREEN", "lang_btn": "LANG: EN", "logout": "🚪 LOGOUT", "select": "SELECT",
                "admin_title": "ADMIN PANEL (Email | Pass | Pet)", "y": "year", "m": "mon."
            }
        }
        self.root.geometry("500x850")
        self.root.configure(bg=self.bg_color)
        self.root.bind("<Control-Shift-KeyPress-A>", lambda e: self.show_admin_panel())
        threading.Thread(target=self.bg_music_loop, daemon=True).start()
        self.check_session()

    # --- ENGINE ---
    def retranslate_ui(self):
        t = self.text[self.lang]
        for key, widget in self.ui_elements.items():
            if widget.winfo_exists():
                if key in t:
                    widget.config(text=t[key])
                elif key.startswith("sel_"):
                    widget.config(text=t["select"])
                elif key.startswith("desc_"):
                    p_name = key.replace("desc_", "")
                    data = self.species_data[p_name]
                    widget.config(text=data[3 if self.lang == "UA" else 4])
                elif key == "age_lbl":
                    self.update_age_text()

    def load_settings(self):
        if self.current_user and self.current_user != "Admin":
            u = self.load_users().get(self.current_user, {})
            self.lang = u.get("lang", "UA")
            self.music_on = u.get("music", False)

    def save_settings_to_db(self):
        if not self.current_user or self.current_user == "Admin": return
        u = self.load_users()
        if self.current_user in u:
            u[self.current_user].update({"lang": self.lang, "music": self.music_on})
            with open(self.db_file, "w") as f: json.dump(u, f)

    # --- LOGIC ---
    def check_session(self):
        if os.path.exists(self.session_file):
            with open(self.session_file, "r") as f:
                try:
                    data = f.read().split("|")
                    # ВИПРАВЛЕНО: data[1] для часу та data[0] для email
                    if len(data) == 2 and time.time() - float(data[1]) < 1800:
                        self.current_user = data[0]
                        self.load_settings()
                        self.show_selection()
                        return
                except:
                    pass
        self.show_main_menu()

    def logout(self):
        if os.path.exists(self.session_file): os.remove(self.session_file)
        self.current_user = None
        self.show_main_menu()

    def load_users(self):
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, "r") as f: return json.load(f)
        except:
            pass
        return {}

    def save_progress(self):
        if not self.current_user or self.current_user == "Admin": return
        users = self.load_users()
        if self.current_user in users:
            users[self.current_user].update({
                "pet": self.current_pet, "stats": self.stats,
                "last_save": time.time(), "lang": self.lang, "music": self.music_on
            })
            with open(self.db_file, "w") as f: json.dump(users, f)

    def clear(self):
        self.paused = True
        self.ui_elements = {}
        for w in self.root.winfo_children(): w.destroy()

    # --- UI ---
    def show_main_menu(self):
        self.clear()
        t = self.text[self.lang]
        tk.Label(self.root, text="NEON PET", font=("Courier", 50, "bold"),
                 bg=self.bg_color, fg=self.accent_color).pack(pady=80)
        for k in ["login", "reg", "rules"]:
            b = tk.Button(self.root, text=t[k], width=25, height=2,
                          bg="#2196F3" if k == "login" else "#4CAF50" if k == "reg" else "#9C27B0", fg="white",
                          command=self.show_login if k == "login" else self.show_reg if k == "reg" else
                          lambda: messagebox.showinfo("Rules", self.text[self.lang]["rule_txt"]))
            b.pack(pady=10)
            self.ui_elements[k] = b
        tk.Button(self.root, text=t["set"], width=10, bg="#1b1b3a", fg="white",
                  command=lambda: self.show_settings(False)).pack(pady=20)

    def show_reg(self):
        self.clear()
        t = self.text[self.lang]
        f = tk.Frame(self.root, bg=self.bg_color)
        f.pack(pady=40, padx=40, fill="both")
        e_m = self.create_input(f, "EMAIL", t["mail_h"])
        e_p = self.create_input(f, "PASSWORD", t["pass_h"], True)
        e_c = self.create_input(f, t["conf"], "", True)

        def save():
            if e_p.get() != e_c.get():
                messagebox.showerror("!", "Mismatch!")
                return
            u = self.load_users()
            u[e_m.get()] = {"pass": e_p.get(), "pet": None, "lang": "UA", "music": False}
            with open(self.db_file, "w") as fd: json.dump(u, fd)
            self.show_login()

        tk.Button(f, text=t["reg"], bg="#4CAF50", fg="white", height=2, command=save).pack(fill="x", pady=20)
        tk.Button(f, text=t["back"], bg=self.bg_color, fg="grey", bd=0, command=self.show_main_menu).pack()

    def show_login(self):
        self.clear()
        t = self.text[self.lang]
        f = tk.Frame(self.root, bg=self.bg_color)
        f.pack(pady=60, padx=40, fill="both")
        e_m = self.create_input(f, "EMAIL")
        e_p = self.create_input(f, "PASSWORD", "", True)

        def enter():
            u = self.load_users()
            if e_m.get() in u and u[e_m.get()]["pass"] == e_p.get():
                self.current_user = e_m.get()
                self.load_settings()
                with open(self.session_file, "w") as fs:
                    fs.write(f"{e_m.get()}|{time.time()}")
                self.show_selection()
            else:
                messagebox.showerror("!", "Error!")

        tk.Button(f, text=t["login"], bg="#2196F3", fg="white", height=2, command=enter).pack(fill="x", pady=20)
        tk.Button(f, text=t["back"], bg=self.bg_color, fg="grey", bd=0, command=self.show_main_menu).pack()

    def show_selection(self):
        self.clear()
        t = self.text[self.lang]
        b_r = tk.Button(self.root, text=t["rules"], bg="#9C27B0", fg="white",
                        command=lambda: messagebox.showinfo("Rules", self.text[self.lang]["rule_txt"]))
        b_r.place(x=10, y=10)
        self.ui_elements["rules"] = b_r
        tk.Button(self.root, text=t["set"], bg="#1b1b3a", fg="white",
                  command=lambda: self.show_settings(False)).place(x=100, y=10)
        tk.Label(self.root, text="NEON STABLE", font=("Arial", 22, "bold"), bg=self.bg_color, fg="white").pack(pady=40)
        for name, data in self.species_data.items():
            f = tk.Frame(self.root, bg="#1b1b3a", bd=1, relief="sunken")
            f.pack(pady=10, padx=50, fill="x")
            tk.Label(f, text=name, fg=data[2], bg="#1b1b3a", font=("Arial", 12, "bold")).pack()
            l_d = tk.Label(f, text=data[3 if self.lang == "UA" else 4], fg="white", bg="#1b1b3a")
            l_d.pack()
            self.ui_elements[f"desc_{name}"] = l_d
            b_s = tk.Button(f, text=t["select"], command=lambda n=name: self.start_game(n))
            b_s.pack(pady=5)
            self.ui_elements[f"sel_{name}"] = b_s
        b_out = tk.Button(self.root, text=t["logout"], bg="#555", fg="white", command=self.logout)
        b_out.pack(pady=20)
        self.ui_elements["logout"] = b_out

    def start_game(self, pet_name):
        self.clear()
        self.current_pet = pet_name
        self.paused = False
        t = self.text[self.lang]
        tk.Button(self.root, text="📜", bg="#9C27B0", fg="white",
                  command=lambda: messagebox.showinfo("Rules", self.text[self.lang]["rule_txt"])).place(x=10, y=10)
        u = self.load_users().get(self.current_user, {})
        if u.get("pet") == pet_name:
            self.stats = u["stats"]
            off = time.time() - u["last_save"]
            self.stats["food"] = max(0, self.stats["food"] - (self.species_data[pet_name][0] * off * 5.5))
            self.stats["water"] = max(0, self.stats["water"] - (self.species_data[pet_name][1] * off * 5.5))
        else:
            self.stats = {"health": 100.0, "food": 100.0, "water": 100.0, "born": time.time()}
        self.pet_lbl = tk.Label(self.root, text="", font=("Courier", 35, "bold"), bg=self.bg_color,
                                fg=self.species_data[pet_name][2])
        self.pet_lbl.pack(pady=40)
        self.bars = {};
        self.v_lbls = {}
        for s in ["health", "food", "water"]:
            l = tk.Label(self.root, text=t[s], bg=self.bg_color, fg="white", font=("Arial", 10, "bold"))
            l.pack()
            self.ui_elements[s] = l
            self.v_lbls[s] = tk.Label(self.root, text="100/100", bg=self.bg_color, fg=self.accent_color)
            self.v_lbls[s].pack()
            c = tk.Canvas(self.root, width=250, height=15, bg="#111", highlightthickness=0)
            c.pack(pady=5)
            self.bars[s] = (c, c.create_rectangle(0, 0, 250, 15, fill=self.species_data[pet_name][2]))
        self.age_lbl = tk.Label(self.root, text="", font=("Arial", 12, "bold"), bg=self.bg_color, fg="white")
        self.age_lbl.pack(pady=20)
        self.ui_elements["age_lbl"] = self.age_lbl
        for k in ["eat", "drink", "back"]:
            b = tk.Button(self.root, text=t[k], bg="#4CAF50" if k == "eat" else "#2196F3" if k == "drink" else "#333",
                          fg="white", width=25, height=2,
                          command=lambda x=k: self.refill("food") if x == "eat" else self.refill(
                              "water") if x == "drink" else self.show_selection())
            b.pack(pady=5)
            self.ui_elements[k] = b
        self.update_loop()

    def update_loop(self):
        if self.paused or self.stats["health"] <= 0: return
        d = self.species_data[self.current_pet]
        self.stats["food"] = max(0, self.stats["food"] - d[0] * 5.5)
        self.stats["water"] = max(0, self.stats["water"] - d[1] * 5.5)
        if self.stats["food"] <= 0 or self.stats["water"] <= 0:
            self.stats["health"] -= 0.15
        self.pet_lbl.config(text=d[5][int(time.time()) % 2])
        self.update_age_text()
        for s in ["health", "food", "water"]:
            val = int(round(self.stats[s]))
            self.v_lbls[s].config(text=f"{val}/100")
            self.bars[s][0].coords(self.bars[s][1], 0, 0, (self.stats[s] / 100) * 250, 15)
        if int(time.time()) % 5 == 0: self.save_progress()
        self.root.after(500, self.update_loop)

    def update_age_text(self):
        el = time.time() - self.stats["born"]
        y, m = int(el // 86400), int((el % 86400) // 7200)
        t = self.text[self.lang]
        self.age_lbl.config(text=f"{t['age']}: {y} {t['y']} {m} {t['m']}")

    def refill(self, s):
        self.stats[s] = min(100.0, self.stats[s] + 15)

    def show_admin_panel(self):
        adm = tk.Toplevel(self.root);
        adm.geometry("500x600");
        adm.title("Admin Tool");
        adm.configure(bg="#222")
        txt = scrolledtext.ScrolledText(adm, bg="#333", fg="lime");
        txt.pack(expand=True, fill="both")
        u = self.load_users()
        for k, v in u.items(): txt.insert(tk.END, f"📧 {k} | 🔑 {v['pass']} | 🐾 {v.get('pet', 'None')}\n")

        def skip(): self.current_user = "Admin"; adm.destroy(); self.show_selection()

        tk.Button(adm, text="SKIP LOGIN (GUEST)", bg="orange", height=2, command=skip).pack(fill="x")

    def show_settings(self, in_game):
        old_p = self.paused;
        self.paused = True
        t = self.text[self.lang]
        s = tk.Toplevel(self.root);
        s.geometry("380x600");
        s.configure(bg=self.bg_color)

        def toggle_l():
            self.lang = "UA" if self.lang == "EN" else "EN"
            b_l.config(text=self.text[self.lang]["lang_btn"]);
            self.retranslate_ui();
            self.save_settings_to_db()

        b_l = tk.Button(s, text=t["lang_btn"], command=toggle_l);
        b_l.pack(pady=10)

        def toggle_m():
            self.music_on = not self.music_on;
            self.save_settings_to_db();
            s.destroy();
            self.show_settings(in_game)

        tk.Button(s, text=f"Music: {'ON' if self.music_on else 'OFF'}", command=toggle_m).pack(pady=10)
        for r in ["400x700", "500x850", "600x950"]:
            tk.Button(s, text=r, command=lambda x=r: self.root.geometry(x)).pack(pady=2)
        tk.Button(s, text="OK", bg="#4CAF50", fg="white", width=15,
                  command=lambda: [setattr(self, 'paused', old_p), s.destroy()]).pack(pady=30)

    def create_input(self, parent, label, hint="", is_pass=False):
        tk.Label(parent, text=label, bg=self.bg_color, fg=self.accent_color, font=("Arial", 8, "bold")).pack(anchor="w")
        if hint: tk.Label(parent, text=hint, bg=self.bg_color, fg="grey", font=("Arial", 7)).pack(anchor="w")
        fr = tk.Frame(parent, bg="#1b1b3a");
        fr.pack(pady=5, fill="x")
        ent = tk.Entry(fr, bg="#1b1b3a", fg="white", bd=0, font=("Arial", 11), insertbackground="white")
        if is_pass: ent.config(show="*")
        ent.pack(side="left", padx=10, ipady=8, expand=True, fill="x")
        if is_pass:
            tk.Button(fr, text="👁", bg="#1b1b3a", fg="white", bd=0,
                      command=lambda: ent.config(show="" if ent.cget("show") == "*" else "*")).pack(side="right",
                                                                                                    padx=5)
        return ent

    def bg_music_loop(self):
        pygame.mixer.init()
        # ВИПРАВЛЕНО: шлях через resource_path
        music_path = resource_path("music.mp3")
        while True:
            if self.music_on:
                if not pygame.mixer.music.get_busy():
                    try:
                        pygame.mixer.music.load(music_path);
                        pygame.mixer.music.play(-1)
                    except:
                        pass
            else:
                pygame.mixer.music.stop()
            time.sleep(1)


if __name__ == "__main__":
    root = tk.Tk()
    app = PetGame(root)
    root.mainloop()
