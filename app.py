import streamlit as st
import random

# --- 定数・データ定義 ---
HANDS = ["右投右打", "右投左打", "左投右打", "左投左打", "右投両打", "左投両打"]
POSITIONS = ["投手", "捕手", "一塁手", "二塁手", "三塁手", "遊撃手", "左翼手", "中堅手", "右翼手"]
GROWTH_TYPES = ["超晩成", "晩成", "緩やか晩成", "普通", "緩やか早熟", "早熟", "超早熟"]
PITCH_TYPES = ["スライダー", "カットボール", "カーブ", "Dカーブ", "フォーク", "SFF", "チェンジアップ", "シンカー", "シュート", "ツーシーム"]

# プロ野球球団リスト（スカウト調査書用）
PRO_TEAMS = ["阪神タイガース", "読売ジャイアンツ", "広島東洋カープ", "横浜DeNAベイスターズ", "東京ヤクルトスワローズ", "中日ドラゴンズ", 
             "オリックス・バファローズ", "千葉ロッテマリーンズ", "福岡ソフトバンクホークス", "東北楽天ゴールデンイーグルス", "埼玉西武ライオンズ", "北海道日本ハムファイターズ"]

# 学校データ
SCHOOLS = {
    "大阪桐蔭": {"甲": 5, "注": 5, "層": 5, "練": 5},
    "神村学園": {"甲": 4, "注": 5, "層": 4, "練": 5},
    "早稲田実業": {"甲": 3, "注": 4, "層": 3, "練": 4},
    "エナジックスポーツ学院": {"甲": 2, "注": 2, "層": 2, "練": 5},
    "佐賀商業": {"甲": 2, "注": 2, "層": 2, "練": 3},
    "笠岡工業": {"甲": 0.1, "注": 1, "層": 0.5, "練": 1}
}

# 練習メニュー定義
PITCHER_PRACTICES = [
    {"name": "フォームチェック", "req_ren": 0, "effect": lambda p: p.add_stat("制球", 1, "球速", 1)},
    {"name": "球速測定", "req_ren": 0, "effect": lambda p: p.add_stat("球速", 2)},
    {"name": "投げ込み", "req_ren": 0, "effect": lambda p: p.add_stat("スタミナ", 1, "制球", 1)},
    {"name": "走り込み", "req_ren": 0, "effect": lambda p: p.add_stat("スタミナ", 2)},
    {"name": "スクワット", "req_ren": 0, "effect": lambda p: p.add_stat("スタミナ", 2)},
    {"name": "変化球練習", "req_ren": 0, "effect": lambda p: p.add_pitch(0.30)},
    {"name": "的あて", "req_ren": 2, "effect": lambda p: p.add_stat("制球", 3)},
    {"name": "タイヤ引き", "req_ren": 2, "effect": lambda p: p.add_stat("スタミナ", 3)},
    {"name": "変化球研究", "req_ren": 3, "effect": lambda p: p.add_pitch(0.70)},
    {"name": "新球種練習", "req_ren": 4, "effect": lambda p: p.learn_new_pitch()},
    {"name": "総合投球練習", "req_ren": 4, "effect": lambda p: p.add_stat("制球", 2, "スタミナ", 1, "球速", 1)}
]

