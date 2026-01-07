import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from datetime import timedelta
import numpy as np
import plotly.graph_objects as go


try:
    print("Fetching the data...")
    df = pd.read_csv("data/cleaned_atp.csv")
except FileNotFoundError:
    print("Error: data source not found. Please ensure the file path you provided is correct.")
    df = pd.DataFrame(columns=[
        'Date', 'Player_1', 'Player_2', 'Winner', 'Odd_1', 'Odd_2', 'Surface',
        'Series', 'Court', 'Round', 'Total_sets_needed', 'Score',
        'Break_pts_1', 'Break_pts_2', 'Tournament'
    ])

df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year

for col in ['Odd_1', 'Odd_2']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

valid_odds_1 = df[df['Odd_1'] > 0]['Odd_1']
valid_odds_2 = df[df['Odd_2'] > 0]['Odd_2']

if not valid_odds_1.empty and not valid_odds_2.empty:
    mean_1, std_1 = valid_odds_1.mean(), valid_odds_1.std()
    mean_2, std_2 = valid_odds_2.mean(), valid_odds_2.std()
    
    def generate_random_odd(value, mean, std):
        if value <= 0 or pd.isna(value):
            new_val = np.random.normal(mean, std)
            return max(1.01, round(new_val, 2))
        return value

    df['Odd_1'] = df['Odd_1'].apply(lambda x: generate_random_odd(x, mean_1, std_1))
    df['Odd_2'] = df['Odd_2'].apply(lambda x: generate_random_odd(x, mean_2, std_2))
else:
    df['Odd_1'] = df['Odd_1'].apply(lambda x: np.random.uniform(1.1, 3.5) if x <= 0 else x)
    df['Odd_2'] = df['Odd_2'].apply(lambda x: np.random.uniform(1.1, 3.5) if x <= 0 else x)

df_odds = df.dropna(subset=['Odd_1', 'Odd_2']).copy()
df_odds = df_odds[(df_odds['Odd_1'] > 1.0) & (df_odds['Odd_2'] > 1.0)]

def get_winner_odd(row):
    if row['Winner'] == row['Player_1']:
        return row['Odd_1']
    elif row['Winner'] == row['Player_2']:
        return row['Odd_2']
    return np.nan

df_odds['Winner_Odd'] = df_odds.apply(get_winner_odd, axis=1)
df_odds.dropna(subset=['Winner_Odd'], inplace=True)
df_odds['Bet_Type'] = df_odds['Winner_Odd'].apply(lambda x: 'Underdog (Odds > 2.0)' if x > 2.0 else 'Favorite (Odds <= 2.0)')

all_players_series = pd.concat([df['Player_1'], df['Player_2']])
all_players = all_players_series.dropna().astype(str).str.strip().unique()
all_players.sort()
player_options = [{'label': player, 'value': player} for player in all_players]

all_years = sorted(df['Year'].unique())
year_options = [{'label': str(year), 'value': year} for year in all_years]

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CERULEAN, 
        "https://fonts.googleapis.com/css2?family=Carter+One&family=Sonsie+One&family=Orbitron:wght@400;700;900&display=swap"
    ],
    suppress_callback_exceptions=True
)

