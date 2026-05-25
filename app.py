import io
import requests
from flask import Flask, request
from PIL import Image
from requests.auth import HTTPBasicAuth
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# paste your actual twilio keys inside these quotes
TWILIO_SID = "AC1ba26ca905ebb8520e4caa2c8a6aecfc" 
TWILIO_TOKEN = "--------------------------------"

def predict_crop_disease(image_bytes):
    """
    Mock AI Model Pipeline.
    """
    return {
        "disease": "Yellow Sigatoka Leaf Spot",
        "confidence": 0.92,
        "remedy": "Apply Propiconazole 25% EC (1 ml per liter of water). Ensure good drainage and remove severely infected leaves immediately."
    }

def calculate_banana_fertilizer(age_in_days):
    if age_in_days <= 30:
        return "Stage: Vegetative (Early).\nApply: 50g Urea, 50g SSP per plant."
    elif 30 < age_in_days <= 90:
        return "Stage: Vegetative (Peak).\nApply: 100g Urea, 100g MOP per plant."
    elif 90 < age_in_days <= 180:
        return "Stage: Shooting / Flowering.\nApply: 150g MOP, reduce Urea to 30g per plant.\nCheck closely for leaf spots."
    else:
        return "Stage: Fruit Development.\nFocus on high Potassium (MOP) inputs and steady water management."

@app.route("/webhook", methods=['POST'])
def whatsapp_webhook():
    response = MessagingResponse()
    msg = response.message()
    
    num_media = int(request.values.get('NumMedia', 0))
    
    if num_media > 0:
        media_url = request.values.get('MediaUrl0')
        
        try:
            # Explicit Basic Authentication Header matching Twilio requirement
            img_response = requests.get(
                media_url, 
                auth=HTTPBasicAuth(TWILIO_SID, TWILIO_TOKEN), 
                stream=True
            )

            if img_response.status_code == 200:
                image_bytes = io.BytesIO(img_response.content)
                
                with Image.open(image_bytes) as img:
                    img = img.convert('RGB')
                    ai_result = predict_crop_disease(image_bytes)
                    
                    reply = (
                        f"⚠️ *AI Diagnosis Report* ⚠️\n\n"
                        f"*Detected:* {ai_result['disease']}\n"
                        f"*Confidence:* {ai_result['confidence'] * 100:.1f}%\n\n"
                        f"*Recommended Actions:*\n{ai_result['remedy']}"
                    )
            else:
                reply = f"❌ Authorization Error: Twilio returned status code {img_response.status_code}. Please check keys."
        except Exception as e:
            reply = f"❌ Error processing image file: Unable to execute AI scan. ({str(e)})"
            
    else:
        incoming_msg = request.values.get('Body', '').strip()
        if incoming_msg.lower() in ['hi', 'hello', 'start']:
            reply = "Welcome to your Digital Farm Assistant! 🌾\n\n• *To get nutrition advice:* Send crop age in days.\n• *To scan for disease:* Send a clear photo of the infected leaf."
        else:
            try:
                age = int(incoming_msg)
                reply = calculate_banana_fertilizer(age)
            except ValueError:
                reply = "Send a crop age in days (e.g. '152') or upload an image of a crop leaf to process."

    msg.body(reply)
    return str(response)

if __name__ == "__main__":
    app.run(port=5000)
