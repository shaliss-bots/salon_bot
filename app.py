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

services= {
    "haircut":300,
    "facial":800,
    "hair spa":1200,
    "cleanup":600,
    "waxing":700,
    "makeup":2500
}

slots = ["11 AM" ,"1 PM","4 PM"]


responses = {

    "english": {

        "slot":
        "✨ {service} price is ₹{price}\nAvailable slots:\n11 AM\n1 PM\n4 PM 😊",

        "name":
        "😊 May I know your name for booking?",

        "confirm":
        "✨ Booking Confirmed 🎉\n{name}, your {service} appointment is booked for {slot}.\nPrice: ₹{price} 😊",
        
          
    },

    "hindi": {

        "slot":
        "✨ {service} ka price ₹{price} hai\nAvailable slots:\n11 AM\n1 PM\n4 PM 😊",

        "name":
        "😊 Booking ke liye aapka naam bata dijiye.",

        "confirm":
        "✨ Booking Confirmed 🎉\n{name} ji, aapka {service} appointment {slot} ke liye book ho gaya hai.\nPrice: ₹{price} 😊"
    },

    "punjabi": {

        "slot":
        "✨ {service} da price ₹{price} aa\nAvailable slots:\n11 AM\n1 PM\n4 PM 😊",

        "name":
        "😊 Booking layi apna naam dass deo.",

        "confirm":
        "✨ Booking Confirmed 🎉\n{name} ji, tuhadi {service} appointment {slot} layi book ho gayi aa.\nPrice: ₹{price} 😊"
    },

    "marathi": {

        "slot":
        "✨ {service} chi price ₹{price} aahe\nAvailable slots:\n11 AM\n1 PM\n4 PM 😊",

        "name":
        "😊 Booking sathi tumcha nav सांगा.",

        "confirm":
        "✨ Booking Confirmed 🎉\n{name}, tumchi {service} appointment {slot} la confirm zali aahe.\nPrice: ₹{price} 😊"
    }

}


def detect_user(user_message):

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[

            {
                "role": "system",
                 "content": """
                   You are ONLY a language analyzer.

                    Detect:

                   1. language
                   2. tone
                   3. intent

                   Possible languages:
                   english
                   hindi
                   punjabi
                   marathi
                   chhattisgarhi

                   Possible intents:
                   booking
                   consultation
                   chat
                   
                   If intent is consultation, also generate a short natural salon
                   consultation reply in the same language as the user.
                   
                   If intent is booking, keep reply empty.
                   

                  Reply ONLY in JSON format.

                  Example:
                  {
                    "language":"punjabi",
                     "tone":"casual",
                     "intent":"consultation",
                     "reply":"Hair spa health reh sakda ho tusi😊"
                    }
                    
                    {
                        "language":"punjabi",
                        "tone":"casual",
                        "intent":"booking",
                        "reply":""
                    }
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
    
    detected = detect_user(msg)
    
    data = json.loads(detected)
    
    language = data["language"]
    tone = data["tone"]
    intent = data["intent"]
    reply_text = data["reply"]
    

    if user not in user_state:
        user_state[user] = {
            "welcome": False,
            "step":"start",
            "service":"",
            "slot":"",
            "name":"",
            "language":"",
            "tone":"casual",
            "intent":"booking"
            
        }

    state = user_state[user]
    
    state["language"] = language
    state["tone"] = tone
    state["intent"] = intent
       
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
    
      #consultation reply
    booking_words =[
        "haircut",
        "facial",
        "cleanup",
        "waxing",
        "makeup",
        "spa"
    ]
    is_booking =( 
    any(word in msg for word in booking_words) or msg in services)
    
    if (
        intent == "consultation"
        and not is_booking
        and state["step"] == "start"
    ):   
        resp.message(reply_text)
        return str(resp) 
          
    # detect service
    for service in services:

      if service in msg:

        state["service"] = service
        state["step"] = "slot"

        price = services[service]

        lang = state["language"]
        
        print("LANGUAGE =", lang)
        reply = responses[lang]["slot"].format(service=service,price=price)
        
        resp.message(reply)
        return str(resp)


      # slot selection
    if state["step"] == "slot":
        
        msg = msg.strip().upper()
        
        valid_slots =["11","1","1 PM","4","4 PM"]
        
        if msg not in valid_slots:
            resp.message("Please select available slot 😊")
            return str(resp)

        state["slot"] = msg
        state["step"] = "name"

        lang = state.get("language")
        print(lang)
        
        
        reply = responses[lang]["name"]
       
        resp.message(reply)

        return str(resp)

      # final confirmation
    if state["step"] == "name":

       state["name"] = msg
       state["step"] = "done"

       service = state["service"]
       price = services[service]
       slot = state["slot"]
       name = state["name"]
       
       lang = state["language"]
       reply = responses[lang]["confirm"].format(
           name=name,
           service=service,
           price=price,
           slot=slot
       )  
     
       resp.message(reply)

       return str(resp)


 
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)