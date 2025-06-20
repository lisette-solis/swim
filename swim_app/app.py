from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Alternative: Import from config file
# from config import Config

app = Flask(__name__)


class LLMWorkoutGenerator:
    def __init__(self):
        # You can switch between different LLM providers
        self.provider = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")

        # API keys - loaded from .env file or environment variables
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

    def create_workout_prompt(
        self,
        distance: int,
        stroke: str,
        equipment: List[str],
        experience: str,
        additional_notes: str = "",
    ) -> str:
        """Create a detailed prompt for the LLM to generate a swimming workout."""

        equipment_str = ", ".join(equipment) if equipment else "no equipment"

        prompt = f"""You are an expert swimming coach. Create a detailed {distance} meter swimming workout with the following specifications:

        **Workout Parameters:**
        - Total Distance: {distance} meters (must add up exactly)
        - Focus Stroke: {stroke}
        - Available Equipment: {equipment_str}
        - Swimmer Experience: {experience}
        - Additional Notes: {additional_notes}

        **Workout Requirements:**
        1. Structure the workout with clear sections: Warm-up, Drill Set, Main Set, Cool-down
        2. Include specific distances for each exercise that add up to exactly {distance}m
        3. Incorporate common drills appropriate for {stroke}
        4. Use the available equipment ({equipment_str}) creatively throughout the workout
        5. Adjust intensity and complexity based on {experience} level
        6. Include rest intervals and specific technique focuses
        7. Format the workout clearly with distances, repetitions, and instructions

        **Experience Level Guidelines:**
        - Beginner: Shorter reps (25-50m), more rest, basic technique focus
        - Intermediate: Medium reps (50-100m), moderate rest, technique + speed work
        - Advanced: Longer reps (100-200m+), less rest, complex sets and race pace work

        **Equipment Usage:**
        - Fins: Speed work, kick sets, underwater dolphin kick
        - Kickboard: Used for kick sets, begginer drills like catch-up
        - Paddles: Strength building, catch improvement, pull sets
        - Pull Buoy: Upper body focus, stroke rate work

        Please provide a complete, structured workout that swimmers can follow exactly."""

        print(f"prompt: {prompt}")
        return prompt

    def call_gemini_api(self, prompt: str) -> str:
        """Call Google's Gemini API."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        # Gemini API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"

        headers = {"Content-Type": "application/json"}

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
                "stopSequences": [],
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
            ],
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise Exception("No response generated from Gemini")
        else:
            raise Exception(
                f"Gemini API call failed: {response.status_code} - {response.text}"
            )

    def generate_workout(
        self,
        distance: int,
        stroke: str,
        equipment: List[str],
        experience: str,
        additional_notes: str = "",
    ) -> str:
        """Generate a workout using the configured LLM provider."""

        prompt = self.create_workout_prompt(
            distance, stroke, equipment, experience, additional_notes
        )

        try:
            if self.provider == "gemini":
                return self.call_gemini_api(prompt)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")

        except Exception as e:
            # Fallback to a basic workout if LLM fails
            return self.generate_fallback_workout(
                distance, stroke, equipment, experience
            )

    def generate_fallback_workout(
        self, distance: int, stroke: str, equipment: List[str], experience: str
    ) -> str:
        """Generate a basic workout if LLM is unavailable."""
        return f"""**FALLBACK WORKOUT - {distance}m {stroke.upper()}**
(LLM temporarily unavailable)

**Warm-up (400m)**
- 200m easy {stroke}
- 4 x 50m build {stroke}

**Main Set ({distance-600}m)**
- 8 x 100m {stroke} at moderate effort
- Rest 20 seconds between each

**Cool-down (200m)**
- 200m easy choice stroke

**Total: {distance}m**

Note: This is a basic fallback workout. Please check your LLM configuration for custom workouts."""


# Initialize workout generator
generator = LLMWorkoutGenerator()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate_workout", methods=["POST"])
def generate_workout():
    try:
        data = request.get_json()

        total_distance = int(data.get("distance", 2000))
        focus_stroke = data.get("stroke", "freestyle")
        equipment = data.get("equipment", [])
        experience_level = data.get("experience", "intermediate")
        additional_notes = data.get("notes", "")

        workout = generator.generate_workout(
            total_distance, focus_stroke, equipment, experience_level, additional_notes
        )

        return jsonify({"workout": workout})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/set_provider", methods=["POST"])
def set_provider():
    """Endpoint to change LLM provider."""
    try:
        data = request.get_json()
        provider = data.get("provider")

        if provider in ["gemini", "anthropic", "openai", "local"]:
            generator.provider = provider
            return jsonify({"success": True, "provider": provider})
        else:
            return jsonify({"error": "Invalid provider"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Print configuration info
    print(f"LLM Provider: {generator.provider}")
    print(f"Gemini API Key: {'Set' if generator.gemini_api_key else 'Not set'}")
    print("Starting Flask app...")

    app.run(debug=True)
