import streamlit as st
import random
import time

# --- 定数・データ定義 ---
HANDS = ["右投右打", "右投左打", "左投右打", "左投左打", "右投両打", "左投両打"]
POSITIONS = ["投手", "捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "左翼手", "中堅手", "右翼手"]
GROWTH_TYPES = ["超晩成", "晩成", "緩やか晩成", "普通", "緩やか早熟", "早熟", "超早熟"]
PITCH_TYPES = ["スライダー", "カットボール", "カーブ", "Dカーブ", "フォーク", "SFF", "チェンジアップ", "シンカー", "シュート", "ツーシーム"]

SCHOOLS = {
    "大阪桐蔭": {"甲": 5, "注": 5, "層": 5, "練": 5},
    "神村学園": {"甲": 4, "注": 5, "層": 4, "練": 5},
    "早稲田実業": {"甲": 3, "注": 4, "層": 3, "練": 4},
    "エナジックスポーツ学院": {"甲": 2, "注": 2, "層": 2, "練": 5},
    "佐賀商業": {"甲": 2, "注": 2, "層": 2, "練": 3},
    "笠岡工業": {"甲": 0.1, "注": 1, "層": 0.5, "練": 1}
}

PITCHER_PRACTICES = [
    {"name": "フォームチェック", "req_ren": 1, "effect": lambda p: p.add_stat("制球", 1, "球速", 1)},
    {"name": "球速測定", "req_ren": 1, "effect": lambda p: p.add_stat("球速", 2)},
    {"name": "投げ込み", "req_ren": 1, "effect": lambda p: p.add_stat("スタミナ", 1, "制球", 1)},
    {"name": "走り込み", "req_ren": 1, "effect": lambda p: p.add_stat("スタミナ", 2)},
    {"name": "スクワット", "req_ren": 1, "effect": lambda p: p.add_stat("スタミナ", 2)},
    {"name": "変化球練習", "req_ren": 1, "effect": lambda p: p.add_pitch(0.30)},
    {"name": "的あて", "req_ren": 2, "effect": lambda p: p.add_stat("制球", 3)},
    {"name": "タイヤ引き", "req_ren": 2, "effect": lambda p: p.add_stat("スタミナ", 3)},
    {"name": "変化球研究", "req_ren": 3, "effect": lambda p: p.add_pitch(0.70)},
    {"name": "新球種練習", "req_ren": 4, "effect": lambda p: p.learn_new_pitch()},
    {"name": "総合投球練習", "req_ren": 4, "effect": lambda p: p.add_stat("制球", 2, "スタミナ", 1, "球速", 1)}
]

FIELDER_PRACTICES = [
    {"name": "素振り", "req_ren": 1, "effect": lambda p: p.add_stat("ミート", 2)},
    {"name": "筋トレ", "req_ren": 1, "effect": lambda p: p.add_stat("パワー", 2)},
    {"name": "ダッシュ", "req_ren": 1, "effect": lambda p: p.add_stat("走力", 2)},
    {"name": "ノック", "req_ren": 1, "effect": lambda p: p.add_stat("守備力", 2)},
    {"name": "フリー打撃", "req_ren": 2, "effect": lambda p: p.add_stat("ミート", 1, "パワー", 1)},
    {"name": "総合練習", "req_ren": 4, "effect": lambda p: p.add_stat("ミート", 1, "走力", 1, "守備力", 1)}
]

class Player:
    def __init__(self, name, hand, pos, school_name, school_data):
        self.name = name
        self.hand = hand
        self.is_pitcher = (pos == "投手")
        self.pos = pos
        self.school_name = school_name
        self.school = school_data
        self.growth = random.choice(GROWTH_TYPES)
        self.coach_eval = 0
        self.scout_eval = 0
        self.salary = 0
        self.lifetime_salary = 0
        
        self.speed = random.randint(105, 140)
        self.control = random.randint(15, 50)
        self.stamina = random.randint(20, 40)
        self.pitches = {}
        if self.is_pitcher:
            num_pitches = random.choices([1, 2, 3, 4], weights=[35, 45, 19, 1])[0]
            for _ in range(num_pitches):
                ptype = random.choice([p for p in PITCH_TYPES if p not in self.pitches])
                self.pitches[ptype] = random.randint(1, 3)
                
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

    def add_stat(self, stat1, val1, stat2=None, val2=0, stat3=None, val3=0):
        for stat, val in [(stat1, val1), (stat2, val2), (stat3, val3)]:
            if stat == "球速": self.speed += val
            elif stat == "制球": self.control += val
            elif stat == "スタミナ": self.stamina += val
            elif stat == "ミート": self.meet += val
            elif stat == "パワー": self.power += val
            elif stat == "走力": self.run += val
            elif stat == "守備力": self.defense += val

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

def trigger_event(player):
    msgs = []
    r = random.random()
    if r < 0.2:
        msgs.append("✨ **練習が上手く行った！能力が2倍成長した！**")
        player.add_stat("スタミナ", 2) if player.is_pitcher else player.add_stat("パワー", 2)
    elif r < 0.4:
        msgs.append("👍 **練習試合で活躍した！監督の評価が上がった。**")
        player.coach_eval = min(10, player.coach_eval + 1)
    
    scout_chance = 0.25
    if player.school["注"] == 5: scout_chance = 0.80
    elif player.school["注"] == 4: scout_chance = 0.60
    elif player.school["注"] == 3: scout_chance = 0.45
    elif player.school["注"] == 2: scout_chance = 0.35
    
    if random.random() < scout_chance:
        if player.ovr >= 45:
            msgs.append("👀 **スカウトが見に来た。高く評価された！(スカウト評価↑↑)**")
            player.scout_eval = min(10, player.scout_eval + 2)
        elif player.ovr >= 35:
            msgs.append("👀 **スカウトが見に来た。注目された(スカウト評価↑)**")
            player.scout_eval = min(10, player.scout_eval + 1)
    return msgs

# --- Streamlit UI ---
if 'step' not in st.session_state:
    st.session_state.step = 'creation'
    st.session_state.player = None
    st.session_state.turn = 0
    st.session_state.events = []
    st.session_state.schedule = [
        (1, "春", 15), (1, "夏", 16), (1, "秋", 16), (1, "冬", 16),
        (2, "春", 16), (2, "夏", 17), (2, "秋", 17), (2, "冬", 17),
        (3, "春", 17), (3, "夏", 18), (3, "秋", 18)
    ]

st.title("⚾ BASEBALL LIFE")

if st.session_state.step == 'creation':
    st.subheader("選手作成")
    name = st.text_input("名前", "野球 太郎")
    hand = st.selectbox("投打", HANDS)
    pos = st.selectbox("ポジション", POSITIONS)
    school = st.selectbox("進学先高校", list(SCHOOLS.keys()))
    
    if st.button("高校1年目からスタート"):
        st.session_state.player = Player(name, hand, pos, school, SCHOOLS[school])
        st.session_state.step = 'playing'
        st.rerun()

elif st.session_state.step == 'playing':
    p = st.session_state.player
    year, season, age = st.session_state.schedule[st.session_state.turn]
    
    st.markdown("---")
    st.markdown(f"### 高校{year}年生 {season} ({age}歳)")
    st.write(f"**{p.name}** │ {p.pos} │ {p.school_name} │ **OVR: {p.ovr}**")
    
    col1, col2 = st.columns(2)
    with col1:
        if p.is_pitcher:
            st.write(f"球速: {p.speed} km/h")
            st.write(f"制球: {p.control}")
            st.write(f"スタミナ: {p.stamina}")
        else:
            st.write(f"ミート: {p.meet}")
            st.write(f"パワー: {p.power}")
            st.write(f"走力: {p.run}")
            st.write(f"守備力: {p.defense}")
    with col2:
        if p.is_pitcher:
            for i, (ptype, level) in enumerate(p.pitches.items(), 1):
                st.write(f"変化球{i}: {ptype} Lv{level}")
                
    if st.session_state.events:
        st.info("\n".join(st.session_state.events))
        st.session_state.events = []

    st.markdown("---")
    st.subheader("練習メニュー選択 (2つまで)")
    
    prac_list = PITCHER_PRACTICES if p.is_pitcher else FIELDER_PRACTICES
    available = [pr for pr in prac_list if pr["req_ren"] <= p.school["練"]]
    prac_names = [pr["name"] for pr in available]
    
    selected = st.multiselect("練習を選択してください", prac_names, max_selections=2)
    
    if st.button("練習実行＆次の季節へ"):
        if len(selected) != 2:
            st.warning("練習を2つ選んでください！")
        else:
            for s_name in selected:
                practice = next(pr for pr in available if pr["name"] == s_name)
                practice["effect"](p)
            
            st.session_state.events = trigger_event(p)
            st.session_state.turn += 1
            
            if st.session_state.turn >= len(st.session_state.schedule):
                st.session_state.step = 'draft'
            st.rerun()

elif st.session_state.step == 'draft':
    p = st.session_state.player
    st.header("🌸 高校生活終了")
    st.write(f"最終OVR: {p.ovr} / スカウト評価: {p.scout_eval}")
    
    choice = st.selectbox("希望進路", ["プロ志望届", "大学進学", "社会人野球", "独立リーグ", "アメリカの大学進学"])
    if st.button("運命の選択へ"):
        if choice == "プロ志望届" and p.scout_eval >= 5 and p.ovr >= 40:
            st.success("🎉 **ドラフト指名されました！プロ野球選手としてのキャリアがスタートします！**")
        elif choice == "プロ志望届":
            st.error("💦 惜しくも指名漏れ...。次のステージでプロを目指しましょう。")
        else:
            st.info(f"✨ {choice}へ進みます。BASEBALL LIFEは続く...")
        
        if st.button("最初から遊ぶ"):
            st.session_state.clear()
            st.rerun()