server = app.server 

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Carter+One&family=Sonsie+One&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            /* Custom styling for dropdowns */
            .Select-control {
                border: 2px solid rgba(0, 255, 242, 0.3) !important;
                border-radius: 12px !important;
                background: rgba(15, 23, 42, 0.6) !important;
                box-shadow: 0 4px 15px rgba(0, 255, 242, 0.2) !important;
                transition: all 0.3s ease !important;
            }
            .Select-control:hover {
                border-color: #00fff2 !important;
                box-shadow: 0 0 20px rgba(0, 255, 242, 0.4) !important;
                background: rgba(15, 23, 42, 0.8) !important;
            }
            .Select--is-focused .Select-control {
                border-color: #00fff2 !important;
                box-shadow: 0 0 25px rgba(0, 255, 242, 0.5) !important;
                background: rgba(15, 23, 42, 0.9) !important;
            }
            .Select-placeholder {
                color: rgba(0, 255, 242, 0.6) !important;
            }
            .Select-input input {
                color: #00fff2 !important;
            }
            .Select-value-label {
                color: #00fff2 !important;
            }
            .Select-menu-outer {
                border-radius: 12px !important;
                box-shadow: 0 10px 40px rgba(0, 255, 242, 0.3) !important;
                border: 2px solid rgba(0, 255, 242, 0.4) !important;
                background: rgba(15, 23, 42, 0.95) !important;
                backdrop-filter: blur(10px) !important;
            }
            .Select-option {
                padding: 12px 16px !important;
                transition: all 0.2s ease !important;
                color: #E0E0E0 !important; 
                background: transparent !important;
            }
            .Select-option:hover {
                background: rgba(0, 255, 242, 0.2) !important;
                color: #00fff2 !important;
            }
            .Select-option.is-selected {
                background: rgba(0, 255, 242, 0.3) !important;
                color: #00fff2 !important;
            }
            
            /* Stílusos Dátum BEMENET */
            .DateRangePickerInput {
                border: 2px solid rgba(0, 255, 242, 0.3) !important;
                border-radius: 12px !important;
                box-shadow: 0 4px 15px rgba(0, 255, 242, 0.2) !important;
                padding: 8px 16px !important;
                background: rgba(15, 23, 42, 0.6) !important;
                transition: all 0.3s ease !important;
                display: flex !important;
                align-items: center !important;
                justify-content: space-around !important;
            }
            .DateRangePickerInput:hover {
                box-shadow: 0 0 20px rgba(0, 255, 242, 0.4) !important;
                border-color: #00fff2 !important;
                background: rgba(15, 23, 42, 0.8) !important;
            }
            .DateInput {
                background: transparent !important;
                border-radius: 8px !important;
                margin: 4px !important;
                border: 1px solid rgba(0, 255, 242, 0.2) !important;
            }
            .DateInput_input {
                color: #00fff2 !important;
                font-weight: 600 !important;
                font-size: 14px !important;
                padding: 12px 16px !important;
                border: none !important;
                background: transparent !important;
            }
            .DateInput_input::placeholder {
                color: rgba(0, 255, 242, 0.5) !important;
            }
            .DateRangePickerInput_arrow {
                color: #00fff2 !important;
                font-weight: bold !important;
                font-size: 20px !important;
            }

            .Select-value {
                background: rgba(0, 255, 242, 0.2) !important;
                color: #00fff2 !important;
                border: 1px solid rgba(0, 255, 242, 0.4) !important;
                border-radius: 8px !important;
                padding: 6px 12px !important;
                margin: 2px !important;
                font-weight: 500 !important;
                box-shadow: 0 2px 8px rgba(0, 255, 242, 0.2) !important;
            }
            .Select-value-icon {
                color: #00fff2 !important;
                border-radius: 50% !important;
                padding: 2px !important;
            }
            .Select-value-icon:hover {
                background: rgba(0, 255, 242, 0.3) !important;
                color: #ffffff !important;
            }
            .Select-control .Select-value-wrapper .Select-value {
                background: rgba(0, 255, 242, 0.15) !important;
                border: 1px solid rgba(0, 255, 242, 0.3) !important;
                box-shadow: 0 2px 8px rgba(0, 255, 242, 0.15) !important;
                color: #00fff2 !important;
            }
            
            /* Futuristic Header Animation */
            @keyframes glow {
                0%, 100% { text-shadow: 0 0 10px #00fff2, 0 0 20px #00fff2, 0 0 30px #00fff2; }
                50% { text-shadow: 0 0 20px #00fff2, 0 0 30px #00fff2, 0 0 40px #00fff2; }
            }
            
            @keyframes slideIn {
                from { transform: translateX(-50px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 0.6; }
                50% { opacity: 1; }
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
            }
            
            .source-icon {
                transition: all 0.3s ease;
            }
            
            .source-icon:hover {
                transform: scale(1.15) rotate(5deg);
                filter: brightness(1.2);
            }
            
            /* Section Title Styling */
            .cyber-title {
                position: relative;
                display: inline-block;
                padding: 0 20px;
            }
            
            .cyber-title::before,
            .cyber-title::after {
                content: '';
                position: absolute;
                height: 2px;
                background: linear-gradient(90deg, transparent, #00fff2, transparent);
                width: 100%;
                animation: pulse 2s ease-in-out infinite;
            }
            
            .cyber-title::before {
                top: 0;
                left: 0;
            }
            
            .cyber-title::after {
                bottom: 0;
                left: 0;
            }

            /* Dátumválasztó felugró ablak elrejtése */
            .DateRangePicker_picker {
                display: none !important;
            }

        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div(
    style={
        'background': 'linear-gradient(135deg, #0a0e27 0%, #1a1a2e 50%, #16213e 100%)',
        'minHeight': '100vh',
        'position': 'relative',
        'overflow': 'hidden'
    },
    children=[
    html.Div(
        style={
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'right': '0',
            'bottom': '0',
            'background': 'radial-gradient(circle at 20% 50%, rgba(0, 255, 242, 0.05) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(102, 126, 234, 0.05) 0%, transparent 50%)',
            'zIndex': '0',
            'pointerEvents': 'none'
        }
    ),
    
    html.Header(
        style={
            'background': 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
            'padding': '25px 40px',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'boxShadow': '0 10px 40px rgba(0, 255, 242, 0.3), 0 0 80px rgba(48, 43, 99, 0.5)',
            'borderBottom': '3px solid #00fff2',
            'position': 'relative',
            'overflow': 'hidden',
            'zIndex': '10'
        },
        children=[
            html.Div(
                style={
                    'position': 'absolute',
                    'top': '0',
                    'left': '0',
                    'right': '0',
                    'bottom': '0',
                    'background': 'linear-gradient(90deg, transparent, rgba(0, 255, 242, 0.1), transparent)',
                    'animation': 'slideIn 3s infinite alternate',
                    'zIndex': '0'
                }
            ),
            
            html.Div(
                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'gap': '25px',
                    'zIndex': '1'
                },
                children=[
                    html.Img(
                        src="assets/atp_logo.png",
                        style={
                            'height': '60px',
                            'width': 'auto',
                            'filter': 'drop-shadow(0 0 15px rgba(0, 255, 242, 0.6))',
                            'animation': 'slideIn 1s ease-out'
                        }
                    ),
                    
                    html.H1(
                        "PROFESSIONAL MEN TENNIS ANALYTICS",
                        style={
                            'color': '#00fff2',
                            'margin': '0',
                            'fontSize': '38px',
                            'fontWeight': '900',
                            'fontFamily': '"Orbitron", sans-serif',
                            'letterSpacing': '4px',
                            'textTransform': 'uppercase',
                            'animation': 'slideIn 1.2s ease-out',
                            'background': 'linear-gradient(90deg, #00fff2, #00d4ff, #00fff2)',
                            'backgroundClip': 'text',
                            'WebkitBackgroundClip': 'text',
                            'WebkitTextFillColor': 'transparent',
                            'lineHeight': '1.2'
                        }
                    ),
                ]
            ),
            
            html.A(
                href="https://www.kaggle.com/datasets/dissfya/atp-tennis-2000-2023daily-pull",
                target="_blank",
                className="source-icon",
                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'gap': '12px',
                    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'padding': '12px 24px',
                    'borderRadius': '50px',
                    'textDecoration': 'none',
                    'boxShadow': '0 8px 20px rgba(102, 126, 234, 0.4)',
                    'border': '2px solid #00fff2',
                    'zIndex': '1'
                },
                children=[
                    html.Span(
                        "📊",
                        style={'fontSize': '24px'}
                    ),
                    html.Span(
                        "DATA SOURCE",
                        style={
                            'color': 'white',
                            'fontFamily': '"Orbitron", sans-serif',
                            'fontWeight': 'bold',
                            'fontSize': '14px',
                            'letterSpacing': '2px'
                        }
                    )
                ]
            )
        ]
    ),

    html.Div(
        style={
            'maxWidth': '1600px',
            'margin': '0 auto',
            'padding': '60px 40px 80px 40px',
            'position': 'relative',
            'zIndex': '1'
        },
        children=[
            
            html.Div(
                style={
                    'background': 'rgba(15, 23, 42, 0.7)',
                    'backdropFilter': 'blur(10px)',
                    'borderRadius': '24px',
                    'padding': '40px',
                    'boxShadow': '0 0 40px rgba(0, 255, 242, 0.15), inset 0 0 60px rgba(0, 255, 242, 0.03)',
                    'border': '2px solid rgba(0, 255, 242, 0.2)',
                    'marginBottom': '60px',
                    'position': 'relative',
                    'overflow': 'hidden'
                },
                children=[
                    html.Div(
                        className="cyber-title",
                        style={
                            'textAlign': 'center',
                            'marginBottom': '40px',
                            'position': 'relative',
                            'zIndex': '1'
                        },
                        children=[
                            html.H2(
                                "Overall Tournament Wins Breakdown 🧠",
                                style={
                                    'fontSize': '28px',
                                    'fontWeight': '900',
                                    'color': '#00fff2',
                                    'fontFamily': '"Orbitron", sans-serif',
                                    'letterSpacing': '3px',
                                    'textTransform': 'uppercase',
                                    'textShadow': '0 0 20px rgba(0, 255, 242, 0.5)',
                                    'margin': '0'
                                }
                            )
                        ]
                    ),
                    html.Div(
                        style={
                            'background': 'rgba(0, 255, 242, 0.05)',
                            'borderRadius': '20px',
                            'padding': '30px',
                            'boxShadow': 'inset 0 0 30px rgba(0, 255, 242, 0.1)',
                            'border': '1px solid rgba(0, 255, 242, 0.2)',
                            'position': 'relative',
                            'zIndex': '1',
                            'marginBottom': '40px' 
                        },
                        children=[
                            html.Div(
                                style={
                                    'display': 'grid',
                                    'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))', 
                                    'gap': '20px'
                                },
                                children=[
                                    html.Div([
                                        html.Label(
                                            "🎾 SURFACE",
                                            style={
                                                'fontWeight': '700',
                                                'fontSize': '13px',
                                                'color': '#00fff2',
                                                'marginBottom': '12px',
                                                'display': 'block',
                                                'fontFamily': '"Orbitron", sans-serif',
                                                'letterSpacing': '2px',
                                                'textShadow': '0 0 10px rgba(0, 255, 242, 0.5)'
                                            }
                                        ),
                                        dcc.Dropdown(
                                            id='surface-slicer',
                                            options=[{'label': f"🏟️ {i}", 'value': i} for i in df['Surface'].unique()],
                                            value=df['Surface'].unique().tolist(),
                                            multi=True,
                                            placeholder="Choose surfaces...",
                                            style={'fontSize': '14px', 'fontWeight': '500'}
                                        ),
                                    ]),
                                    html.Div([
                                        html.Label(
                                            "🏆 SERIES",
                                            style={
                                                'fontWeight': '700',
                                                'fontSize': '13px',
                                                'color': '#00fff2',
                                                'marginBottom': '12px',
                                                'display': 'block',
                                                'fontFamily': '"Orbitron", sans-serif',
                                                'letterSpacing': '2px',
                                                'textShadow': '0 0 10px rgba(0, 255, 242, 0.5)'
                                            }
                                        ),
                                        dcc.Dropdown(
                                            id='series-slicer',
                                            options=[{'label': f"🎪 {i}", 'value': i} for i in df['Series'].unique()],
                                            value=['International'],
                                            multi=True,
                                            placeholder="Choose series...",
                                            style={'fontSize': '14px', 'fontWeight': '500'}
                                        ),
                                    ]),
                                    html.Div([
                                        html.Label(
                                            "🏟️ COURT",
                                            style={
                                                'fontWeight': '700',
                                                'fontSize': '13px',
                                                'color': '#00fff2',
                                                'marginBottom': '12px',
                                                'display': 'block',
                                                'fontFamily': '"Orbitron", sans-serif',
                                                'letterSpacing': '2px',
                                                'textShadow': '0 0 10px rgba(0, 255, 242, 0.5)'
                                            }
                                        ),
                                        dcc.Dropdown(
                                            id='court-slicer',
                                            options=[{'label': f"📍 {i}", 'value': i} for i in df['Court'].unique()],
                                            value=df['Court'].unique().tolist(),
                                            multi=True,
                                            placeholder="Choose court types...",
                                            style={'fontSize': '14px', 'fontWeight': '500'}
                                        ),
                                    ]),
                                    html.Div([
                                        html.Label(
                                            "📅 DATE RANGE",
                                            style={
                                                'fontWeight': '700',
                                                'fontSize': '13px',
                                                'color': '#00fff2',
                                                'marginBottom': '12px',
                                                'display': 'block',
                                                'fontFamily': '"Orbitron", sans-serif',
                                                'letterSpacing': '2px',
                                                'textShadow': '0 0 10px rgba(0, 255, 242, 0.5)'
                                            }
                                        ),
                                        dcc.DatePickerRange(
                                            id='date-range-slicer',
                                            min_date_allowed=df['Date'].min(),
                                            max_date_allowed=df['Date'].max(),
                                            start_date=df['Date'].min(),
                                            end_date=df['Date'].max(),
                                            display_format='DD/MM/YYYY',
                                            start_date_placeholder_text="Start",
                                            end_date_placeholder_text="End",
                                            style={'width': '100%'}
                                        )
                                    ]),
                                ]
                            ),
                        ]
                    ),
                    
                    html.Div(
                        style={
                            'display': 'grid',
                            'gridTemplateColumns': '2fr 1fr', 
                            'gap': '40px',
                        },
                        children=[
                            html.Div(
                                style={
                                    'background': 'rgba(0, 255, 242, 0.03)',
                                    'borderRadius': '16px',
                                    'padding': '25px',
                                    'border': '1px solid rgba(0, 255, 242, 0.15)',
                                    'position': 'relative'
                                },
                                children=[
                                    html.Div(
                                        className="cyber-title",
                                        style={
                                            'textAlign': 'center',
                                            'marginBottom': '40px',
                                            'position': 'relative',
                                            'zIndex': '1'
                                        },
                                        children=[
                                            html.H2(
                                                "Series Kings 👑",
                                                style={
                                                    'fontSize': '28px',
                                                    'fontWeight': '900',
                                                    'color': '#00fff2',
                                                    'fontFamily': '"Orbitron", sans-serif',
                                                    'letterSpacing': '3px',
                                                    'textTransform': 'uppercase',
                                                    'textShadow': '0 0 20px rgba(0, 255, 242, 0.5)',
                                                    'margin': '0'
                                                }
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        style={'position': 'relative', 'zIndex': '1'},
                                        children=[dcc.Graph(id='wins-treemap')] 
                                    )
                                ]
                            ),
                            
                            html.Div(
                                style={
                                    'background': 'rgba(0, 255, 242, 0.03)',
                                    'borderRadius': '16px',
                                    'padding': '25px',
                                    'border': '1px solid rgba(0, 255, 242, 0.15)',
                                    'position': 'relative'
                                },
                                children=[
                                    html.Div(
                                        className="cyber-title",
                                        style={
                                            'textAlign': 'center',
                                            'marginBottom': '40px',
                                            'position': 'relative',
                                            'zIndex': '1'
                                        },
                                        children=[
                                            html.H2(
                                                "PATH TO VICTORY 🏆",
                                                style={
                                                    'fontSize': '24px',
                                                    'fontWeight': '900',
                                                    'color': '#00fff2',
                                                    'fontFamily': '"Orbitron", sans-serif',
                                                    'letterSpacing': '3px',
                                                    'textTransform': 'uppercase',
                                                    'textShadow': '0 0 20px rgba(0, 255, 242, 0.5)',
                                                    'margin': '0'
                                                }
                                            )
                                        ]
                                    ),
                                    html.Div(
                                        style={'position': 'relative', 'zIndex': '1'},
                                        children=[dcc.Graph(id='sunburst-chart')]
                                    )
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            
            html.Div(
                style={
                    'background': 'rgba(15, 23, 42, 0.7)',
                    'backdropFilter': 'blur(10px)',
                    'borderRadius': '24px',
                    'padding': '40px',
                    'boxShadow': '0 0 40px rgba(0, 255, 242, 0.15), inset 0 0 60px rgba(0, 255, 242, 0.03)',
                    'border': '2px solid rgba(0, 255, 242, 0.2)',
                    'marginBottom': '60px',
                    'position': 'relative',
                    'overflow': 'hidden'
                },
                children=[
                    html.Div(
                        className="cyber-title",
                        style={
                            'textAlign': 'center',
                            'marginBottom': '40px'
                        },
                        children=[
                            html.H2(
                                "QUALITY GAP: FAVORITES VS UNDERDOGS ⚖️",
                                style={
                                    'fontSize': '28px',
                                    'fontWeight': '900',
                                    'color': '#00fff2',
                                    'fontFamily': '"Orbitron", sans-serif',
                                    'letterSpacing': '3px',
                                    'textTransform': 'uppercase',
                                    'textShadow': '0 0 20px rgba(0, 255, 242, 0.5)',
                                    'margin': '0'
                                }
                            )
                        ]
                    ),
                    
                    html.Div(
                        style={
                            'background': 'rgba(0, 255, 242, 0.05)',
                            'borderRadius': '20px',
                            'padding': '30px',
                            'marginBottom': '35px',
                            'boxShadow': 'inset 0 0 30px rgba(0, 255, 242, 0.1)',
                            'border': '1px solid rgba(0, 255, 242, 0.2)'
                        },
                        children=[
                            html.Div(
                                style={
                                    'display': 'grid',
                                    'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
                                    'gap': '20px'
                                },
                                children=[
                                    html.Div([
                                        html.Label(
                                            "📊 VISUALIZATION CATEGORY",
                                            style={
                                                'fontWeight': '700',
                                                'fontSize': '13px',
                                                'color': '#00fff2',
                                                'marginBottom': '12px',
                                                'display': 'block',
                                                'fontFamily': '"Orbitron", sans-serif',
                                                'letterSpacing': '2px',
                                                'textShadow': '0 0 10px rgba(0, 255, 242, 0.5)'
                                            }
                                        ),
                                        dcc.Dropdown(
                                            id='category-selector',
                                            options=[
                                                {'label': '🏟️ Surface', 'value': 'Surface'},
                                                {'label': '🏆 Series', 'value': 'Series'}
                                            ],
                                            value='Series',
                                            clearable=False,
                                            placeholder="Choose category...",
                                            style={'fontSize': '14px', 'fontWeight': '500'}
                                        ),
                                    ]),
                                ]
                            )
                        ]
                    ),
                    
                    dcc.Graph(id='odds-box-plot')
                ]
            ),

            html.Div(
                style={
                    'background': 'rgba(15, 23, 42, 0.7)',
                    'backdropFilter': 'blur(10px)',
                    'borderRadius': '24px',
                    'padding': '40px',
                    'boxShadow': '0 0 40px rgba(0, 255, 242, 0.15), inset 0 0 60px rgba(0, 255, 242, 0.03)',
                    'border': '2px solid rgba(0, 255, 242, 0.2)',
                    'marginBottom': '60px',
                    'position': 'relative',
                    'overflow': 'hidden'
                },
                children=[
                    html.Div(
                        className="cyber-title",
                        style={
                            'textAlign': 'center',
                            'marginBottom': '40px'
                        },
                        children=[
                            html.H2(
                                "INDIVIDUAL PLAYER PERFORMANCE 👤",
                                style={
                                    'fontSize': '28px',
                                    'fontWeight': '900',
                                    'color': '#00fff2',
                                    'fontFamily': '"Orbitron", sans-serif',
                                    'letterSpacing': '3px',
                                    'textTransform': 'uppercase',
                                    'textShadow': '0 0 20px rgba(0, 255, 242, 0.5)',
                                    'margin': '0'
                                }
                            )
                        ]
                    ),
                    
                    html.Div(
                        style={
                            'background': 'rgba(0, 255, 242, 0.05)',
                            'borderRadius': '20px',
                            'padding': '30px',
                            'marginBottom': '35px',
                            'boxShadow': 'inset 0 0 30px rgba(0, 255, 242, 0.1)',
                            'border': '1px solid rgba(0, 255, 242, 0.2)'
                        },
                        children=[
                            html.Div(
                                style={
                                    'display': 'grid',
                                    'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
                                    'gap': '20px'
                                },
                                children=[
                                    html.Div([
                                        html.Label(
                                            "👨‍🎾 SELECT PLAYER",
                                            style={
                                                'fontWeight': '700',
                                                'fontSize': '13px',
                                                'color': '#00fff2',
                                                'marginBottom': '12px',
                                                'display': 'block',
                                                'fontFamily': '"Orbitron", sans-serif',
                                                'letterSpacing': '2px',
                                                'textShadow': '0 0 10px rgba(0, 255, 242, 0.5)'
                                            }
                                        ),
                                        dcc.Dropdown(
                                            id='player-slicer',
                                            options=player_options,
                                            value='Nadal R.',
                                            placeholder="Choose a player...",
                                            style={'fontSize': '14px', 'fontWeight': '500'}
                                        ),
                                    ]),
                                    html.Div([
                                        html.Label(
                                            "📆 SELECT YEAR",
                                            style={
                                                'fontWeight': '700',
                                                'fontSize': '13px',
                                                'color': '#00fff2',
                                                'marginBottom': '12px',
                                                'display': 'block',
                                                'fontFamily': '"Orbitron", sans-serif',
                                                'letterSpacing': '2px',
                                                'textShadow': '0 0 10px rgba(0, 255, 242, 0.5)'
                                            }
                                        ),
                                        dcc.Dropdown(
                                            id='year-slicer',
                                            options=year_options,
                                            value=2015,
                                            placeholder="Choose a year...",
                                            style={'fontSize': '14px', 'fontWeight': '500'}
                                        ),
                                    ]),
                                ]
                            )
                        ]
                    ),
                    
                    html.Div(id='player-kpi-row', style={'marginBottom': '40px'}),

                    html.Div(
                        style={
                            'display': 'grid',
                            'gridTemplateColumns': '2fr 1fr',
                            'gap': '30px'
                        },
                        children=[
                            html.Div(
                                style={
                                    'background': 'rgba(0, 255, 242, 0.03)',
                                    'borderRadius': '16px',
                                    'padding': '25px',
                                    'border': '1px solid rgba(0, 255, 242, 0.15)'
                                },
                                children=[dcc.Graph(id='timeline-chart')]
                            ),
                            html.Div(
                                style={
                                    'background': 'rgba(0, 255, 242, 0.03)',
                                    'borderRadius': '16px',
                                    'padding': '25px',
                                    'border': '1px solid rgba(0, 255, 242, 0.15)'
                                },
                                children=[dcc.Graph(id='radar-chart')]
                            ),
                        ]
                    ),
                ]
            ),

            html.Div(
                style={
                    'background': 'rgba(15, 23, 42, 0.7)',
                    'backdropFilter': 'blur(10px)',
                    'borderRadius': '24px',
                    'padding': '40px',
                    'boxShadow': '0 0 40px rgba(0, 255, 242, 0.15), inset 0 0 60px rgba(0, 255, 242, 0.03)',
                    'border': '2px solid rgba(0, 255, 242, 0.2)',
                    'position': 'relative',
                    'overflow': 'hidden'
                },
                children=[
                    html.Div(
                        className="cyber-title",
                        style={
                            'textAlign': 'center',
                            'marginBottom': '40px'
                        },
                        children=[
                            html.H2(
                                "HEAD-TO-HEAD COMPARISON ⚔️",
                                style={
                                    'fontSize': '28px',
                                    'fontWeight': '900',
                                    'color': '#00fff2',
                                    'fontFamily': '"Orbitron", sans-serif',
                                    'letterSpacing': '3px',
                                    'textTransform': 'uppercase',
                                    'textShadow': '0 0 20px rgba(0, 255, 242, 0.5)',
                                    'margin': '0'
                                }
                            )
                        ]
                    ),
                    
                    html.Div(
                        style={
                            'background': 'rgba(0, 255, 242, 0.05)',
                            'borderRadius': '20px',
                            'padding': '30px',
                            'marginBottom': '35px',
                            'boxShadow': 'inset 0 0 30px rgba(0, 255, 242, 0.1)',
                            'border': '1px solid rgba(0, 255, 242, 0.2)'
                        },
                        children=[
                            html.Div(
                                style={
                                    'display': 'grid',
                                    'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
                                    'gap': '20px'
                                },
                                children=[
                                    html.Div([
                                        html.Label(
                                            "🥇 PLAYER 1",
                                            style={
                                                'fontWeight': '700',
                                                'fontSize': '13px',
                                                'color': '#00fff2',
                                                'marginBottom': '12px',
                                                'display': 'block',
                                                'fontFamily': '"Orbitron", sans-serif',
                                                'letterSpacing': '2px',
                                                'textShadow': '0 0 10px rgba(0, 255, 242, 0.5)'
                                            }
                                        ),
                                        dcc.Dropdown(
                                            id='player1-slicer',
                                            options=player_options,
                                            value='Federer R.',
                                            placeholder="Choose first player...",
                                            style={'fontSize': '14px', 'fontWeight': '500'}
                                        ),
                                    ]),
                                    html.Div([
                                        html.Label(
                                            "🥈 PLAYER 2",
                                            style={
                                                'fontWeight': '700',
                                                'fontSize': '13px',
                                                'color': '#00fff2',
                                                'marginBottom': '12px',
                                                'display': 'block',
                                                'fontFamily': '"Orbitron", sans-serif',
                                                'letterSpacing': '2px',
                                                'textShadow': '0 0 10px rgba(0, 255, 242, 0.5)'
                                            }
                                        ),
                                        dcc.Dropdown(
                                            id='player2-slicer',
                                            options=player_options,
                                            value='Nadal R.',
                                            placeholder="Choose second player...",
                                            style={'fontSize': '14px', 'fontWeight': '500'}
                                        ),
                                    ]),
                                ]
                            )
                        ]
                    ),
                    
                    html.Div(id='1v1-results'),
                ]
            ),
        ]
    )
])

@app.callback(
    Output('wins-treemap', 'figure'),
    [Input('surface-slicer', 'value'),
     Input('series-slicer', 'value'),
     Input('court-slicer', 'value'),
     Input('date-range-slicer', 'start_date'),
     Input('date-range-slicer', 'end_date')]
)
def update_treemap(surfaces, series, courts, start_date, end_date):
    if not all([surfaces, series, courts, start_date, end_date]):
        return {}
    filtered_df = df[
        df['Surface'].isin(surfaces) &
        df['Series'].isin(series) &
        df['Court'].isin(courts) &
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date)
    ].copy()
    
    if filtered_df.empty:
        return {
            'layout': {
                'title': 'No Data Available for Selected Filters',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0.1)',
                'font': {'color': '#ffffff'}
            }
        }
        
    player_wins = filtered_df['Winner'].value_counts().reset_index()
    player_wins.columns = ['Winner', 'Wins']
    player_wins = player_wins.head(15).sort_values('Wins', ascending=True)
    
    fig = px.bar(
        player_wins,
        x='Wins',
        y='Winner',
        orientation='h', 
        text='Wins',     
        color='Wins',    
        color_continuous_scale='Tealgrn' 
    )

    fig.update_traces(
        texttemplate='%{text}', 
        textposition='outside',
        marker_line_color='rgba(0, 255, 242, 0.8)',
        marker_line_width=1,
        opacity=0.8
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', family='"Orbitron", sans-serif'),
        xaxis_title="Number of Wins",
        yaxis_title=None,
        xaxis=dict(
            showgrid=True, 
            gridcolor='rgba(0, 255, 242, 0.1)', 
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=11)
        ),
        coloraxis_showscale=False, 
        margin=dict(l=10, r=10, t=10, b=10)
    )

    return fig

@app.callback(
    Output('sunburst-chart', 'figure'),
    [Input('surface-slicer', 'value'),
     Input('series-slicer', 'value'),
     Input('court-slicer', 'value'),
     Input('date-range-slicer', 'start_date'),
     Input('date-range-slicer', 'end_date')]
)
def update_sunburst(surfaces, series, courts, start_date, end_date):
    if not all([surfaces, series, courts, start_date, end_date]):
        return {}
    filtered_df = df[
        df['Surface'].isin(surfaces) &
        df['Series'].isin(series) &
        df['Court'].isin(courts) &
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date)
    ].copy()

    if filtered_df.empty:
        return {
            'layout': {
                'title': 'No Data Available for Selected Filters',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0.1)',
                'font': {'color': '#ffffff'}
            }
        }

    fig = px.sunburst(
        filtered_df,
        path=['Surface', 'Round', 'Total_sets_needed']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff')
    )
    return fig

@app.callback(
    Output('odds-box-plot', 'figure'),
    Input('category-selector', 'value')
)
def update_odds_distribution_histogram(selected_category):
    if df_odds.empty:
        fig = go.Figure().update_layout(
            title="Data unavailable",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            font=dict(color='#ffffff')
        )
        return fig
    
    categories = df_odds[selected_category].unique()
    
    if selected_category == "Surface":
        color_map = {'Hard': '#3b82f6', 'Clay': '#ef4444', 'Grass': '#10b981', 'Carpet': '#f59e0b'}
    else:
        color_map = {
            'Grand Slam': '#4c1d95', 'Masters': '#f43f5e', 'ATP500': '#059669',
            'ATP250': '#6366f1', 'Masters 1000': '#f59e0b', 'International Gold': '#94a3b8',
            'International': '#f472b6', 'Masters Cup': '#c084fc'
        }

    fig = go.Figure()

    for cat in categories:
        df_group = df_odds[df_odds[selected_category] == cat]
        color = color_map.get(cat, '#e0e0e0')
        
        fig.add_trace(go.Histogram(
            x=df_group['Winner_Odd'],
            name=cat,
            xbins=dict(
                start=1.0,
                size=0.1
            ),
            marker_color=color,
            opacity=0.8, 
            marker=dict(
                line=dict(
                    width=1,
                    color='rgba(255, 255, 255, 0.5)'
                )
            ),
            hovertemplate=f'<b>{selected_category}:</b> {cat}<br><b>Odds Range:</b> %{{x}}<br><b>Count:</b> %{{y}}<extra></extra>'
        ))
    
    fig.update_layout(
        title={'text': f"Winner Odds Distribution by {selected_category}"},
        xaxis_title="Winner's Odd",
        yaxis_title="Frequency (Number of Wins)",
        font=dict(color='#ffffff'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        barmode='stack', 
        bargap=0.05,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            showgrid=True, gridcolor='rgba(0, 255, 242, 0.1)', zeroline=False,
            range=[1.0, df_odds['Winner_Odd'].quantile(0.99) + 0.5]
        ),
        yaxis=dict(
            showgrid=True, gridcolor='rgba(0, 255, 242, 0.1)', zeroline=False
        )
    )
    
    return fig

@app.callback(
    Output('timeline-chart', 'figure'),
    [Input('player-slicer', 'value'),
     Input('year-slicer', 'value')]
)
def update_timeline(player_name, selected_year):
    if not player_name or not selected_year:
        return {}

    player_df = df[
        ((df['Player_1'] == player_name) | (df['Player_2'] == player_name)) &
        (df['Year'] == selected_year)
    ].copy()

    if player_df.empty:
        return {
            'layout': {
                'title': f"No data available for {player_name} in {selected_year}",
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0.1)',
                'font': {'color': '#ffffff'}
            }
        }

    player_df = player_df.sort_values(by='Date')
    ordered_tournaments = player_df['Tournament'].unique().tolist() 

    player_df['Outcome'] = player_df.apply(
        lambda row: 'Win' if row['Winner'] == player_name else 'Loss',
        axis=1
    )
    
    player_df['Start_Date'] = player_df['Date']
    player_df['End_Date'] = player_df['Date'] + timedelta(days=1)

    fig = px.timeline(
        player_df,
        x_start="Start_Date",
        x_end="End_Date",
        y="Tournament",
        color="Outcome",
        color_discrete_map={'Win': '#10b981', 'Loss': '#ef4444'},
        title=f"Tournament Performance of {player_name} in {selected_year}",
        hover_data=['Date', 'Round', 'Score'],
        category_orders={'Tournament': ordered_tournaments} 
    )
    
    fig.update_layout(
        xaxis_title=None, 
        yaxis_title=None, 
        xaxis_type="date",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        font=dict(color='#ffffff'),
        height=600, 
        yaxis=dict(
            dtick=1,       
            automargin=True 
        )
    )

    return fig

@app.callback(
    Output('radar-chart', 'figure'),
    [Input('player-slicer', 'value')]
)
def update_radar(player_name):
    if not player_name:
        return {}

    player_df = df[(df['Player_1'] == player_name) | (df['Player_2'] == player_name)].copy()

    if player_df.empty:
        return {
            'layout': {
                'title': f"No data available for {player_name}",
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0.1)',
                'font': {'color': '#ffffff'}
            }
        }
    
    wins_per_surface = player_df[player_df['Winner'] == player_name]['Surface'].value_counts()
    matches_per_surface = player_df.groupby('Surface').size()
    
    all_surfaces = player_df['Surface'].unique()
    wins_per_surface = wins_per_surface.reindex(all_surfaces, fill_value=0)
    matches_per_surface = matches_per_surface.reindex(all_surfaces, fill_value=0)

    win_percentage = (wins_per_surface / matches_per_surface).fillna(0) * 100
    win_percentage_df = win_percentage.reset_index()
    win_percentage_df.columns = ['Surface', 'Win_Percentage']

    fig = px.line_polar(
        win_percentage_df,
        r='Win_Percentage',
        theta='Surface',
        line_close=True,
        range_r=[0, 100],
        title=f"Win Percentage by Surface for {player_name}"
    )
    
    fig.update_traces(fill='toself', line_color='#00fff2', fillcolor='rgba(0, 255, 242, 0.3)')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        polar=dict(
            bgcolor='rgba(0,0,0,0.1)',
            radialaxis=dict(gridcolor='rgba(0, 255, 242, 0.2)', showline=False, tickfont=dict(color="#ffffff")),
            angularaxis=dict(gridcolor='rgba(0, 255, 242, 0.2)', showline=False, tickfont=dict(color="#ffffff"))
        )
    )

    return fig

def create_odds_time_series(player1, player2):
    h2h = df[
        ((df["Player_1"] == player1) & (df["Player_2"] == player2)) |
        ((df["Player_1"] == player2) & (df["Player_2"] == player1))
    ].copy()

    def get_player_odds(row, player):
        return row["Odd_1"] if row["Player_1"] == player else row["Odd_2"]

    h2h["Odd_p1"] = h2h.apply(lambda r: get_player_odds(r, player1), axis=1)
    h2h["Odd_p2"] = h2h.apply(lambda r: get_player_odds(r, player2), axis=1)

    plot_df = pd.melt(
        h2h,
        id_vars=["Date", "Tournament", "Round", "Score", "Surface"],
        value_vars=["Odd_p1", "Odd_p2"],
        var_name="Player_Var",
        value_name="Odds"
    )

    plot_df["Player"] = plot_df["Player_Var"].replace({
        "Odd_p1": player1,
        "Odd_p2": player2
    })
    
    plot_df = plot_df.sort_values("Date")
    plot_df = plot_df.dropna(subset=['Odds'])
    
    fig = px.line(
        plot_df,
        x="Date",
        y="Odds",
        color="Player",
        markers=True,
        color_discrete_map={
            player1: '#667eea', 
            player2: '#f472b6' 
        },
        hover_data={
            "Tournament": True,
            "Round": True,
            "Score": True,
            "Surface": True,
            "Date": '|%Y-%m-%d',
            "Odds": ':.2f',
            "Player_Var": False
        },
        title=f"Odds Change Over: {player1} vs {player2}"
    )

    fig.update_layout(
        font=dict(color='#ffffff'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        xaxis=dict(showgrid=True, gridcolor='rgba(0, 255, 242, 0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(0, 255, 242, 0.1)', range=[1, plot_df['Odds'].max() * 1.1])
    )
    
    return fig

@app.callback(
    Output('player-kpi-row', 'children'),
    [Input('player-slicer', 'value')]
)
def update_player_kpis(player_name):
    if not player_name:
        return []

    player_df = df[(df['Player_1'] == player_name) | (df['Player_2'] == player_name)].copy()

    if player_df.empty:
        return [html.Div(f"No career data available for {player_name}.", 
                         style={'color': '#00fff2', 'textAlign': 'center', 'padding': '20px'})]

    total_matches = len(player_df)
    total_wins = len(player_df[player_df['Winner'] == player_name])
    
    final_wins_df = player_df[(player_df['Winner'] == player_name) & (player_df['Round'] == 'Final')]
    gs_titles = final_wins_df[final_wins_df['Series'] == 'Grand Slam'].shape[0]
    total_final_wins = final_wins_df.shape[0]
    atp_tour_titles = total_final_wins

    def create_kpi_card(title, value, icon, gradient):
        return html.Div(
            style={
                'background': gradient,
                'borderRadius': '16px',
                'padding': '28px 24px',
                'textAlign': 'center',
                'boxShadow': '0 0 30px rgba(0, 255, 242, 0.2)',
                'border': '2px solid rgba(0, 255, 242, 0.3)',
                'transition': 'all 0.3s ease',
                'position': 'relative',
                'overflow': 'hidden'
            },
            children=[
                html.Div(
                    icon,
                    style={
                        'fontSize': '36px',
                        'marginBottom': '12px',
                        'filter': 'drop-shadow(0 0 10px rgba(255, 255, 255, 0.5))'
                    }
                ),
                html.P(
                    title,
                    style={
                        'margin': '0 0 10px 0',
                        'fontSize': '12px',
                        'fontWeight': '700',
                        'color': 'rgba(255, 255, 255, 0.9)',
                        'fontFamily': '"Orbitron", sans-serif',
                        'letterSpacing': '1.5px',
                        'textTransform': 'uppercase'
                    }
                ),
                html.H3(
                    f"{value}",
                    style={
                        'margin': '0',
                        'fontSize': '42px',
                        'fontWeight': 'bold',
                        'color': '#00fff2',
                        'textShadow': '0 0 20px rgba(0, 255, 242, 0.8)',
                        'fontFamily': '"Orbitron", sans-serif'
                    }
                )
            ]
        )

    kpi_data = [
        {'title': 'Total Matches', 'value': total_matches, 'icon': '🎾', 'bg': 'linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%)'},
        {'title': 'Career Wins', 'value': total_wins, 'icon': '🏆', 'bg': 'linear-gradient(135deg, rgba(17, 153, 142, 0.3) 0%, rgba(56, 239, 125, 0.3) 100%)'},
        {'title': 'Tour Titles', 'value': atp_tour_titles, 'icon': '🥇', 'bg': 'linear-gradient(135deg, rgba(245, 158, 11, 0.3) 0%, rgba(249, 115, 22, 0.3) 100%)'},
        {'title': 'Grand Slams', 'value': gs_titles, 'icon': '👑', 'bg': 'linear-gradient(135deg, rgba(217, 70, 239, 0.3) 0%, rgba(139, 92, 246, 0.3) 100%)'}
    ]
    
    kpis = html.Div(
        style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
            'gap': '20px'
        },
        children=[create_kpi_card(k['title'], k['value'], k['icon'], k['bg']) for k in kpi_data]
    )

    return kpis

@app.callback(
    Output('1v1-results', 'children'),
    [Input('player1-slicer', 'value'),
     Input('player2-slicer', 'value')]
)
def update_1v1_comparison(player1, player2):
    if not player1 or not player2:
        return html.Div("Please select two players to compare.", 
                        style={'color': '#00fff2', 'textAlign': 'center', 'padding': '20px'})

    h2h_df = df[
        ((df['Player_1'] == player1) & (df['Player_2'] == player2)) |
        ((df['Player_1'] == player2) & (df['Player_2'] == player1))
    ].copy()

    if h2h_df.empty:
        return html.Div("No head-to-head matches found for these players.", 
                        style={'color': '#00fff2', 'textAlign': 'center', 'padding': '20px'})

    total_matches = len(h2h_df)
    p1_wins = len(h2h_df[h2h_df['Winner'] == player1])
    p2_wins = len(h2h_df[h2h_df['Winner'] == player2])
    
    last_3_matches = h2h_df.sort_values(by='Date', ascending=False).head(3)

    round_counts = h2h_df['Round'].value_counts().reset_index()
    round_counts.columns = ['Round', 'Matches']
    
    round_chart = dcc.Graph(
        figure=px.pie(
            round_counts, 
            names='Round', 
            values='Matches', 
            hole=0.4, 
            title="Meetings by Round"
        ).update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff')
        )
    )
    
    odds_line_chart = dcc.Graph(
        figure=create_odds_time_series(player1, player2)
    )

    return html.Div([
        html.Div(
            style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
                'gap': '24px',
                'marginBottom': '40px'
            },
            children=[
                html.Div(
                    style={
                        'background': 'linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%)',
                        'borderRadius': '16px',
                        'padding': '32px 24px',
                        'textAlign': 'center',
                        'boxShadow': '0 0 30px rgba(0, 255, 242, 0.2)',
                        'border': '2px solid rgba(0, 255, 242, 0.3)'
                    },
                    children=[
                        html.Div("📊", style={'fontSize': '36px', 'marginBottom': '12px'}),
                        html.P("TOTAL MATCHES", 
                               style={
                                   'fontSize': '12px',
                                   'fontWeight': '700',
                                   'margin': '0 0 10px 0',
                                   'color': 'rgba(255, 255, 255, 0.9)',
                                   'fontFamily': '"Orbitron", sans-serif',
                                   'letterSpacing': '1.5px'
                               }),
                        html.H2(f"{total_matches}", 
                                style={
                                    'fontSize': '42px',
                                    'fontWeight': 'bold',
                                    'margin': '0',
                                    'color': '#00fff2',
                                    'textShadow': '0 0 20px rgba(0, 255, 242, 0.8)',
                                    'fontFamily': '"Orbitron", sans-serif'
                                })
                    ]
                ),
                
                html.Div(
                    style={
                        'background': 'linear-gradient(135deg, rgba(17, 153, 142, 0.3) 0%, rgba(56, 239, 125, 0.3) 100%)',
                        'borderRadius': '16px',
                        'padding': '32px 24px',
                        'textAlign': 'center',
                        'boxShadow': '0 0 30px rgba(0, 255, 242, 0.2)',
                        'border': '2px solid rgba(0, 255, 242, 0.3)'
                    },
                    children=[
                        html.Div("🏅", style={'fontSize': '36px', 'marginBottom': '12px'}),
                        html.P(f"{player1} WINS", 
                               style={
                                   'fontSize': '12px',
                                   'fontWeight': '700',
                                   'margin': '0 0 10px 0',
                                   'color': 'rgba(255, 255, 255, 0.9)',
                                   'fontFamily': '"Orbitron", sans-serif',
                                   'letterSpacing': '1.5px'
                               }),
                        html.H2(f"{p1_wins}", 
                                style={
                                    'fontSize': '42px',
                                    'fontWeight': 'bold',
                                    'margin': '0',
                                    'color': '#00fff2',
                                    'textShadow': '0 0 20px rgba(0, 255, 242, 0.8)',
                                    'fontFamily': '"Orbitron", sans-serif'
                                })
                    ]
                ),
                
                html.Div(
                    style={
                        'background': 'linear-gradient(135deg, rgba(252, 70, 107, 0.3) 0%, rgba(63, 94, 251, 0.3) 100%)',
                        'borderRadius': '16px',
                        'padding': '32px 24px',
                        'textAlign': 'center',
                        'boxShadow': '0 0 30px rgba(0, 255, 242, 0.2)',
                        'border': '2px solid rgba(0, 255, 242, 0.3)'
                    },
                    children=[
                        html.Div("🏅", style={'fontSize': '36px', 'marginBottom': '12px'}),
                        html.P(f"{player2} WINS", 
                               style={
                                   'fontSize': '12px',
                                   'fontWeight': '700',
                                   'margin': '0 0 10px 0',
                                   'color': 'rgba(255, 255, 255, 0.9)',
                                   'fontFamily': '"Orbitron", sans-serif',
                                   'letterSpacing': '1.5px'
                               }),
                        html.H2(f"{p2_wins}", 
                                style={
                                    'fontSize': '42px',
                                    'fontWeight': 'bold',
                                    'margin': '0',
                                    'color': '#00fff2',
                                    'textShadow': '0 0 20px rgba(0, 255, 242, 0.8)',
                                    'fontFamily': '"Orbitron", sans-serif'
                                })
                    ]
                ),
            ]
        ),
        
        html.Div(
            style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(400px, 1fr))',
                'gap': '30px',
                'marginBottom': '40px'
            },
            children=[
                html.Div(
                    style={
                        'background': 'rgba(0, 255, 242, 0.03)',
                        'borderRadius': '16px',
                        'padding': '25px',
                        'border': '1px solid rgba(0, 255, 242, 0.15)'
                    },
                    children=round_chart
                ),
                html.Div(
                    style={
                        'background': 'rgba(0, 255, 242, 0.03)',
                        'borderRadius': '16px',
                        'padding': '25px',
                        'border': '1px solid rgba(0, 255, 242, 0.15)'
                    },
                    children=odds_line_chart
                )
            ]
        ),

        html.Div([
            html.Div(
                style={
                    'textAlign': 'center',
                    'marginBottom': '32px',
                    'padding': '0 16px'
                },
                children=[
                    html.H3("Last 3 Head-to-Head Encounters", 
                            style={
                                'fontSize': '24px',
                                'fontWeight': '700',
                                'color': '#00fff2',
                                'margin': '0 0 8px 0',
                                'fontFamily': '"Orbitron", sans-serif',
                                'textTransform': 'uppercase',
                                'letterSpacing': '2px',
                                'textShadow': '0 0 10px rgba(0, 255, 242, 0.5)'
                            })
                ]
            ),
            html.Div(
                style={
                    'display': 'grid',
                    'gridTemplateColumns': 'repeat(auto-fit, minmax(320px, 1fr))',
                    'gap': '24px',
                    'padding': '0 16px'
                },
                children=[
                    html.Div(
                        style={
                            'background': 'rgba(15, 23, 42, 0.8)',
                            'backdropFilter': 'blur(5px)',
                            'borderRadius': '16px',
                            'padding': '24px',
                            'boxShadow': '0 0 20px rgba(0, 255, 242, 0.1)',
                            'border': '1px solid rgba(0, 255, 242, 0.2)',
                            'position': 'relative',
                            'overflow': 'hidden'
                        },
                        children=[
                            html.Div(
                                f"Match {i+1}",
                                style={
                                    'position': 'absolute',
                                    'top': '16px',
                                    'right': '20px',
                                    'background': '#00fff2',
                                    'color': '#0a0e27',
                                    'padding': '6px 12px',
                                    'borderRadius': '20px',
                                    'fontSize': '12px',
                                    'fontWeight': 'bold'
                                }
                            ),
                            
                            html.Div(
                                style={'marginBottom': '16px'},
                                children=[
                                    html.H4(row['Tournament'], 
                                            style={
                                                'fontSize': '20px',
                                                'fontWeight': '700',
                                                'color': '#ffffff',
                                                'margin': '0 0 6px 0',
                                                'fontFamily': '"Orbitron", sans-serif'
                                            }),
                                    html.P(row['Date'].strftime('%B %d, %Y'), 
                                           style={
                                               'fontSize': '14px',
                                               'color': 'rgba(255, 255, 255, 0.7)',
                                               'margin': '0'
                                           })
                                ]
                            ),
                            
                            html.Div(
                                style={
                                    'backgroundColor': 'rgba(16, 185, 129, 0.1)',
                                    'border': '2px solid #10b981',
                                    'borderRadius': '12px',
                                    'padding': '16px',
                                    'marginBottom': '12px'
                                },
                                children=[
                                    html.Div(
                                        style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},
                                        children=[
                                            html.Span("🏆", style={'fontSize': '20px', 'marginRight': '8px'}),
                                            html.Span("Winner: ", style={'fontWeight': '600', 'color': 'rgba(255, 255, 255, 0.8)', 'marginRight': '5px'}),
                                            html.Span(row['Winner'], 
                                                      style={
                                                          'fontWeight': 'bold', 
                                                          'color': '#10b981',
                                                          'fontSize': '16px'
                                                      })
                                        ]
                                    )
                                ]
                            ),
                            
                            html.Div(
                                style={
                                    'backgroundColor': 'rgba(245, 158, 11, 0.1)',
                                    'border': '2px solid #f59e0b',
                                    'borderRadius': '12px',
                                    'padding': '16px',
                                    'textAlign': 'center'
                                },
                                children=[
                                    html.P("Final Score", 
                                           style={
                                               'fontSize': '12px',
                                               'color': 'rgba(255, 255, 255, 0.8)',
                                               'margin': '0 0 4px 0',
                                               'fontWeight': '600',
                                               'textTransform': 'uppercase'
                                           }),
                                    html.P(row['Score'], 
                                           style={
                                               'fontSize': '18px',
                                               'fontWeight': 'bold',
                                               'color': '#f59e0b',
                                               'margin': '0',
                                               'fontFamily': 'monospace'
                                           })
                                ]
                            )
                        ]
                    ) for i, (_, row) in enumerate(last_3_matches.iterrows())
                ]
            )
        ]),
    ])

if __name__ == '__main__':
    app.run(debug=False)
