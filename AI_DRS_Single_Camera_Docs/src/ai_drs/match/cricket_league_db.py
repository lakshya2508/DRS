"""
Cricket League Database — Real IPL, T20I, ODI, Test teams and player rosters.
"""

from typing import Dict, List
from pydantic import BaseModel


class PlayerProfile(BaseModel):
    player_id:     str
    name:          str
    role:          str
    batting_style: str
    bowling_style: str
    nationality:   str
    jersey_number: int


class TeamRoster(BaseModel):
    team_id:    str
    team_name:  str
    short_name: str
    league:     str
    home_ground: str
    players:    List[PlayerProfile]


def _p(pid, name, role, bat, bowl, nat, num) -> PlayerProfile:
    return PlayerProfile(player_id=pid, name=name, role=role,
                         batting_style=bat, bowling_style=bowl,
                         nationality=nat, jersey_number=num)


IPL_TEAMS: Dict[str, TeamRoster] = {
    "MI": TeamRoster(team_id="MI", team_name="Mumbai Indians", short_name="MI",
        league="IPL", home_ground="Wankhede Stadium, Mumbai", players=[
        _p("mi_01","Rohit Sharma","BATTER","RHB","None","IND",45),
        _p("mi_02","Suryakumar Yadav","BATTER","RHB","None","IND",63),
        _p("mi_03","Ishan Kishan","WK_BATTER","LHB","None","IND",32),
        _p("mi_04","Hardik Pandya","ALL_ROUNDER","RHB","RFM","IND",228),
        _p("mi_05","Tilak Varma","BATTER","LHB","None","IND",9),
        _p("mi_06","Tim David","BATTER","RHB","None","SGP",8),
        _p("mi_07","Jasprit Bumrah","BOWLER","RHB","RF","IND",93),
        _p("mi_08","Gerald Coetzee","BOWLER","RHB","RF","RSA",21),
        _p("mi_09","Piyush Chawla","BOWLER","RHB","LB","IND",11),
        _p("mi_10","Trent Boult","BOWLER","LHB","LFM","NZL",18),
        _p("mi_11","Naman Dhir","ALL_ROUNDER","RHB","RMS","IND",19),
    ]),
    "CSK": TeamRoster(team_id="CSK", team_name="Chennai Super Kings", short_name="CSK",
        league="IPL", home_ground="MA Chidambaram Stadium, Chennai", players=[
        _p("csk_01","MS Dhoni","WK_BATTER","RHB","None","IND",7),
        _p("csk_02","Ruturaj Gaikwad","BATTER","RHB","None","IND",31),
        _p("csk_03","Shivam Dube","ALL_ROUNDER","LHB","RMS","IND",25),
        _p("csk_04","Ravindra Jadeja","ALL_ROUNDER","LHB","SLA","IND",8),
        _p("csk_05","Deepak Chahar","BOWLER","RHB","RFM","IND",90),
        _p("csk_06","Moeen Ali","ALL_ROUNDER","LHB","OB","ENG",18),
        _p("csk_07","Matheesha Pathirana","BOWLER","RHB","RF","SL",40),
        _p("csk_08","Rachin Ravindra","ALL_ROUNDER","LHB","SLA","NZL",54),
        _p("csk_09","Devon Conway","WK_BATTER","LHB","None","NZL",22),
        _p("csk_10","Tushar Deshpande","BOWLER","RHB","RFM","IND",77),
        _p("csk_11","Mitchell Santner","ALL_ROUNDER","LHB","SLA","NZL",16),
    ]),
    "RCB": TeamRoster(team_id="RCB", team_name="Royal Challengers Bengaluru", short_name="RCB",
        league="IPL", home_ground="M.Chinnaswamy Stadium, Bengaluru", players=[
        _p("rcb_01","Virat Kohli","BATTER","RHB","None","IND",18),
        _p("rcb_02","Faf du Plessis","BATTER","RHB","None","RSA",13),
        _p("rcb_03","Glenn Maxwell","ALL_ROUNDER","RHB","OB","AUS",32),
        _p("rcb_04","Mohammad Siraj","BOWLER","RHB","RFM","IND",77),
        _p("rcb_05","Cameron Green","ALL_ROUNDER","RHB","RFM","AUS",23),
        _p("rcb_06","Dinesh Karthik","WK_BATTER","RHB","None","IND",5),
        _p("rcb_07","Reece Topley","BOWLER","LHB","LFM","ENG",30),
        _p("rcb_08","Mahipal Lomror","ALL_ROUNDER","LHB","SLA","IND",88),
        _p("rcb_09","Alzarri Joseph","BOWLER","RHB","RF","WI",45),
        _p("rcb_10","Yash Dayal","BOWLER","LHB","LFM","IND",71),
        _p("rcb_11","Rajat Patidar","BATTER","RHB","None","IND",10),
    ]),
    "KKR": TeamRoster(team_id="KKR", team_name="Kolkata Knight Riders", short_name="KKR",
        league="IPL", home_ground="Eden Gardens, Kolkata", players=[
        _p("kkr_01","Shreyas Iyer","BATTER","RHB","None","IND",41),
        _p("kkr_02","Venkatesh Iyer","ALL_ROUNDER","LHB","RMS","IND",19),
        _p("kkr_03","Phil Salt","WK_BATTER","RHB","None","ENG",28),
        _p("kkr_04","Andre Russell","ALL_ROUNDER","RHB","RF","WI",12),
        _p("kkr_05","Sunil Narine","ALL_ROUNDER","LHB","OB","TT",74),
        _p("kkr_06","Mitchell Starc","BOWLER","LHB","LF","AUS",56),
        _p("kkr_07","Harshit Rana","BOWLER","RHB","RFM","IND",99),
        _p("kkr_08","Varun Chakravarthy","BOWLER","RHB","LB","IND",29),
        _p("kkr_09","Rinku Singh","BATTER","LHB","None","IND",17),
        _p("kkr_10","Angkrish Raghuvanshi","BATTER","RHB","None","IND",53),
        _p("kkr_11","Ramandeep Singh","ALL_ROUNDER","RHB","RMS","IND",11),
    ]),
    "GT": TeamRoster(team_id="GT", team_name="Gujarat Titans", short_name="GT",
        league="IPL", home_ground="Narendra Modi Stadium, Ahmedabad", players=[
        _p("gt_01","Shubman Gill","BATTER","RHB","None","IND",77),
        _p("gt_02","Wriddhiman Saha","WK_BATTER","RHB","None","IND",9),
        _p("gt_03","Mohammed Shami","BOWLER","RHB","RFM","IND",11),
        _p("gt_04","Rashid Khan","BOWLER","RHB","LB","AFG",19),
        _p("gt_05","David Miller","BATTER","LHB","None","RSA",10),
        _p("gt_06","Rahul Tewatia","ALL_ROUNDER","LHB","LB","IND",55),
        _p("gt_07","Vijay Shankar","ALL_ROUNDER","RHB","RFM","IND",13),
        _p("gt_08","Darshan Nalkande","BOWLER","RHB","RFM","IND",24),
        _p("gt_09","Noor Ahmad","BOWLER","LHB","SLA","AFG",31),
        _p("gt_10","Azmatullah Omarzai","ALL_ROUNDER","RHB","RFM","AFG",18),
        _p("gt_11","Sai Sudharsan","BATTER","LHB","None","IND",36),
    ]),
    "SRH": TeamRoster(team_id="SRH", team_name="Sunrisers Hyderabad", short_name="SRH",
        league="IPL", home_ground="Rajiv Gandhi International Stadium, Hyderabad", players=[
        _p("srh_01","Pat Cummins","ALL_ROUNDER","RHB","RF","AUS",30),
        _p("srh_02","Travis Head","BATTER","LHB","OB","AUS",62),
        _p("srh_03","Heinrich Klaasen","WK_BATTER","RHB","None","RSA",17),
        _p("srh_04","Abhishek Sharma","ALL_ROUNDER","LHB","SLA","IND",28),
        _p("srh_05","Nitish Kumar Reddy","ALL_ROUNDER","RHB","RFM","IND",10),
        _p("srh_06","Bhuvneshwar Kumar","BOWLER","RHB","RMS","IND",15),
        _p("srh_07","T Natarajan","BOWLER","LHB","LFM","IND",75),
        _p("srh_08","Adam Zampa","BOWLER","RHB","LB","AUS",33),
        _p("srh_09","Marco Jansen","BOWLER","LHB","LF","RSA",28),
        _p("srh_10","Shahbaz Ahmed","ALL_ROUNDER","LHB","SLA","IND",44),
        _p("srh_11","Jaydev Unadkat","BOWLER","LHB","LFM","IND",11),
    ]),
    "LSG": TeamRoster(team_id="LSG", team_name="Lucknow Super Giants", short_name="LSG",
        league="IPL", home_ground="BRSABV Ekana Cricket Stadium, Lucknow", players=[
        _p("lsg_01","KL Rahul","WK_BATTER","RHB","None","IND",1),
        _p("lsg_02","Quinton de Kock","WK_BATTER","LHB","None","RSA",23),
        _p("lsg_03","Marcus Stoinis","ALL_ROUNDER","RHB","RFM","AUS",20),
        _p("lsg_04","Nicholas Pooran","WK_BATTER","LHB","None","WI",33),
        _p("lsg_05","Deepak Hooda","ALL_ROUNDER","RHB","OB","IND",19),
        _p("lsg_06","Krunal Pandya","ALL_ROUNDER","LHB","SLA","IND",14),
        _p("lsg_07","Avesh Khan","BOWLER","RHB","RFM","IND",31),
        _p("lsg_08","Ravi Bishnoi","BOWLER","RHB","LB","IND",43),
        _p("lsg_09","Mark Wood","BOWLER","RHB","RF","ENG",55),
        _p("lsg_10","Mohsin Khan","BOWLER","LHB","LFM","IND",18),
        _p("lsg_11","Ayush Badoni","BATTER","RHB","None","IND",27),
    ]),
    "PBKS": TeamRoster(team_id="PBKS", team_name="Punjab Kings", short_name="PBKS",
        league="IPL", home_ground="Punjab Cricket Association IS Bindra Stadium, Mohali", players=[
        _p("pbks_01","Shikhar Dhawan","BATTER","LHB","None","IND",25),
        _p("pbks_02","Jonny Bairstow","WK_BATTER","RHB","None","ENG",51),
        _p("pbks_03","Liam Livingstone","ALL_ROUNDER","RHB","LB","ENG",23),
        _p("pbks_04","Sam Curran","ALL_ROUNDER","LHB","LFM","ENG",58),
        _p("pbks_05","Kagiso Rabada","BOWLER","RHB","RF","RSA",25),
        _p("pbks_06","Prabhsimran Singh","WK_BATTER","RHB","None","IND",15),
        _p("pbks_07","Arshdeep Singh","BOWLER","LHB","LFM","IND",2),
        _p("pbks_08","Nathan Ellis","BOWLER","RHB","RFM","AUS",37),
        _p("pbks_09","Rahul Chahar","BOWLER","RHB","LB","IND",19),
        _p("pbks_10","Rishi Dhawan","ALL_ROUNDER","RHB","RFM","IND",22),
        _p("pbks_11","Harpreet Brar","ALL_ROUNDER","LHB","SLA","IND",29),
    ]),
    "RR": TeamRoster(team_id="RR", team_name="Rajasthan Royals", short_name="RR",
        league="IPL", home_ground="Sawai Mansingh Stadium, Jaipur", players=[
        _p("rr_01","Sanju Samson","WK_BATTER","RHB","None","IND",9),
        _p("rr_02","Jos Buttler","WK_BATTER","RHB","None","ENG",63),
        _p("rr_03","Yashasvi Jaiswal","BATTER","LHB","None","IND",12),
        _p("rr_04","Trent Boult","BOWLER","LHB","LFM","NZL",22),
        _p("rr_05","Shimron Hetmyer","BATTER","LHB","None","GUY",44),
        _p("rr_06","R Ashwin","ALL_ROUNDER","RHB","OB","IND",99),
        _p("rr_07","Yuzvendra Chahal","BOWLER","RHB","LB","IND",3),
        _p("rr_08","Riyan Parag","ALL_ROUNDER","RHB","LB","IND",10),
        _p("rr_09","Nandre Burger","BOWLER","LHB","LFM","RSA",16),
        _p("rr_10","Dhruv Jurel","WK_BATTER","RHB","None","IND",21),
        _p("rr_11","Sandeep Sharma","BOWLER","RHB","RFM","IND",7),
    ]),
    "DC": TeamRoster(team_id="DC", team_name="Delhi Capitals", short_name="DC",
        league="IPL", home_ground="Arun Jaitley Stadium, Delhi", players=[
        _p("dc_01","David Warner","BATTER","LHB","None","AUS",31),
        _p("dc_02","Prithvi Shaw","BATTER","RHB","None","IND",100),
        _p("dc_03","Rishabh Pant","WK_BATTER","LHB","None","IND",17),
        _p("dc_04","Axar Patel","ALL_ROUNDER","LHB","SLA","IND",20),
        _p("dc_05","Anrich Nortje","BOWLER","RHB","RF","RSA",32),
        _p("dc_06","Mitchell Marsh","ALL_ROUNDER","RHB","RFM","AUS",8),
        _p("dc_07","Lungi Ngidi","BOWLER","RHB","RF","RSA",11),
        _p("dc_08","Kuldeep Yadav","BOWLER","LHB","SLA","IND",24),
        _p("dc_09","Yash Dhull","BATTER","RHB","None","IND",40),
        _p("dc_10","Lalit Yadav","ALL_ROUNDER","RHB","OB","IND",45),
        _p("dc_11","Ishant Sharma","BOWLER","RHB","RF","IND",29),
    ]),
}

