import random
import time

# --- 定数・データ定義 ---
HANDS = ["右投右打", "右投左打", "左投右打", "左投左打", "右投両打", "左投両打"]
POSITIONS = ["投手", "捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "左翼手", "中堅手", "右翼手"]
GROWTH_TYPES = ["超晩成", "晩成", "緩やか晩成", "普通", "緩やか早熟", "早熟", "超早熟"]
PITCH_TYPES = ["スライダー", "カットボール", "カーブ", "Dカーブ", "フォーク", "SFF", "チェンジアップ", "シンカー", "シュート", "ツーシーム"]

SCHOOLS = {
    "1": {"name": "大阪桐蔭", "甲": 5, "注": 5, "層": 5, "練": 5},
    "2": {"name": "神村学園", "甲": 4, "注": 5, "層": 4, "練": 5},
    "3": {"name": "早稲田実業", "甲": 3, "注": 4, "層": 3, "練": 4},
    "4": {"name": "エナジックスポーツ学院", "甲": 2, "注": 2, "層": 2, "練": 5},
    "5": {"name": "佐賀商業", "甲": 2, "注": 2, "層": 2, "練": 3},
    "6": {"name": "笠岡工業", "甲": 0.1, "注": 1, "層": 0.5, "練": 1}
}

PITCHER_PRACTICES = [
    {"name": "フォームチェック", "effect": lambda p: p.add_stat("制球", 1, "球速", 1)},
    {"name": "球速測定", "effect": lambda p: p.add_stat("球速", 2)},
    {"name": "投げ込み", "effect": lambda p: p.add_stat("スタミナ", 1, "制球", 1)},
    {"name": "走り込み", "effect": lambda p: p.add_stat("スタミナ", 2)},
    {"name": "スクワット", "effect": lambda p: p.add_stat("スタミナ", 2)},
    {"name": "変化球練習", "effect": lambda p: p.add_pitch(0.30)},
    {"name": "的あて", "req_ren": 2, "effect": lambda p: p.add_stat("制球", 3)},
    {"name": "タイヤ引き", "req_ren": 2, "effect": lambda p: p.add_stat("スタミナ", 3)},
    {"name": "変化球研究", "req_ren": 3, "effect": lambda p: p.add_pitch(0.70)},
    {"name": "新球種練習", "req_ren": 4, "effect": lambda p: p.learn_new_pitch()},
    {"name": "総合投球練習", "req_ren": 4, "effect": lambda p: p.add_stat("制球", 2, "スタミナ", 1, "球速", 1)}
]

class Player:
    def __init__(self, name, hand, pos, school):
        self.name = name
        self.hand = hand
        self.is_pitcher = (pos == "投手")
        self.pos = pos
        self.school = school
        self.growth = random.choice(GROWTH_TYPES)
        self.coach_eval = 0
        self.scout_eval = 0
        self.salary = 0
        self.lifetime_salary = 0
        
        # 投手ステータス
        self.speed = random.randint(105, 140)
        self.control = random.randint(15, 50)
        self.stamina = random.randint(20, 40)
        self.pitches = {}
        if self.is_pitcher:
            num_pitches = random.choices([1, 2, 3, 4], weights=[35, 45, 19, 1])[0]
            for _ in range(num_pitches):
                ptype = random.choice([p for p in PITCH_TYPES if p not in self.pitches])
                self.pitches[ptype] = random.randint(1, 3)
                
        # 野手ステータス
        self.meet = random.randint(15, 45)
        self.power = random.randint(10, 55)
        self.run = random.randint(20, 55)
        self.defense = random.randint(10, 45)

    @property
    def ovr(self):
        if self.is_pitcher:
            pitch_val = sum(self.pitches.values()) * 10
            return int((self.speed * 0.5 + self.control + self.stamina + pitch_val) / 4)
        else:
            return int((self.meet + self.power + self.run + self.defense) / 4)

    def add_stat(self, stat1, val1, stat2=None, val2=0):
        if stat1 == "球速": self.speed += val1
        elif stat1 == "制球": self.control += val1
        elif stat1 == "スタミナ": self.stamina += val1
        elif stat1 == "ミート": self.meet += val1
        elif stat1 == "パワー": self.power += val1
        
        if stat2 == "球速": self.speed += val2
        elif stat2 == "制球": self.control += val2
        elif stat2 == "スタミナ": self.stamina += val2

    def add_pitch(self, prob):
        if self.pitches and random.random() < prob:
            ptype = random.choice(list(self.pitches.keys()))
            if self.pitches[ptype] < 7:
                self.pitches[ptype] += 1

    def learn_new_pitch(self):
        prob = 0.30 if self.school["練"] >= 4 else 0.15
        available = [p for p in PITCH_TYPES if p not in self.pitches]
        if available and random.random() < prob:
            self.pitches[random.choice(available)] = 1

def print_header(player, year, season, age):
    print("\n" + "ー"*20)
    print(f"⚾BASEBALL LIFE  年俸{player.salary}円")
    print(f"           生涯{player.lifetime_salary}円")
    print(f"高校{year}年生 {season}")
    print(f"{player.name}")
    print(f"{age}歳│{player.pos}│{player.school['name']}  [能力OVR値: {player.ovr}]")
    
    if player.is_pitcher:
        print(f"球速   {player.speed}km/h")
        print(f"制球   {player.control}")
        print(f"スタミナ {player.stamina}")
        for i, (ptype, level) in enumerate(player.pitches.items(), 1):
            print(f"変化球{i}  {ptype} Lv{level}")
    else:
        print(f"ミート  {player.meet}")
        print(f"パワー  {player.power}")
        print(f"走力   {player.run}")
        print(f"守備力  {player.defense}")
    print("ー"*20)

def trigger_event(player):
    r = random.random()
    if r < 0.2:
        print("(イベント) 練習が上手く行った！能力が2倍成長した！")
        player.add_stat("スタミナ", 2) if player.is_pitcher else player.add_stat("パワー", 2)
    elif r < 0.4:
        print("(イベント) 練習試合で活躍した！監督の評価が上がった。")
        player.coach_eval = min(10, player.coach_eval + 1)
    
    # スカウトイベント
    scout_chance = 0.25
    if player.school["注"] == 5: scout_chance = 0.80
    elif player.school["注"] == 4: scout_chance = 0.60
    elif player.school["注"] == 3: scout_chance = 0.45
    elif player.school["注"] == 2: scout_chance = 0.35
    
    if random.random() < scout_chance:
        if player.ovr >= 45:
            print("(イベント) スカウトが見に来た。高く評価された！(スカウト評価↑↑)")
            player.scout_eval = min(10, player.scout_eval + 2)
        elif player.ovr >= 35:
            print("(イベント) スカウトが見に来た。注目された(スカウト評価↑)")
            player.scout_eval = min(10, player.scout_eval + 1)

def main():
    print("⚾BASEBALL LIFE")
    name = input("名前を入力: ")
    
    print("\n投打を選択:")
    for i, h in enumerate(HANDS): print(f"{i+1}: {h}")
    hand = HANDS[int(input("番号: ")) - 1]
    
    print("\nポジションを選択:")
    for i, p in enumerate(POSITIONS): print(f"{i+1}: {p}")
    pos = POSITIONS[int(input("番号: ")) - 1]
    
    print("\n進学先高校を選択:")
    for k, v in SCHOOLS.items():
        print(f"{k}: {v['name']} (甲☆{v['甲']}, 注☆{v['注']}, 層☆{v['層']}, 練☆{v['練']})")
    school = SCHOOLS[input("番号: ")]
    
    player = Player(name, hand, pos, school)
    print("\n[高校1年目からスタート]")
    time.sleep(1)
    
    schedule = [
        (1, "春", 15), (1, "夏", 16), (1, "秋", 16), (1, "冬", 16),
        (2, "春", 16), (2, "夏", 17), (2, "秋", 17), (2, "冬", 17),
        (3, "春", 17), (3, "夏", 18), (3, "秋", 18)
    ]
    
    for year, season, age in schedule:
        print_header(player, year, season, age)
        
        # 練習メニュー抽出 (野手用は簡易的に代用)
        available_pracs = [p for p in PITCHER_PRACTICES if p.get("req_ren", 1) <= school["練"]] if player.is_pitcher else [{"name": "素振り", "effect": lambda p: p.add_stat("ミート", 2)}, {"name": "筋トレ", "effect": lambda p: p.add_stat("パワー", 2)}, {"name": "ダッシュ", "effect": lambda p: p.add_stat("走力", 2)}]
        
        num_choices = max(2, int(school["練"]) + 1)
        current_pracs = random.sample(available_pracs, min(num_choices, len(available_pracs)))
        
        print("練習の中から2つ選択")
        for i, p in enumerate(current_pracs):
            print(f"[{i+1}: {p['name']}]", end="  ")
        print()
        
        c1 = int(input("1つ目の練習番号: ")) - 1
        c2 = int(input("2つ目の練習番号: ")) - 1
        
        current_pracs[c1]["effect"](player)
        current_pracs[c2]["effect"](player)
        
        print("\n練習実行中...")
        time.sleep(1)
        trigger_event(player)
        input("Enterキーで次の季節へ...\n")
        
    print_header(player, 3, "秋", 18)
    print("高校生活終了。進路希望を選択してください。")
    print("1: プロ志望届  2: 大学進学  3: 社会人野球  4: 独立リーグ  5: アメリカの大学進学")
    choice = input("番号: ")
    
    if choice == "1" and player.scout_eval >= 5 and player.ovr >= 40:
        print("\n🎉ドラフト指名されました！プロ野球選手としてのキャリアがスタートします！")
    elif choice == "1":
        print("\n惜しくも指名漏れ...。次のステージでプロを目指しましょう。")
    else:
        print("\n新たな道へ進みます。BASEBALL LIFEは続く...")

if __name__ == "__main__":
    main()
