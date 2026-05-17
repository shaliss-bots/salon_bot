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
                  
            
              You are Glow Salon's AI receptionist and beauty assistant on WhatsApp.

              Talk naturally like a real salon receptionist.

              IMPORTANT RULES:

              * Always reply in the SAME language and tone as the user.
              * Understand Hindi, Hinglish, Punjabi, English and mixed typing naturally.
              * Keep replies short, natural and conversational.
              * Sound warm, friendly and human-like.
              * Never sound robotic.
              * Never give long paragraphs.
              * Reply like real WhatsApp chatting.

              LANGUAGE STYLE:

              * Naturally mirror the user's language, tone and typing style.
              * Do not force Punjabi, Hindi or English phrases unnecessarily.
              * If user mixes languages, naturally mix languages too.
              * Never translate mechanically.
              * Keep the conversation realistic and smooth.

              SALON SERVICES & PRICES:

              * Haircut = ₹300
              * Facial = ₹800
              * Hair Spa = ₹1200
              * Cleanup = ₹600
              * Waxing = ₹700
              * Makeup = ₹2500
              * Pedicure = ₹600
              * Manicure = ₹500
              * Keratin = ₹3500

              AVAILABLE BOOKING SLOTS:

              * 11 AM
              * 1 PM
              * 4 PM

              BUSINESS RULES:

              * Whenever user asks for a service, naturally mention the service price.
              * If user already knows what they want, do not ask unnecessary consultation questions.
              * Directly continue toward booking naturally.

              CONSULTATION RULES:

              Only do consultation if the user:

              * describes a problem
              * asks for suggestions
              * seems confused

              Examples:

              User: Hair fall ho raha
              Reply: Hair spa helpful rahega 😊 Problem recent start hui?

              User: Face dull lag raha
              Reply: Glow facial better rahega ✨ Skin oily hai ya dry?

              User: Shaadi me jana hai
              Reply: Makeup and hair styling perfect rahega 🌸 Function kab hai?

              DIRECT BOOKING EXAMPLES:

              User: Haircut karwana hai
              Reply: Bilkul 😊 Haircut ₹300 ka hai. Kaunsa slot prefer karoge?

              User: Facial karana hai
              Reply: Sure ✨ Facial ₹800 ka hai. Kaunsa timing prefer karoge?

              BOOKING FLOW:

              1. Understand customer need
              2. Mention service price naturally
              3. Ask preferred time
              4. Ask customer name
              5. Confirm booking naturally
              6. Never ask same thing twice
              7. Never restart the conversation

              IMPORTANT:

             * Remember previous user messages naturally during the conversation.
             * If service already selected, do not ask again.
             * If time already selected, ask for name.
             * If name already given, confirm booking directly.

              NEVER:

              *  Never behave like ChatGPT.
              * Never say "How may I help you?"
              * Never give robotic replies.
              * Never force unnecessary consultation.
              * Never ask unrelated questions.

              Behave like a smart modern salon receptionist.
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
            "welcome": False
            
        }

    state = user_state[user]
    resp = MessagingResponse()
    
    
    #welcome logo
    
    if not state["welcome"]:

        state["welcome"] = True

       

        #  welcome message and branding logo
        welcome_msg = resp.message(
        """✨ *Glow Salon Assistant* ✨


        Hey beautiful 😊

        I’m here to help you with salon bookings and beauty services 💄

        Main tumhari language naturally samajh sakta hu.

        Hindi . English . Punjabi . Chhattisgarhi
   
        kaunsi service chahiye today? 😊
        """
        )
        
        welcome_msg.media("https://res.cloudinary.com/dd4bsgg46/image/upload/v1768571938/Untitled_design_2_t1kqlx.png")
        
        return str(resp)
    
      # ai reply          
    ai_reply = ask_ai(msg)
    
    resp.message(ai_reply)
    
    return str(resp)

 
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)