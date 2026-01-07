# 🎾 Professional Men's Tennis Analytics Dashboard

An interactive, data-driven dashboard analyzing professional men's tennis matches (ATP) from 2000 to 2025. This project visualizes player performance, betting odds, and tournament statistics using a modern, futuristic UI.

## 🚀 Live Demo

You can access the deployed application here:
👉 **[https://my-tennis-dashboard.onrender.com/](https://my-tennis-dashboard.onrender.com/)**

---

## 📊 Dashboard Features

The dashboard is divided into several analytical sections:

* **🏆 Series Kings:** A horizontal bar chart showcasing the players with the most wins, filtered by surface and tournament series.
* **☀️ Path to Victory:** A Sunburst chart visualizing the hierarchy of surfaces, rounds, and sets needed for victories.
* **⚖️ Quality Gap (Odds Analysis):** A deep dive into betting odds, comparing favorites vs. underdogs across different tournament categories.
* **👤 Individual Player Performance:**
    * **KPI Cards:** Key metrics (Total Matches, Career Wins, Tour Titles, Grand Slams).
    * **Tournament Timeline:** A Gantt-style chart showing a player's run in various tournaments throughout a specific year.
    * **Surface Radar:** A radar chart displaying win percentages across Hard, Clay, Grass, and Carpet courts.
* **⚔️ Head-to-Head Comparison:** A direct comparison tool between two players, featuring:
    * Win counters.
    * Matches by round breakdown.
    * Historical odds evolution graph.
    * Detailed cards for the last 3 encounters.

## 🛠️ Built With

* **Python 3.13**
* **[Dash](https://dash.plotly.com/)** - The core framework for the web application.
* **[Plotly](https://plotly.com/python/)** - For creating interactive and responsive charts.
* **Pandas** - For data cleaning and manipulation.
* **Dash Bootstrap Components** - For the responsive grid layout.
* **Render** - Cloud hosting platform used for deployment.

## 📂 Installation (Run Locally)

If you want to run this project on your local machine:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Regeleardealui/tennis-analytics.git](https://github.com/Regeleardealui/tennis-analytics.git)
    cd tennis-analytics
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the app:**
    ```bash
    python app.py
    ```

4.  Open your browser and navigate to `http://127.0.0.1:8050/`.

---
