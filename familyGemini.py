import tkinter as tk
from tkinter import messagebox
import json
import os

class FamilyFeudGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Family Feud: Jannat Edition")
        self.root.configure(bg="#0F1B4C")
        
        # UI Setup
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        # Game Logic Variables
        self.teams = ["Nikhil's Family", "Jannat's Family"]
        self.scores = {self.teams[0]: 0, self.teams[1]: 0}
        self.round_num = 0
        self.active_team = None
        self.bank = 0
        self.strikes = {self.teams[0]: 0, self.teams[1]: 0}
        
        self.load_data()
        self.build_ui()
        self.setup_round()

    def load_data(self):
        try:
            with open('questions.json', 'r') as f:
                self.questions = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "questions.json not found!")
            self.root.destroy()

    def build_ui(self):
        # Header Scores
        self.header = tk.Frame(self.root, bg="#0F1B4C", pady=20)
        self.header.pack(fill="x")

        self.lbl_t1 = tk.Label(self.header, text="", font=("Helvetica", 24, "bold"), bg="#0F1B4C", fg="#FFD700")
        self.lbl_t1.pack(side="left", padx=60)

        self.lbl_bank = tk.Label(self.header, text="BANK: 0", font=("Helvetica", 40, "bold"), bg="#0F1B4C", fg="#00FF00")
        self.lbl_bank.pack(side="left", expand=True)

        self.lbl_t2 = tk.Label(self.header, text="", font=("Helvetica", 24, "bold"), bg="#0F1B4C", fg="#FFD700")
        self.lbl_t2.pack(side="right", padx=60)

        # Question Display
        self.lbl_q = tk.Label(self.root, text="", font=("Helvetica", 20, "italic"), bg="#2A3B75", fg="white", pady=15)
        self.lbl_q.pack(fill="x", padx=100, pady=20)

        # Buzzer Controls
        self.buzzer_bar = tk.Frame(self.root, bg="#0F1B4C")
        self.buzzer_bar.pack(pady=10)
        
        tk.Button(self.buzzer_bar, text=f"WIN: {self.teams[0]}", command=lambda: self.set_active(0)).pack(side="left", padx=10)
        self.lbl_status = tk.Label(self.buzzer_bar, text="WAITING FOR BUZZER", font=("Arial", 12), bg="#0F1B4C", fg="cyan")
        self.lbl_status.pack(side="left", padx=20)
        tk.Button(self.buzzer_bar, text=f"WIN: {self.teams[1]}", command=lambda: self.set_active(1)).pack(side="left", padx=10)

        # Board
        self.board = tk.Frame(self.root, bg="#0F1B4C")
        self.board.pack(expand=True, fill="both", padx=100)

        # Bottom Controls
        self.footer = tk.Frame(self.root, bg="#0F1B4C", pady=30)
        self.footer.pack(side="bottom", fill="x")

        self.btn_strike = tk.Button(self.footer, text="❌ STRIKE", font=("Arial", 14, "bold"), bg="red", fg="white", command=self.add_strike)
        self.btn_strike.pack(side="left", padx=50)

        self.lbl_strikes = tk.Label(self.footer, text="", font=("Arial", 30), bg="#0F1B4C", fg="red")
        self.lbl_strikes.pack(side="left")

        tk.Button(self.footer, text="AWARD BANK", bg="gold", command=self.award).pack(side="right", padx=20)
        tk.Button(self.footer, text="NEXT >>", command=self.next_round).pack(side="right", padx=10)

    def setup_round(self):
        if self.round_num >= len(self.questions):
            self.game_over()
            return

        data = self.questions[self.round_num]
        self.current_ans = data["answers"]
        self.revealed = [False] * len(self.current_ans)
        self.bank = 0
        self.strikes = {t: 0 for t in self.teams}
        self.active_team = None

        self.lbl_q.config(text=f"ROUND {self.round_num+1}: {data['q']}")
        self.lbl_bank.config(text="BANK: 0")
        self.lbl_status.config(text="WAITING FOR BUZZER")
        self.lbl_strikes.config(text="")
        self.update_scores()

        for w in self.board.winfo_children(): w.destroy()
        for i in range(8):
            txt = f"{i+1}" if i < len(self.current_ans) else ""
            state = "normal" if i < len(self.current_ans) else "disabled"
            btn = tk.Button(self.board, text=txt, font=("Arial", 16, "bold"), bg="#2A3B75", fg="white", 
                            height=2, width=25, state=state, command=lambda idx=i: self.reveal_ans(idx))
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
        self.board.grid_columnconfigure((0,1), weight=1)

    def set_active(self, idx):
        self.active_team = self.teams[idx]
        self.lbl_status.config(text=f"PLAYING: {self.active_team.upper()}")
        self.update_strike_view()

    def reveal_ans(self, idx):
        if self.revealed[idx]: return
        self.revealed[idx] = True
        name, pts = self.current_ans[idx]
        
        btns = self.board.winfo_children()
        btns[idx].config(text=f"{name.upper()}  {pts}", bg="#FFD700", fg="black")
        
        self.bank += pts
        self.lbl_bank.config(text=f"BANK: {self.bank}")

    def add_strike(self):
        if not self.active_team: return
        self.strikes[self.active_team] += 1
        self.update_strike_view()

        if self.strikes[self.active_team] == 3:
            other = self.teams[1] if self.active_team == self.teams[0] else self.teams[0]
            messagebox.showinfo("STRIKE!", f"{self.active_team} is OUT! {other}, try to steal!")
            self.active_team = other
            self.lbl_status.config(text=f"STEAL: {self.active_team.upper()}")
            self.update_strike_view()

    def update_strike_view(self):
        s = self.strikes.get(self.active_team, 0)
        self.lbl_strikes.config(text="X " * s)

    def award(self):
        if self.active_team:
            self.scores[self.active_team] += self.bank
            self.bank = 0
            self.lbl_bank.config(text="AWARDED")
            self.update_scores()

    def update_scores(self):
        self.lbl_t1.config(text=f"{self.teams[0]}\n{self.scores[self.teams[0]]}")
        self.lbl_t2.config(text=f"{self.teams[1]}\n{self.scores[self.teams[1]]}")

    def next_round(self):
        self.round_num += 1
        self.setup_round()

    def game_over(self):
        winner = max(self.scores, key=self.scores.get)
        messagebox.showinfo("Winner!", f"Game Over!\nWinner: {winner}")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FamilyFeudGame(root)
    root.mainloop()