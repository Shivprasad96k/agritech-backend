from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

def calculate_banana_fertilizer(age_in_days):
    """
    Calculates exact fertilizer per banana plant based on growth stage.
    """
    if age_in_days <= 30:
        return "Stage: Vegetative (Early).\nApply: 50g Urea, 50g SSP (Single Super Phosphate) per plant.\nKeep soil damp."
    elif 30 < age_in_days <= 90:
        return "Stage: Vegetative (Peak).\nApply: 100g Urea, 100g MOP (Muriate of Potash) per plant.\nEnsure uniform drip irrigation."
    elif 90 < age_in_days <= 180:
        return "Stage: Shooting / Flowering.\nApply: 150g MOP, reduce Urea to 30g per plant.\nCheck closely for leaf spots."
    else:
        return "Stage: Fruit Development.\nFocus on high Potassium (MOP) inputs and steady water management. Do not add heavy Nitrogen."

@app.route("/webhook", methods=['POST'])
def whatsapp_webhook():
    # Read the text message sent by the farmer on WhatsApp
    incoming_msg = request.values.get('Body', '').strip()
    
    response = MessagingResponse()
    msg = response.message()
    
    # Simple operational routing logic
    if incoming_msg.lower() in ['hi', 'hello', 'start']:
        reply = "Welcome to your Digital Farm Assistant! 🌾\nPlease reply with your Banana crop age in days (e.g., '45') to get your custom fertilizer schedule."
    else:
        try:
            # Try to read the message as a crop age
            age = int(incoming_msg)
            reply = calculate_banana_fertilizer(age)
        except ValueError:
            reply = "I didn't quite catch that. Please send just the number of days (e.g., '60') or type 'hi' to start over."
            
    msg.body(reply)
    return str(response)

if __name__ == "__main__":
    app.run(port=5000)