INDIA_T20I = TeamRoster(team_id="IND", team_name="India", short_name="IND",
    league="T20I/ODI/TEST", home_ground="Various", players=[
    _p("ind_01","Rohit Sharma","BATTER","RHB","None","IND",45),
    _p("ind_02","Virat Kohli","BATTER","RHB","None","IND",18),
    _p("ind_03","Suryakumar Yadav","BATTER","RHB","None","IND",63),
    _p("ind_04","KL Rahul","WK_BATTER","RHB","None","IND",1),
    _p("ind_05","Hardik Pandya","ALL_ROUNDER","RHB","RFM","IND",228),
    _p("ind_06","Ravindra Jadeja","ALL_ROUNDER","LHB","SLA","IND",8),
    _p("ind_07","R Ashwin","ALL_ROUNDER","RHB","OB","IND",99),
    _p("ind_08","Jasprit Bumrah","BOWLER","RHB","RF","IND",93),
    _p("ind_09","Mohammed Shami","BOWLER","RHB","RFM","IND",11),
    _p("ind_10","Arshdeep Singh","BOWLER","LHB","LFM","IND",2),
    _p("ind_11","Kuldeep Yadav","BOWLER","LHB","SLA","IND",24),
])

ALL_IPL_TEAMS = list(IPL_TEAMS.keys())


def get_team(team_id: str) -> TeamRoster:
    team_id = team_id.upper()
    if team_id in IPL_TEAMS:
        return IPL_TEAMS[team_id]
    if team_id in ("IND", "INDIA"):
        return INDIA_T20I
    raise KeyError(f"Team '{team_id}' not found in league database.")


def list_all_teams() -> List[str]:
    return ALL_IPL_TEAMS + ["IND"]
