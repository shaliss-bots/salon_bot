from flask import Flask, request
import json
from twilio.twiml.messaging_response import MessagingResponse
import json  
import os
from services import services
from openai import OpenAI
user_state = {}


app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def ask_ai(user_message):

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[

            {
                "role": "system",
                 "content": """
                  You are Glow Salon's premium AI WhatsApp assistant.

                  Your job:
                  - Talk like a real human salon receptionist.
                  - Understand ANY language naturally.
                  - Reply in the SAME language and tone as the user.
                  - Be warm, friendly, stylish and short.
                  - Never sound robotic.

                    Salon details:

                    Services and prices:
                    - Haircut = ₹300
                    - Facial = ₹800
                    - Hair Spa = ₹1200
                    - Makeup = ₹2500
                    - Waxing = ₹700
                    - Manicure = ₹500
                    - Pedicure = ₹600

                    Available booking times:
                    11 AM
                    1 PM
                    4 PM

                    Rules:
                    - If user wants a salon service, guide them naturally to booking.
                    - Ask only one thing at a time.
                    - First understand what service they want.
                    - Then ask preferred time.
                    - Then ask name.
                    - Then confirm booking beautifully.

                    Examples:
                    User: menu haircut karna si
                    Reply: Bilkul 😊 Haircut karvaoge. Tuhanu kehda time pasand aa? 11 AM, 1 PM ya 4 PM?

                    User: mujhe facial karana hai
                    Reply: Sure 😊 Facial available hai. Kaunsa timing prefer karoge?

                    User: price kya hai haircut ka
                    Reply: Haircut ₹300 ka hai 😊

                    User: tusi ki kar rahe ho
                    Reply: Bas tuhadi service layi ready haan 😊

                    Important:
                    - Understand slang, mixed language, typos and regional language naturally.
                    - Never say you are AI unless asked.
                    - Never give long paragraphs.
                    - Keep replies short and natural.
                    """
            },
            
            {
                "role": "user",
                "content": user_message
            }

        ]
    )

    return response.choices[0].message.content

def save_booking(data):
    with open("data.json", "r+") as f:
        bookings = json.load(f)
        bookings.append(data)
        f.seek(0)
        json.dump(bookings, f, indent=2)


@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.form.get("Body").lower()
    user = request.form.get("From")

    if user not in user_state:
        user_state[user] = {
            "welcomed": False
            
        }

    state = user_state[user]
    resp = MessagingResponse()
    
    
    #welcome logo
    
    if not state["welcome"]:

        state["welcomed"] = True

        # First send branding image
        image_msg = resp.message()
        image_msg.media("https://res.cloudinary.com/dd4bsgg46/image/upload/v1768571938/Untitled_design_2_t1kqlx.png")

        # Then send welcome message
        resp.message(
        """✨ *Glow Salon Assistant* ✨

        Hey beautiful 😊

        I’m here to help you with salon bookings and beauty services 💄

        Main tumhari language naturally samajh sakta hu.

        Hindi . English . Punjabi . Chhattisgarhi
   
        kaunsi service chahiye today? 😊
        """
        )
        return str(resp)
    
      # ai reply          
    ai_reply = ask_ai(msg)
    resp.message(ai_reply)
    return str(resp)

 
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)