import tkinter as tk
from tkinter import messagebox, simpledialog
from perplexity import generate_game_content

class FamilyFeudApp:
    def __init__(self, root, game_data):
        self.root = root
        self.root.title("Family Feud AI")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#0F1B4C")
        
        # Data
        self.teams = game_data.team_names
        self.questions = game_data.questions
        
        # State
        self.scores = {self.teams[0]: 0, self.teams[1]: 0}
        self.round_idx = 0
        self.active_team = None
        self.bank = 0
        self.strikes = 0
        self.revealed = []

        self.setup_ui()
        self.load_round()

        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

    def setup_ui(self):
        # Score Header
        header = tk.Frame(self.root, bg="#0F1B4C", pady=20)
        header.pack(fill="x")

        self.team1_lbl = tk.Label(header, text="", font=("Arial", 24, "bold"), bg="#0F1B4C", fg="#FFD700")
        self.team1_lbl.pack(side="left", padx=50)

        self.bank_lbl = tk.Label(header, text="BANK: 0", font=("Arial", 40, "bold"), bg="#0F1B4C", fg="#00FF00")
        self.bank_lbl.pack(side="left", expand=True)

        self.team2_lbl = tk.Label(header, text="", font=("Arial", 24, "bold"), bg="#0F1B4C", fg="#FFD700")
        self.team2_lbl.pack(side="right", padx=50)

        # Question Area
        self.q_lbl = tk.Label(self.root, text="", font=("Arial", 22, "bold"), bg="#2A3B75", fg="white", pady=15)
        self.q_lbl.pack(fill="x", padx=100, pady=20)

        # Buzzer/Status
        status_frame = tk.Frame(self.root, bg="#0F1B4C")
        status_frame.pack(pady=10)
        
        tk.Button(status_frame, text=f"WIN: {self.teams[0]}", bg="orange", command=lambda: self.set_active(0)).pack(side="left", padx=10)
        self.status_lbl = tk.Label(status_frame, text="WHO WON THE BUZZER?", font=("Arial", 14), bg="#0F1B4C", fg="cyan")
        self.status_lbl.pack(side="left", padx=20)
        tk.Button(status_frame, text=f"WIN: {self.teams[1]}", bg="orange", command=lambda: self.set_active(1)).pack(side="left", padx=10)

        # Board
        self.board = tk.Frame(self.root, bg="#0F1B4C")
        self.board.pack(expand=True, fill="both", padx=100)

        # Footer
        footer = tk.Frame(self.root, bg="#0F1B4C", pady=30)
        footer.pack(side="bottom", fill="x")

        self.strike_btn = tk.Button(footer, text="❌ STRIKE", font=("Arial", 16, "bold"), bg="red", fg="white", command=self.add_strike)
        self.strike_btn.pack(side="left", padx=50)

        self.strike_lbl = tk.Label(footer, text="", font=("Arial", 35, "bold"), bg="#0F1B4C", fg="red")
        self.strike_lbl.pack(side="left")

        tk.Button(footer, text="NEXT ROUND", command=self.next_round).pack(side="right", padx=50)
        tk.Button(footer, text="AWARD POINTS", bg="gold", command=self.award_points).pack(side="right")

    def load_round(self):
        if self.round_idx >= len(self.questions):
            self.show_final_winner()
            return

        q_data = self.questions[self.round_idx]
        self.current_answers = q_data.answers
        self.revealed = [False] * 8
        self.bank = 0
        self.strikes = 0
        self.active_team = None

        self.q_lbl.config(text=f"ROUND {self.round_idx+1}: {q_data.q}")
        self.bank_lbl.config(text="BANK: 0")
        self.status_lbl.config(text="WAITING FOR BUZZER...")
        self.strike_lbl.config(text="")
        self.update_team_displays()

        for w in self.board.winfo_children(): w.destroy()
        for i in range(8):
            btn = tk.Button(self.board, text=f"{i+1}", font=("Arial", 18, "bold"), bg="#2A3B75", fg="white", 
                            height=2, width=25, command=lambda idx=i: self.reveal_answer(idx))
            btn.grid(row=i//2, column=i%2, padx=15, pady=10)
        self.board.grid_columnconfigure((0,1), weight=1)

    def set_active(self, idx):
        self.active_team = self.teams[idx]
        self.status_lbl.config(text=f"PLAYING: {self.active_team}")
        self.strikes = 0
        self.strike_lbl.config(text="")

    def reveal_answer(self, idx):
        if self.revealed[idx]: return
        self.revealed[idx] = True
        ans, pts = self.current_answers[idx]
        
        btns = self.board.winfo_children()
        btns[idx].config(text=f"{ans.upper()} ({pts})", bg="#FFD700", fg="black")
        
        self.bank += pts
        self.bank_lbl.config(text=f"BANK: {self.bank}")

    def add_strike(self):
        if not self.active_team: return
        self.strikes += 1
        self.strike_lbl.config(text="X " * self.strikes)
        
        if self.strikes == 3:
            other = self.teams[1] if self.active_team == self.teams[0] else self.teams[0]
            messagebox.showinfo("STRIKE 3", f"{self.active_team} is out! {other} chance to steal!")
            self.active_team = other
            self.status_lbl.config(text=f"STEAL ATTEMPT: {self.active_team}")
            self.strikes = 0 # Reset for the steal attempt

    def award_points(self):
        if self.active_team:
            self.scores[self.active_team] += self.bank
            self.bank = 0
            self.bank_lbl.config(text="AWARDED!")
            self.update_team_displays()

    def update_team_displays(self):
        self.team1_lbl.config(text=f"{self.teams[0]}\n{self.scores[self.teams[0]]}")
        self.team2_lbl.config(text=f"{self.teams[1]}\n{self.scores[self.teams[1]]}")

    def next_round(self):
        self.round_idx += 1
        self.load_round()

    def show_final_winner(self):
        winner = max(self.scores, key=self.scores.get)
        messagebox.showinfo("GAME OVER", f"Winner: {winner}\nFinal Score: {self.scores[winner]}")
        self.root.destroy()

def run_launcher():
    root = tk.Tk()
    root.withdraw()
    topic = simpledialog.askstring("Game Generator", "What should the game be about?")
    if topic:
        try:
            print("Fetching AI questions...")
            game_data = generate_game_content(topic)
            game_root = tk.Toplevel()
            app = FamilyFeudApp(game_root, game_data)
            root.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate game: {e}")
            root.destroy()
    else:
        root.destroy()

if __name__ == "__main__":
    run_launcher()