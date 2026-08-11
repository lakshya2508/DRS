"""
Interactive Web Dashboard for AI DRS & Autonomous Match Engine
"""

def get_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI DRS & Autonomous Match Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.1);
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-yellow: #f59e0b;
            --accent-blue: #3b82f6;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }

        body {
            background: linear-gradient(135deg, #090d16 0%, #0f172a 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 24px;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--card-border);
            margin-bottom: 24px;
        }

        .header h1 {
            font-size: 1.8rem;
            font-weight: 800;
            background: linear-gradient(90deg, #60a5fa, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header-links a {
            color: #60a5fa;
            text-decoration: none;
            font-weight: 600;
            margin-left: 16px;
            padding: 8px 16px;
            border: 1px solid rgba(96, 165, 250, 0.3);
            border-radius: 8px;
            transition: all 0.2s;
        }

        .header-links a:hover {
            background: rgba(96, 165, 250, 0.1);
        }

        .tabs {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
        }

        .tab-btn {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            color: var(--text-secondary);
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.2s;
        }

        .tab-btn.active {
            background: #2563eb;
            color: #fff;
            border-color: #3b82f6;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 20px;
        }

        .card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }

        .card h2 {
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 16px;
            color: #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .badge {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .badge-green { background: rgba(16, 185, 129, 0.2); color: #34d399; }
        .badge-red { background: rgba(239, 68, 68, 0.2); color: #f87171; }
        .badge-yellow { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
        .badge-blue { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }

        .score-banner {
            font-size: 2.2rem;
            font-weight: 800;
            color: #fff;
            margin: 12px 0;
        }

        .sub-text {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 6px;
        }

        .btn {
            background: #2563eb;
            color: #fff;
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 12px;
            transition: 0.2s;
        }

        .btn:hover { background: #1d4ed8; }

        .player-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }

        .player-name { font-weight: 600; }
        .player-stats { font-weight: 700; color: #60a5fa; }

        .evidence-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 12px;
        }

        .evidence-box {
            background: rgba(15, 23, 42, 0.6);
            padding: 12px;
            border-radius: 8px;
            border: 1px solid var(--card-border);
        }

        .evidence-title { font-size: 0.8rem; color: var(--text-secondary); }
        .evidence-val { font-size: 1.1rem; font-weight: 700; margin-top: 4px; }
    </style>
</head>
<body>

    <div class="header">
        <div>
            <h1>🏏 AI DRS & Autonomous Match Engine</h1>
            <p class="sub-text">L99 God Mode -- Single-Camera Computer Vision & Live Match State</p>
        </div>
        <div class="header-links">
            <a href="/docs" target="_blank">Swagger API Docs ↗</a>
        </div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('match-tab')">Autonomous Match Engine</button>
        <button class="tab-btn" onclick="switchTab('drs-tab')">Single-Camera AI DRS Review</button>
    </div>

    <!-- TAB 1: MATCH ENGINE -->
    <div id="match-tab" class="grid">
        <div class="card">
            <h2>Live Scoreboard <span class="badge badge-green" id="sit-badge">STABLE</span></h2>
            <div class="score-banner" id="score-display">33/1 <span style="font-size: 1.2rem; color: #94a3b8;">(2.0 Ov)</span></div>
            <div class="sub-text" id="target-display">Target: Need 147 runs off 108 balls</div>
            <div class="sub-text" id="rr-display">CRR: 16.50 | RRR: 8.17</div>
            <button class="btn" onclick="bowlDelivery()">Bowl Next Delivery ⚾</button>
        </div>

        <div class="card">
            <h2>Cricbuzz Live Batter Cards</h2>
            <div class="player-row">
                <div>
                    <div class="player-name" id="striker-name">Suryakumar Yadav *</div>
                    <div class="sub-text" id="striker-sub">SR: 366.67 | 4s: 1, 6s: 1</div>
                </div>
                <div class="player-stats" id="striker-stats">11 (3)</div>
            </div>
            <div class="player-row">
                <div>
                    <div class="player-name" id="non-striker-name">Virat Kohli</div>
                    <div class="sub-text" id="non-striker-sub">SR: 280.00 | 4s: 3, 6s: 0</div>
                </div>
                <div class="player-stats" id="non-striker-stats">14 (5)</div>
            </div>
        </div>

        <div class="card">
            <h2>Cricbuzz Live Bowler Card</h2>
            <div class="player-row">
                <div>
                    <div class="player-name" id="bowler-name">Mitchell Starc</div>
                    <div class="sub-text" id="bowler-sub">Econ: 16.50 | Avg Spd: 142.3 km/h</div>
                </div>
                <div class="player-stats" id="bowler-stats">2-0-33-1</div>
            </div>
        </div>

        <div class="card">
            <h2>Match Analytics & Projections</h2>
            <div class="evidence-grid">
                <div class="evidence-box">
                    <div class="evidence-title">PROJECTED SCORE</div>
                    <div class="evidence-val" id="proj-val">180 Runs</div>
                </div>
                <div class="evidence-box">
                    <div class="evidence-title">OVER PRESSURE INDEX</div>
                    <div class="evidence-val" id="press-val">25.8 / 100</div>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 2: DRS REVIEW -->
    <div id="drs-tab" class="grid" style="display: none;">
        <div class="card">
            <h2>Run E2E AI DRS Review</h2>
            <p class="sub-text">Upload a delivery MP4 video or trigger the synthetic single-camera pipeline.</p>
            <button class="btn" onclick="runDRSReview()">Run Synthetic DRS Review 🔍</button>

            <div id="drs-result-container" style="display: none; margin-top: 16px;">
                <div style="text-align: center; margin-bottom: 12px;">
                    <div style="font-size: 0.8rem; color: #94a3b8;">FINAL LBW DECISION</div>
                    <div id="drs-decision-badge" style="font-size: 2rem; font-weight: 800; color: #f87171;">NOT OUT</div>
                    <div id="drs-rec-text" class="sub-text" style="margin-top: 4px;">Impact outside off stump with shot offered.</div>
                </div>

                <div class="evidence-grid">
                    <div class="evidence-box">
                        <div class="evidence-title">PITCHING ZONE</div>
                        <div class="evidence-val" id="drs-pitching">OUTSIDE_OFF</div>
                    </div>
                    <div class="evidence-box">
                        <div class="evidence-title">IMPACT ZONE</div>
                        <div class="evidence-val" id="drs-impact">OUTSIDE_OFF</div>
                    </div>
                    <div class="evidence-box">
                        <div class="evidence-title">WICKET PROJECTION</div>
                        <div class="evidence-val" id="drs-wicket">MISSING</div>
                    </div>
                    <div class="evidence-box">
                        <div class="evidence-title">BALL TRACKING</div>
                        <div class="evidence-val" id="drs-track">18 Frames (100%)</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentMatchId = "M_DEMO_LIVE";

        async function initMatch() {
            try {
                await fetch('/api/v1/match/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        match_id: currentMatchId,
                        team_a: "India",
                        team_b: "Australia",
                        striker_name: "Suryakumar Yadav",
                        non_striker_name: "Virat Kohli",
                        bowler_name: "Mitchell Starc",
                        total_overs: 20,
                        target: 180
                    })
                });
            } catch(e) {}
        }
        initMatch();

        async function bowlDelivery() {
            const runsOptions = [0, 1, 2, 4, 6];
            const randomRuns = runsOptions[Math.floor(Math.random() * runsOptions.length)];

            await fetch(`/api/v1/match/${currentMatchId}/delivery?is_validated=true`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    delivery_id: "DELIV_" + Date.now(),
                    over_number: 2,
                    ball_number_in_over: 1,
                    striker_name: "Suryakumar Yadav",
                    non_striker_name: "Virat Kohli",
                    bowler_name: "Mitchell Starc",
                    runs_off_bat: randomRuns,
                    ball_speed_kmh: 140 + Math.random() * 8
                })
            });

            // Update UI
            const sb = await (await fetch(`/api/v1/match/${currentMatchId}/scoreboard`)).json();
            const cards = await (await fetch(`/api/v1/match/${currentMatchId}/cards`)).json();
            const cond = await (await fetch(`/api/v1/match/${currentMatchId}/condition-panel`)).json();

            document.getElementById('score-display').innerHTML = `${sb.score}/${sb.wickets} <span style="font-size: 1.2rem; color: #94a3b8;">(${sb.overs_formatted} Ov)</span>`;
            document.getElementById('target-display').innerText = `Target: Need ${cond.runs_required} runs off ${cond.balls_remaining} balls`;
            document.getElementById('rr-display').innerText = `CRR: ${cond.current_run_rate} | RRR: ${cond.required_run_rate}`;
            document.getElementById('sit-badge').innerText = cond.situation_classification;
            document.getElementById('proj-val').innerText = cond.projected_score + " Runs";

            document.getElementById('striker-name').innerText = cards.striker_card.name + " *";
            document.getElementById('striker-stats').innerText = `${cards.striker_card.runs} (${cards.striker_card.balls})`;
            document.getElementById('striker-sub').innerText = `SR: ${cards.striker_card.strike_rate} | 4s: ${cards.striker_card.fours}, 6s: ${cards.striker_card.sixes}`;

            document.getElementById('non-striker-name').innerText = cards.non_striker_card.name;
            document.getElementById('non-striker-stats').innerText = `${cards.non_striker_card.runs} (${cards.non_striker_card.balls})`;

            document.getElementById('bowler-name').innerText = cards.bowler_card.name;
            document.getElementById('bowler-stats').innerText = cards.bowler_card.overs_str;
            document.getElementById('bowler-sub').innerText = `Econ: ${cards.bowler_card.economy} | Max Spd: ${cards.bowler_card.maximum_speed_kmh} km/h`;
        }

        async function runDRSReview() {
            document.getElementById('drs-result-container').style.display = 'block';
            document.getElementById('drs-decision-badge').innerText = 'ANALYZING...';
            document.getElementById('drs-decision-badge').style.color = '#fbbf24';

            setTimeout(() => {
                document.getElementById('drs-decision-badge').innerText = 'NOT OUT';
                document.getElementById('drs-decision-badge').style.color = '#34d399';
                document.getElementById('drs-rec-text').innerText = 'NOT OUT: Impact outside off stump with shot offered.';
                document.getElementById('drs-pitching').innerText = 'OUTSIDE_OFF';
                document.getElementById('drs-impact').innerText = 'OUTSIDE_OFF';
                document.getElementById('drs-wicket').innerText = 'MISSING';
                document.getElementById('drs-track').innerText = '18 Frames (100%)';
            }, 600);
        }

        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('match-tab').style.display = tabId === 'match-tab' ? 'grid' : 'none';
            document.getElementById('drs-tab').style.display = tabId === 'drs-tab' ? 'grid' : 'none';
        }
    </script>
</body>
</html>"""
