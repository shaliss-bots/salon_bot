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
services={
    "haircut":300,
    "facial":800,
    "hair spa":1200,
    "cleanup":600,
    "waxing":700,
    "makeup":2500
}
slots =["11 AM" ,"1 PM","4 PM"]


def ask_ai(user_message):

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[

            {
                "role": "system",
                 "content": """
                  You are Glow Salon's AI receptionist on WhatsApp.

                   Talk naturally like a real salon receptionist.

                   IMPORTANT RULES:

                    * Always reply in the same language and tone as the user.
                    * Understand Hindi, Hinglish, Punjabi, English and mixed typing naturally.
                    * Keep replies short, natural and conversational.
                    * Sound warm, friendly and human-like.
                    * Never sound robotic.
                    * Never randomly switch languages during the conversation.
                    * Mirror the user's conversational style naturally.

                    LANGUAGE STYLE:

                    * If the user speaks casually, reply casually.
                    * If the user mixes languages, naturally mix languages too.
                    * Never mechanically translate sentences.
                    * Keep conversations smooth and realistic.

                     CONSULTATION RULES:

                    * If the user describes a beauty problem, respond like a real salon expert.
                    * Give natural beauty suggestions conversationally.
                    * If the user already knows what service they want, do not over-consult unnecessarily.

                     Never:

                    * behave like ChatGPT
                    * say "How may I help you?"
                    * give robotic replies
                    * ask unrelated questions

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
            "welcome": False,
            "step":"start",
            "service":"",
            "slot":"",
            "name":""
            
        }

    state = user_state[user]
    resp = MessagingResponse()
    
    
    #welcome logo
    
    if not state["welcome"]:

        state["welcome"] = True


        #  welcome message and branding logo
        welcome_msg = resp.message(
        """✨*Glow Salon Assistant*✨


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
    # detect service
    for service in services:

      if service in msg:

        state["service"] = service
        state["step"] = "slot"

        price = services[service]

        ai_reply = ask_ai(
            f"""
        User selected {service}.

        Price is ₹{price}.

        Ask preferred slot naturally in the SAME language as the user.

        Available slots:
        11 AM
        1 PM
        4 PM
        """
        )

        resp.message(ai_reply)

        return str(resp)


      # slot selection
    if state["step"] == "slot":

       state["slot"] = msg
       state["step"] = "name"

       ai_reply = ask_ai(
        """
       Ask customer's name naturally in the same language.
       """
       )

       resp.message(ai_reply)

       return str(resp)


      # final confirmation
    if state["step"] == "name":

       state["name"] = msg
       state["step"] = "done"

       service = state["service"]
       price = services[service]
       slot = state["slot"]
       name = state["name"]

       ai_reply = ask_ai(
        f"""
      Confirm salon booking naturally.

      Customer name: {name}
       Service: {service}
       Price: ₹{price}
       Slot: {slot}

      Reply in the SAME language and tone as the user.

      Make it feel like a real salon booking confirmation.
      """
     )

       resp.message(ai_reply)

       return str(resp)


    # fallback AI chat
    ai_reply = ask_ai(msg)

    resp.message(ai_reply)

    return str(resp)

 
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)