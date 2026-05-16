from flask import Flask, request
import json
from twilio.twiml.messaging_response import MessagingResponse
import json  
import os
from services import services
import responses
from language import detect_language
from openai import OpenAI
user_state = {}


app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def ask_ai(user_message):

    response = client.chat.completions.create(

        model="gpt-3.5-turbo",

        messages=[

            {
                "role": "system",
                "content":  """

                You are a premium salon AI assistant on WhatsApp.

                Understand natural human conversation.

                Reply in the SAME:
                - language
                - tone
                - slang
                - conversational style

                as the user.

                Do NOT translate mechanically.

                Keep replies:
                - short
                - natural
                - warm
                - human-like

                You help users with:
                - salon bookings
                - beauty services
                - timings
                - pricing
                - recommendations

                Available services:
                - haircut
                - hair spa
                - facial
                - makeup
                - waxing
                - manicure
                - pedicure

                If the user changes service,
                adapt naturally.

                Always understand:
                - user intent
                - service name
                - language style

                Reply ONLY in valid JSON format like this:

                {
                   "intent": "booking",
                    "service": "haircut",
                    "reply": "natural reply here"
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

    if user not in user_state:
        user_state[user] = {
            "service": "",
            "time": "",
            "name": "",
            "intent": "",
            "welcomed": False,
            "lang": ""
        }

    state = user_state[user]
    resp = MessagingResponse()
    
    
    #welcome logo
    greetings = ["hi","hello","hey","hii"]
    
    if msg in greetings and not state["welcomed"]:
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
           
    #step 2 service             
           
    if state["step"] == "service":

     ai_reply = ask_ai(msg)

    ai_data = json.loads(ai_reply)
    
    intent = ai_data["intent"]
    service = ai_data["service"].lower()
    reply_text = ai_data["reply"]

    if intent == "booking" and service in services:

        state["service"] = service
        
        resp.message(

            f"{reply_text}\n\n"
            f"Available slots:\n"
            f"11 AM\n"
            f"1 PM\n"
            f"4 PM"
            )
        state["step"] = "time"

        return str(resp)

    else:

        resp.message(
            "Sorry 😊 please tell me service again."
        )

        return str(resp)        
        
            

    # STEP 3: Time
    if state["step"] == "time":
        state["time"] = msg
        state["step"] = "name"
    resp.message(responses.ask_name(state["lang"]))
    return str(resp)

    # STEP 4: Name
    if state["step"] == "name":
        state["name"] = msg
        state["step"] = "done"

        save_booking(state)

        resp.message(
            responses.confirm(
            state["name"],
            state["service"],
            state["time"],
            state["lang"]
                )    )
        return str(resp)

    resp.message("Type hi to restart 😊")
    return str(resp)

 
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)