"""
Cricbuzz-Style Live Mobile App Interface for AI DRS & Autonomous Match Engine
"""

def get_mobile_app_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Cricbuzz AI — Live Cricket Match Engine & DRS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #070b14;
            --bg-card: #0f172a;
            --bg-card-light: #1e293b;
            --border-color: rgba(255, 255, 255, 0.08);
            --cricbuzz-green: #00d26a;
            --cricbuzz-header: #001a33;
            --cricbuzz-red: #ff3b30;
            --cricbuzz-yellow: #ffcc00;
            --cricbuzz-blue: #0088ff;
            --text-primary: #ffffff;
            --text-muted: #8e8ea0;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', -apple-system, sans-serif; -webkit-tap-highlight-color: transparent; }

        body {
            background-color: #030712;
            color: var(--text-primary);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 0;
            overflow-x: hidden;
        }

        /* Mobile Device Frame Container */
        .mobile-container {
            width: 100%;
            max-width: 430px;
            height: 100vh;
            max-height: 932px;
            background-color: var(--bg-dark);
            border-radius: 0px;
            display: flex;
            flex-direction: column;
            position: relative;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
            border: 1px solid var(--border-color);
            overflow: hidden;
        }

        @media (min-width: 450px) {
            .mobile-container {
                height: 880px;
                border-radius: 44px;
                border: 12px solid #1f2937;
                margin: 20px 0;
            }
        }

        /* Top Mobile Status Bar */
        .status-bar {
            height: 40px;
            background: var(--cricbuzz-header);
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
            font-size: 0.8rem;
            font-weight: 600;
            color: #d1d5db;
            z-index: 10;
        }

        /* Cricbuzz App Header */
        .app-header {
            background: linear-gradient(180deg, #002244 0%, #00152b 100%);
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .app-title {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .app-title h1 {
            font-size: 1.1rem;
            font-weight: 900;
            letter-spacing: -0.5px;
            color: #ffffff;
        }

        .live-tag {
            background: var(--cricbuzz-red);
            color: #ffffff;
            font-size: 0.65rem;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 4px;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

        /* Main Viewport Content */
        .view-content {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            scrollbar-width: none;
        }

        .view-content::-webkit-scrollbar { display: none; }

        /* Cricbuzz Match Card Header */
        .match-score-card {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border-radius: 16px;
            padding: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
        }

        .team-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .team-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .team-flag {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #374151;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 800;
            color: #fff;
        }

        .team-name {
            font-size: 1rem;
            font-weight: 700;
        }

        .team-score {
            font-size: 1.25rem;
            font-weight: 800;
            color: var(--cricbuzz-green);
        }

        .match-notes {
            font-size: 0.75rem;
            color: var(--cricbuzz-yellow);
            font-weight: 600;
            margin-top: 8px;
            display: flex;
            justify-content: space-between;
            padding-top: 8px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* Ball-by-Ball Recent Deliveries Strip */
        .balls-strip {
            display: flex;
            gap: 6px;
            align-items: center;
            overflow-x: auto;
            padding: 4px 0;
        }

        .ball-pill {
            min-width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #1f2937;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            font-weight: 800;
            color: #d1d5db;
        }

        .ball-pill.four { background: #1e3a8a; color: #60a5fa; border: 1px solid #3b82f6; }
        .ball-pill.six { background: #065f46; color: #34d399; border: 1px solid #10b981; }
        .ball-pill.wicket { background: #881337; color: #f87171; border: 1px solid #ef4444; }

        /* Player Stats Card */
        .section-card {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 14px;
            border: 1px solid var(--border-color);
        }

        .section-title {
            font-size: 0.75rem;
            font-weight: 800;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .batter-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }

        .batter-table th {
            text-align: right;
            color: var(--text-muted);
            font-weight: 600;
            font-size: 0.7rem;
            padding-bottom: 6px;
        }

        .batter-table th:first-child { text-align: left; }

        .batter-table td {
            padding: 8px 0;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            text-align: right;
            font-weight: 600;
        }

        .batter-table td:first-child {
            text-align: left;
            font-weight: 700;
            color: #ffffff;
        }

        .active-striker { color: var(--cricbuzz-green) !important; }

        /* Action Buttons Grid */
        .action-bar {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #00c853 0%, #009624 100%);
            color: #fff;
            border: none;
            padding: 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 800;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            box-shadow: 0 4px 14px rgba(0, 200, 83, 0.3);
            transition: transform 0.1s;
        }

        .btn-primary:active { transform: scale(0.97); }

        .btn-drs {
            background: linear-gradient(135deg, #d50000 0%, #9b0000 100%);
            color: #fff;
            border: none;
            padding: 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 800;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            box-shadow: 0 4px 14px rgba(213, 0, 0, 0.3);
        }

        /* Bottom App Navigation Bar */
        .nav-bar {
            height: 65px;
            background: #00152b;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            justify-content: space-around;
            align-items: center;
            padding-bottom: 8px;
        }

        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            color: var(--text-muted);
            font-size: 0.65rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
        }

        .nav-item.active { color: var(--cricbuzz-green); }
        .nav-icon { font-size: 1.2rem; }

        /* Setup Form Modal */
        .modal {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(3, 7, 18, 0.95);
            backdrop-filter: blur(16px);
            z-index: 50;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .input-group {
            margin-bottom: 12px;
        }

        .input-group label {
            display: block;
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
            margin-bottom: 4px;
            text-transform: uppercase;
        }

        .input-field {
            width: 100%;
            background: #111827;
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 10px 14px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
        }

        /* DRS Camera Visualizer Overlay */
        .drs-modal {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: #000;
            z-index: 60;
            display: flex;
            flex-direction: column;
        }

        .camera-viewfinder {
            flex: 1;
            background: radial-gradient(circle at center, #1e293b 0%, #020617 100%);
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }

        .pitch-overlay {
            width: 140px;
            height: 280px;
            border: 2px solid rgba(16, 185, 129, 0.6);
            position: relative;
            transform: perspective(300px) rotateX(40deg);
            background: rgba(16, 185, 129, 0.05);
        }

        .stumps-overlay {
            width: 30px;
            height: 50px;
            border-top: 3px solid #facc15;
            border-left: 3px solid #facc15;
            border-right: 3px solid #facc15;
            position: absolute;
            top: 10px; left: 55px;
        }

        .ball-trajectory {
            width: 6px;
            height: 200px;
            background: linear-gradient(180deg, #ef4444 0%, #f59e0b 50%, #10b981 100%);
            position: absolute;
            left: 67px; top: 30px;
            border-radius: 4px;
            box-shadow: 0 0 12px #10b981;
        }
    </style>
</head>
<body>

    <div class="mobile-container">
        <!-- Status Bar -->
        <div class="status-bar">
            <span>9:41</span>
            <span>CRICBUZZ AI 5G</span>
            <span>100%</span>
        </div>

        <!-- App Header -->
        <div class="app-header">
            <div class="app-title">
                <h1>cricbuzz <span style="color: var(--cricbuzz-green);">AI</span></h1>
                <span class="live-tag">LIVE DRS</span>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-muted); cursor: pointer;" onclick="openSetup()">⚙️ Setup</div>
        </div>

        <!-- Main Live Match Screen -->
        <div id="screen-match" class="view-content">
            <!-- Score Card -->
            <div class="match-score-card">
                <div class="team-row">
                    <div class="team-info">
                        <div class="team-flag">IND</div>
                        <div class="team-name" id="batting-team-name">India</div>
                    </div>
                    <div class="team-score" id="match-score">33/1 <span style="font-size: 0.85rem; color: #9ca3af;">(2.0)</span></div>
                </div>

                <div class="team-row">
                    <div class="team-info">
                        <div class="team-flag" style="background: #eab308; color: #000;">AUS</div>
                        <div class="team-name" id="bowling-team-name">Australia</div>
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-muted);" id="target-info">Target: 180</div>
                </div>

                <div class="match-notes">
                    <span id="chase-req">Need 147 off 108b</span>
                    <span id="rr-rates">CRR: 16.50 | RRR: 8.17</span>
                </div>
            </div>

            <!-- Recent Ball-by-Ball Strip -->
            <div class="section-card" style="padding: 10px 14px;">
                <div class="section-title">
                    <span>Recent Deliveries</span>
                    <span style="color: var(--cricbuzz-green);" id="situation-badge">STABLE</span>
                </div>
                <div class="balls-strip" id="balls-strip">
                    <div class="ball-pill four">4</div>
                    <div class="ball-pill">1</div>
                    <div class="ball-pill six">6</div>
                    <div class="ball-pill">0</div>
                    <div class="ball-pill">2</div>
                    <div class="ball-pill wicket">W</div>
                </div>
            </div>

            <!-- Batting Card -->
            <div class="section-card">
                <div class="section-title">Batting</div>
                <table class="batter-table">
                    <thead>
                        <tr>
                            <th>BATTER</th>
                            <th>R</th>
                            <th>B</th>
                            <th>4s</th>
                            <th>6s</th>
                            <th>SR</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><span class="active-striker" id="b1-name">Suryakumar Yadav *</span></td>
                            <td id="b1-r">11</td>
                            <td id="b1-b">3</td>
                            <td id="b1-4s">1</td>
                            <td id="b1-6s">1</td>
                            <td id="b1-sr">366.7</td>
                        </tr>
                        <tr>
                            <td><span id="b2-name">Virat Kohli</span></td>
                            <td id="b2-r">14</td>
                            <td id="b2-b">5</td>
                            <td id="b2-4s">3</td>
                            <td id="b2-6s">0</td>
                            <td id="b2-sr">280.0</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Bowling Card -->
            <div class="section-card">
                <div class="section-title">Bowling</div>
                <table class="batter-table">
                    <thead>
                        <tr>
                            <th>BOWLER</th>
                            <th>O</th>
                            <th>M</th>
                            <th>R</th>
                            <th>W</th>
                            <th>ECO</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td id="bw-name">Mitchell Starc</td>
                            <td id="bw-o">2.0</td>
                            <td id="bw-m">0</td>
                            <td id="bw-r">33</td>
                            <td id="bw-w">1</td>
                            <td id="bw-eco">16.5</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Interactive Action Controls -->
            <div class="action-bar">
                <button class="btn-primary" onclick="bowlBall()">⚾ Bowl Ball</button>
                <button class="btn-drs" onclick="triggerDRSModal()">📹 AI DRS Review</button>
            </div>
        </div>

        <!-- Setup Screen Modal -->
        <div id="screen-setup" class="modal" style="display: none;">
            <h2 style="font-size: 1.3rem; font-weight: 800; margin-bottom: 16px; color: #fff;">Match Setup & Toss</h2>

            <div class="input-group">
                <label>Batting Team</label>
                <input id="in-team-a" class="input-field" value="Team India">
            </div>

            <div class="input-group">
                <label>Bowling Team</label>
                <input id="in-team-b" class="input-field" value="Team Australia">
            </div>

            <div class="input-group">
                <label>Opening Striker</label>
                <input id="in-striker" class="input-field" value="Suryakumar Yadav">
            </div>

            <div class="input-group">
                <label>Opening Non-Striker</label>
                <input id="in-non-striker" class="input-field" value="Virat Kohli">
            </div>

            <div class="input-group">
                <label>Opening Bowler</label>
                <input id="in-bowler" class="input-field" value="Mitchell Starc">
            </div>

            <div class="input-group">
                <label>Target Runs (Chase)</label>
                <input id="in-target" type="number" class="input-field" value="180">
            </div>

            <button class="btn-primary" style="margin-top: 10px;" onclick="saveMatchSetup()">🪙 Flip Toss & Start Match</button>
        </div>

        <!-- DRS Camera Overlay Modal -->
        <div id="screen-drs" class="drs-modal" style="display: none;">
            <div class="app-header">
                <div class="app-title">
                    <h1 style="color: #ef4444;">AI DRS VIEW FINDER</h1>
                </div>
                <div style="font-size: 0.8rem; color: #fff; cursor: pointer;" onclick="closeDRSModal()">✖ Close</div>
            </div>

            <div class="camera-viewfinder">
                <div class="pitch-overlay">
                    <div class="stumps-overlay"></div>
                    <div class="ball-trajectory" id="traj-line"></div>
                </div>
            </div>

            <div style="background: #0f172a; padding: 16px; border-top: 1px solid var(--border-color);">
                <div style="text-align: center; margin-bottom: 10px;">
                    <div style="font-size: 0.7rem; color: var(--text-muted);">THIRD UMPIRE DECISION</div>
                    <div id="drs-verdict" style="font-size: 1.6rem; font-weight: 900; color: #34d399;">NOT OUT</div>
                    <div id="drs-reason" style="font-size: 0.75rem; color: #d1d5db; margin-top: 2px;">Impact outside off stump</div>
                </div>

                <button class="btn-primary" style="background: #2563eb; width: 100%;" onclick="runSyntheticDRS()">Re-Track Delivery 🔍</button>
            </div>
        </div>

        <!-- Bottom Navigation -->
        <div class="nav-bar">
            <div class="nav-item active" onclick="switchNav('screen-match')">
                <span class="nav-icon">🏏</span>
                <span>Match</span>
            </div>
            <div class="nav-item" onclick="triggerDRSModal()">
                <span class="nav-icon">📹</span>
                <span>DRS AI</span>
            </div>
            <div class="nav-item" onclick="openSetup()">
                <span class="nav-icon">⚙️</span>
                <span>Setup</span>
            </div>
        </div>
    </div>

    <script>
        const matchId = "MOBILE_APP_MATCH";

        async function initApp() {
            try {
                await fetch('/api/v1/match/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        match_id: matchId,
                        team_a: "Team India",
                        team_b: "Team Australia",
                        striker_name: "Suryakumar Yadav",
                        non_striker_name: "Virat Kohli",
                        bowler_name: "Mitchell Starc",
                        total_overs: 20,
                        target: 180
                    })
                });
            } catch(e) {}
        }
        initApp();

        async function bowlBall() {
            const options = [0, 1, 2, 4, 6, 'W'];
            const res = options[Math.floor(Math.random() * options.length)];

            const isW = (res === 'W');
            const runs = isW ? 0 : res;

            await fetch(`/api/v1/match/${matchId}/delivery?is_validated=true`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    delivery_id: "DELIV_" + Date.now(),
                    over_number: 2,
                    ball_number_in_over: 1,
                    striker_name: "Suryakumar Yadav",
                    non_striker_name: "Virat Kohli",
                    bowler_name: "Mitchell Starc",
                    runs_off_bat: runs,
                    is_wicket: isW,
                    wicket_type: isW ? "LBW" : null,
                    ball_speed_kmh: 140 + Math.random() * 8
                })
            });

            // Update UI
            const sb = await (await fetch(`/api/v1/match/${matchId}/scoreboard`)).json();
            const cards = await (await fetch(`/api/v1/match/${matchId}/cards`)).json();
            const cond = await (await fetch(`/api/v1/match/${matchId}/condition-panel`)).json();

            document.getElementById('match-score').innerHTML = `${sb.score}/${sb.wickets} <span style="font-size: 0.85rem; color: #9ca3af;">(${sb.overs_formatted})</span>`;
            document.getElementById('chase-req').innerText = `Need ${cond.runs_required} off ${cond.balls_remaining}b`;
            document.getElementById('rr-rates').innerText = `CRR: ${cond.current_run_rate} | RRR: ${cond.required_run_rate}`;
            document.getElementById('situation-badge').innerText = cond.situation_classification;

            // Strip
            const pill = document.createElement('div');
            pill.className = `ball-pill ${runs === 4 ? 'four' : runs === 6 ? 'six' : isW ? 'wicket' : ''}`;
            pill.innerText = isW ? 'W' : runs;
            document.getElementById('balls-strip').prepend(pill);

            // Cards
            document.getElementById('b1-name').innerText = cards.striker_card.name + " *";
            document.getElementById('b1-r').innerText = cards.striker_card.runs;
            document.getElementById('b1-b').innerText = cards.striker_card.balls;
            document.getElementById('b1-4s').innerText = cards.striker_card.fours;
            document.getElementById('b1-6s').innerText = cards.striker_card.sixes;
            document.getElementById('b1-sr').innerText = cards.striker_card.strike_rate;

            document.getElementById('b2-name').innerText = cards.non_striker_card.name;
            document.getElementById('b2-r').innerText = cards.non_striker_card.runs;
            document.getElementById('b2-b').innerText = cards.non_striker_card.balls;
            document.getElementById('b2-4s').innerText = cards.non_striker_card.fours;
            document.getElementById('b2-6s').innerText = cards.non_striker_card.sixes;
            document.getElementById('b2-sr').innerText = cards.non_striker_card.strike_rate;

            document.getElementById('bw-name').innerText = cards.bowler_card.name;
            document.getElementById('bw-o').innerText = cards.bowler_card.overs_str;
            document.getElementById('bw-m').innerText = cards.bowler_card.maidens;
            document.getElementById('bw-r').innerText = cards.bowler_card.runs_conceded;
            document.getElementById('bw-w').innerText = cards.bowler_card.wickets;
            document.getElementById('bw-eco').innerText = cards.bowler_card.economy;
        }

        async function saveMatchSetup() {
            const teamA = document.getElementById('in-team-a').value;
            const teamB = document.getElementById('in-team-b').value;
            const target = parseInt(document.getElementById('in-target').value);

            await fetch('/api/v1/match/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    match_id: matchId,
                    team_a: teamA,
                    team_b: teamB,
                    striker_name: document.getElementById('in-striker').value,
                    non_striker_name: document.getElementById('in-non-striker').value,
                    bowler_name: document.getElementById('in-bowler').value,
                    total_overs: 20,
                    target: target
                })
            });

            await fetch(`/api/v1/match/${matchId}/toss`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ caller_team: teamA, caller_call: "HEADS", winner_decision: "BAT" })
            });

            document.getElementById('batting-team-name').innerText = teamA;
            document.getElementById('bowling-team-name').innerText = teamB;
            document.getElementById('target-info').innerText = "Target: " + target;
            document.getElementById('screen-setup').style.display = 'none';
        }

        function openSetup() { document.getElementById('screen-setup').style.display = 'flex'; }
        function triggerDRSModal() { document.getElementById('screen-drs').style.display = 'flex'; runSyntheticDRS(); }
        function closeDRSModal() { document.getElementById('screen-drs').style.display = 'none'; }

        async function runSyntheticDRS() {
            document.getElementById('drs-verdict').innerText = 'TRACKING...';
            document.getElementById('drs-verdict').style.color = '#facc15';

            setTimeout(() => {
                document.getElementById('drs-verdict').innerText = 'NOT OUT';
                document.getElementById('drs-verdict').style.color = '#34d399';
                document.getElementById('drs-reason').innerText = 'Impact outside off stump with shot offered';
            }, 500);
        }
    </script>
</body>
</html>"""