FIELDER_PRACTICES = [
    {"name": "素振り", "req_ren": 0, "effect": lambda p: p.add_stat("ミート", 2)},
    {"name": "筋トレ", "req_ren": 0, "effect": lambda p: p.add_stat("パワー", 2)},
    {"name": "ダッシュ", "req_ren": 0, "effect": lambda p: p.add_stat("走力", 2)},
    {"name": "ノック", "req_ren": 0, "effect": lambda p: p.add_stat("守備力", 2)},
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
        self.investigated_teams = [] # 調査書を受け取った球団リスト
        
        # 初期能力
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
            # 球速のOVR換算
            if self.speed <= 150:
                speed_val = 55 + (self.speed - 145)
            else:
                speed_val = 60 + (self.speed - 150) * 2
                
            # 変化球のOVR換算
            total_pitch = sum(self.pitches.values())
            if total_pitch == 0: pitch_val = 0
            elif total_pitch == 1: pitch_val = 5
            elif total_pitch == 2: pitch_val = 20
            elif total_pitch == 3: pitch_val = 25
            elif total_pitch == 4: pitch_val = 40
            elif total_pitch == 5: pitch_val = 50
            else: pitch_val = 50 + (total_pitch - 5) * 5

            return int((self.control + self.stamina + speed_val + pitch_val) / 4)
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

def trigger_events(player, season):
    msgs = []
    
    # 1. 通常イベント（練習・監督）
    if random.random() < 0.2:
        msgs.append("✨ **練習が上手く行った！2倍成長した。**")
        player.add_stat("スタミナ", 2) if player.is_pitcher else player.add_stat("パワー", 2)
    if random.random() < 0.4:
        msgs.append("👍 **練習試合で活躍した！監督の評価が上がった。**")
        player.coach_eval = min(10, player.coach_eval + 1)
    
    # 2. スカウト視察イベント
    scout_chance = 0.25
    if player.school["注"] >= 5: scout_chance = 0.80
    elif player.school["注"] >= 4: scout_chance = 0.60
    elif player.school["注"] >= 3: scout_chance = 0.45
    elif player.school["注"] >= 2: scout_chance = 0.35
    
    if random.random() < scout_chance:
        eval_up = 0
        if player.is_pitcher:
            if player.ovr >= 45 or player.speed >= 147: eval_up = 2
            elif player.ovr >= 35 or player.speed >= 142: eval_up = 1
        else:
            max_stat = max(player.meet, player.power, player.run, player.defense)
            if player.ovr >= 45 or max_stat >= 65: eval_up = 2
            elif player.ovr >= 35 or max_stat >= 50: eval_up = 1

        if eval_up == 2:
            msgs.append("👀 **スカウトが見に来た。「高く評価された」(スカウト評価2段階上昇)**")
            player.scout_eval = min(10, player.scout_eval + 2)
        elif eval_up == 1:
            msgs.append("👀 **スカウトが見に来た。「注目された」(スカウト評価1段階上昇)**")
            player.scout_eval = min(10, player.scout_eval + 1)

    # 3. スカウト面談・調査書イベント
    invest_prob = 0
    if 3 <= player.scout_eval <= 5: invest_prob = 0.25
    elif 6 <= player.scout_eval <= 7: invest_prob = 0.50
    elif player.scout_eval >= 8: invest_prob = 1.0

    if invest_prob > 0 and random.random() < invest_prob:
        available_teams = [t for t in PRO_TEAMS if t not in player.investigated_teams]
        if available_teams:
            num_teams = random.randint(1, 3) if player.scout_eval >= 8 else 1
            num_teams = min(num_teams, len(available_teams))
            
            teams = random.sample(available_teams, num_teams)
            player.investigated_teams.extend(teams)
            msgs.append(f"✉️ **スカウトと面談をした。{ '、'.join(teams) }から調査書を受け取った。**")

    # 4. 夏大会イベント
    if season == "夏":
        msgs.append("---")
        k_val = player.school["甲"]
        s_val = player.school["層"]
        
        pref_prob = 0.01
        if k_val >= 5: pref_prob = 0.85
        elif k_val >= 4: pref_prob = 0.70
        elif k_val >= 3: pref_prob = 0.45
        elif k_val >= 2: pref_prob = 0.20
        elif k_val >= 1: pref_prob = 0.05
        
        if random.random() < pref_prob:
            msgs.append("🏆 **都道府県大会を優勝した！甲子園出場決定！**")
            
            total_ks = k_val + s_val
            koshien_prob = 0.05
            if total_ks >= 10: koshien_prob = 0.75
            elif total_ks >= 7: koshien_prob = 0.25
            
            if random.random() < koshien_prob:
                msgs.append("🥇 **甲子園大会で優勝した！！全国制覇達成！**")
                player.scout_eval = min(10, player.scout_eval + 3)
            else:
                msgs.append("⚾ 甲子園大会で敗退した。")
                player.scout_eval = min(10, player.scout_eval + 1)
        else:
            msgs.append("💦 都道府県大会で敗退した。")

    return msgs

# --- Streamlit UI 状態管理 ---
if 'step' not in st.session_state:
    st.session_state.step = 'creation'
    st.session_state.player = None
    st.session_state.turn = 0
    st.session_state.current_practices = []
    st.session_state.turn_results = []
    st.session_state.schedule = [
        (1, "春", 15), (1, "夏", 16), (1, "秋", 16), (1, "冬", 16),
        (2, "春", 16), (2, "夏", 17), (2, "秋", 17), (2, "冬", 17),
        (3, "春", 17), (3, "夏", 18), (3, "秋", 18)
    ]

# --- メイン画面 ---
st.title("⚾ BASEBALL LIFE")

# 1. 選手作成フェーズ
if st.session_state.step == 'creation':
    st.subheader("選手名とポジションを選んでください。")
    name = st.text_input("名前", "野球 太郎")
    hand = st.selectbox("投打", HANDS)
    pos = st.selectbox("ポジション", POSITIONS)
    school = st.selectbox("進学先高校", list(SCHOOLS.keys()))
    
    if st.button("[高校1年目からスタート]"):
        st.session_state.player = Player(name, hand, pos, school, SCHOOLS[school])
        st.session_state.step = 'playing'
        st.rerun()

# 2. プレイフェーズ（練習選択）
elif st.session_state.step == 'playing':
    p = st.session_state.player
    year, season, age = st.session_state.schedule[st.session_state.turn]
    
    st.markdown("---")
    st.write(f"**年俸 {p.salary}円 / 生涯 {p.lifetime_salary}円**")
    st.markdown(f"### 高校{year}年生 {season}")
    st.write(f"**{p.name}** │ {age}歳 │ {p.pos} │ {p.school_name} │ **能力OVR値: {p.ovr}**")
    
    # ステータス表示
    col1, col2 = st.columns(2)
    with col1:
        if p.is_pitcher:
            st.write(f"球速   {p.speed} km/h")
            st.write(f"制球   {p.control}")
            st.write(f"スタミナ {p.stamina}")
        else:
            st.write(f"ミート  {p.meet}")
            st.write(f"パワー  {p.power}")
            st.write(f"走力   {p.run}")
            st.write(f"守備力  {p.defense}")
    with col2:
        if p.is_pitcher:
            for i, (ptype, level) in enumerate(p.pitches.items(), 1):
                st.write(f"変化球{i}  {ptype} Lv{level}")
                
    st.markdown("---")
    
    # 練習メニューの生成（ターン初めのみ）
    ren_val = p.school["練"]
    if not st.session_state.current_practices:
        if ren_val >= 5: num_options = 6
        elif ren_val >= 4: num_options = 5
        elif ren_val >= 3: num_options = 4
        elif ren_val >= 2: num_options = 3
        else: num_options = 2
        
        prac_list = PITCHER_PRACTICES if p.is_pitcher else FIELDER_PRACTICES
        available = [pr for pr in prac_list if pr["req_ren"] <= ren_val]
        st.session_state.current_practices = random.sample(available, min(num_options, len(available)))

    # 選択可能数の判定
    max_select = 1 if ren_val <= 1 else 2
    st.write(f"練習の中から**{max_select}つ**選択 (学校の練習環境: ☆{ren_val})")
    
    prac_names = [pr["name"] for pr in st.session_state.current_practices]
    selected = st.multiselect(" ", prac_names, max_selections=max_select)
    
    if st.button("練習実行"):
        if len(selected) == 0:
            st.warning("練習を選択してください！")
        else:
            # 練習効果の適用
            for s_name in selected:
                practice = next(pr for pr in st.session_state.current_practices if pr["name"] == s_name)
                practice["effect"](p)
            
            # イベント発生
            st.session_state.turn_results = trigger_events(p, season)
            st.session_state.step = 'results'
            st.rerun()

# 3. 結果・イベント表示フェーズ
elif st.session_state.step == 'results':
    st.subheader("📝 実行結果・イベント")
    
    if len(st.session_state.turn_results) > 0:
        for msg in st.session_state.turn_results:
            st.info(msg)
    else:
        st.write("特に変わった出来事はなかった。（能力上昇中）")
        
    if st.button("次の季節へ"):
        st.session_state.turn += 1
        st.session_state.current_practices = [] # 次のターンのためにリセット
        
        if st.session_state.turn >= len(st.session_state.schedule):
            st.session_state.step = 'draft'
        else:
            st.session_state.step = 'playing'
        st.rerun()

# 4. ドラフト・進路フェーズ
elif st.session_state.step == 'draft':
    p = st.session_state.player
    st.markdown("---")
    st.header("🌸 高校３年生 秋")
    st.write(f"**{p.name}** │ 18歳 │ {p.pos} │ {p.school_name}")
    st.write(f"最終 能力OVR値: **{p.ovr}** / スカウト評価: **{p.scout_eval}**")
    if len(p.investigated_teams) > 0:
        st.write(f"✉️ **調査書獲得球団:** {', '.join(p.investigated_teams)}")
    
    choice = st.selectbox("希望進路", ["", "プロ志望届", "大学進学", "社会人野球", "独立リーグ", "アメリカの大学進学"])
    
    if choice != "":
        if st.button("進路決定"):
            st.markdown("---")
            if choice == "プロ志望届":
                # OVRとスカウト評価による独自ドラフト判定
                if p.scout_eval >= 6 and p.ovr >= 40:
                    team = random.choice(p.investigated_teams) if p.investigated_teams else random.choice(PRO_TEAMS)
                    st.success(f"🎉 **ドラフト指名！ {team}から指名を受けました！** プロ野球選手としてのキャリアがスタートします！")
                elif p.scout_eval >= 4 and p.ovr >= 35 and random.random() < 0.3:
                    team = random.choice(p.investigated_teams) if p.investigated_teams else random.choice(PRO_TEAMS)
                    st.success(f"🎉 **ドラフト下位指名！ {team}から指名を受けました！** プロの世界に飛び込みます！")
                else:
                    st.error("💦 惜しくも指名漏れ...。次のステージでプロを目指しましょう。")
            else:
                st.info(f"✨ {choice}へ進学/入団が決定しました！ 新たなステージで BASEBALL LIFE は続く...")
            
            if st.button("最初から遊ぶ"):
                st.session_state.clear()
                st.rerun()
