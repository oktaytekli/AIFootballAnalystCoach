import matplotlib.pyplot as plt
import google.generativeai as genai
import config
import json
import numpy as np

# --- SETTINGS ---
REPORT_FILE = "Match_Report.txt"

def analyze_report_with_ai():
    """Reads the report file and requests statistical estimates from Gemini."""
    print("📂 Reading report file...")
    try:
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("ERROR: Report file not found! Run main.py first.")
        return None

    print("🧠 Gemini is analyzing the match to extract statistics...")
    
    genai.configure(api_key=config.API_KEY)
    model = genai.GenerativeModel(config.GEMINI_MODEL)

    prompt = f"""
    Read the football match report and commentary below carefully.
    Based on these comments, ESTIMATE the general match statistics.
    
    Provide ONLY a valid JSON object with the following data structure:
    {{
        "team1_name": "Name of Team 1",
        "team2_name": "Name of Team 2",
        "possession": [55, 45],  // Sum must be 100 (Team 1, Team 2)
        "attack_score": [7, 5],   // Out of 10 (Team 1, Team 2)
        "defense_score": [6, 8],  // Out of 10
        "pass_accuracy": [80, 75], // Percentage
        "match_summary": "A short sentence summarizing the match"
    }}

    REPORT CONTENT:
    {content[-3000:]} 
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean JSON (Remove Markdown tags if present)
        json_str = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(json_str)
        return data
    except Exception as e:
        print(f"ERROR: AI could not parse the data. {e}")
        return None

def draw_charts(data):
    """Draws the Dashboard using the provided JSON data."""
    if not data: return

    t1 = data["team1_name"]
    t2 = data["team2_name"]
    
    # Chart Settings (Dark Theme)
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(14, 8))
    fig.suptitle(f"POST-MATCH AI ANALYSIS REPORT\n({t1} vs {t2})", fontsize=16, color='yellow')

    # --- CHART 1: POSSESSION (Pie Chart) ---
    ax1 = fig.add_subplot(1, 2, 1) # Left side
    labels = [t1, t2]
    sizes = data["possession"]
    colors = ['#ffcc00', '#333333'] # Yellow and Dark Grey
    explode = (0.05, 0) 

    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90, textprops={'fontsize': 12, 'color': 'white'})
    ax1.set_title("POSSESSION (Estimated)", fontsize=14, color="#4af")

    # --- CHART 2: PERFORMANCE RADAR (Spider Web) ---
    ax2 = fig.add_subplot(1, 2, 2, polar=True) # Right side (Polar)
    
    categories = ['Attack', 'Defense', 'Pass Accuracy (/10)', 'Tempo', 'Pressing']
    
    # Prepare data (Convert pass accuracy to scale of 10 for the chart)
    values_t1 = [
        data["attack_score"][0], 
        data["defense_score"][0], 
        data["pass_accuracy"][0] / 10, 
        data["attack_score"][0] * 0.8, # Estimated derivative metric
        data["defense_score"][0] * 0.9
    ]
    values_t2 = [
        data["attack_score"][1], 
        data["defense_score"][1], 
        data["pass_accuracy"][1] / 10,
        data["attack_score"][1] * 0.7,
        data["defense_score"][1] * 1.1
    ]
    
    # Close the chart loop by appending the first value to the end
    values_t1 += values_t1[:1]
    values_t2 += values_t2[:1]
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    
    # Drawing
    ax2.plot(angles, values_t1, color='#ffcc00', linewidth=2, label=t1)
    ax2.fill(angles, values_t1, color='#ffcc00', alpha=0.25)
    
    ax2.plot(angles, values_t2, color='gray', linewidth=2, label=t2)
    ax2.fill(angles, values_t2, color='gray', alpha=0.25)
    
    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(categories, color="white", size=10)
    ax2.set_title("TEAM PERFORMANCE CARD", fontsize=14, color="#4af", pad=20)
    ax2.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

    # Footer (Match Summary)
    plt.figtext(0.5, 0.05, f"AI COMMENT: {data['match_summary']}", ha="center", fontsize=11, 
                bbox={"facecolor":"#222", "alpha":0.8, "pad":10, "edgecolor":"#4af"})

    print("✅ Charts generated, displaying now...")
    plt.show()

if __name__ == "__main__":
    analysis_data = analyze_report_with_ai()
    if analysis_data:
        print(f"📊 Data Received: {analysis_data}")
        draw_charts(analysis_data)