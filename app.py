import io
import requests
from flask import Flask, request
from PIL import Image
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

def predict_crop_disease(image_bytes):
    """
    Mock AI Model Pipeline.
    This replaces your deep learning framework inference loop.
    """
    # In production, you would run:
    # model = load_model("banana_model.h5")
    # prediction = model.predict(image_bytes)
    
    # Mocking a positive classification result for test verification
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
    else:
        return "Stage: Mature.\nFocus on high Potassium (MOP) inputs."

@app.route("/webhook", methods=['POST'])
def whatsapp_webhook():
    response = MessagingResponse()
    msg = response.message()
    
    # 1. Check if the incoming message contains an image/media attachment
    num_media = int(request.values.get('NumMedia', 0))
    
    if num_media > 0:
        # Get the public direct URL of the uploaded image file hosted on Twilio's cloud
        media_url = request.values.get('MediaUrl0')
        content_type = request.values.get('MediaContentType0', '')
        
        # Verify the file is an image
        if 'image' in content_type:
            try:
                # Download the image directly into server RAM safely using requests
                img_response = requests.get(media_url)
                image_bytes = io.BytesIO(img_response.content)
                
                # Verify it can be read as a valid picture format
                test_image = Image.open(image_bytes)
                
                # Execute your classification model function
                ai_result = predict_crop_disease(image_bytes)
                
                reply = (
                    f"⚠️ *AI Diagnosis Report* ⚠️\n\n"
                    f"*Detected:* {ai_result['disease']}\n"
                    f"*Confidence:* {ai_result['confidence'] * 100:.1f}%\n\n"
                    f"*Recommended Actions:*\n{ai_result['remedy']}"
                )
            except Exception as e:
                reply = f"❌ Error processing image file: Unable to execute AI scan. ({str(e)})"
        else:
            reply = "❌ Unsupported file type. Please send a clear, uncompressed leaf photo (.jpg/.png)."
            
    # 2. If it is standard text, fall back to the text-based workflow engine
    else:
        incoming_msg = request.values.get('Body', '').strip()
        if incoming_msg.lower() in ['hi', 'hello', 'start']:
            reply = "Welcome to your Digital Farm Assistant! 🌾\n\n• *To get nutrition advice:* Send crop age in days.\n• *To scan for disease:* Send a clear photo of the infected leaf."
        else:
            try:
                age = int(incoming_msg)
                reply = calculate_banana_fertilizer(age)
            except ValueError:
                reply = "Send a crop age in days (e.g. '45') or upload an image of a crop leaf to process."

    msg.body(reply)
    return str(response)

if __name__ == "__main__":
    app.run(port=5000)