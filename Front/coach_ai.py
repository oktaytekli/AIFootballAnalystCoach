import google.generativeai as genai
import config
from prompts import main_coach_prompt

class VirtualCoach:
    def __init__(self):
        genai.configure(api_key=config.API_KEY)
        
        self.models_to_try = [
            config.GEMINI_MODEL,
            'gemini-2.0-flash',
            'gemini-1.5-flash',
            'gemini-pro'
        ]
        self.active_model = None
        
        print("\nSearching for AI Model...")
        for model_name in self.models_to_try:
            try:
                clean_name = model_name.replace("models/", "")
                test_model = genai.GenerativeModel(clean_name)
                # Test request
                test_model.generate_content("Test")
                self.active_model = test_model
                print(f"SUCCESS: '{clean_name}' is active!")
                break
            except Exception:
                continue
        
        if not self.active_model:
            print("ERROR: Could not load any AI Model!")

    def analyze_game_data(self, match_logs):
        if not self.active_model: return "ERROR: No AI Connection."
        if not match_logs: return "Gathering data..."

        # Extract minute info from the last log line
        # Log format: "Min 24:15 | ..."
        last_log = match_logs[-1]
        minute_info = last_log.split("|")[0].strip()

        prompt = main_coach_prompt(match_logs, minute_info)
        
        try:
            response = self.active_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Analysis Error: {e}"