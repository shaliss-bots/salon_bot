from flask import Flask, request
import json
from twilio.twiml.messaging_response import MessagingResponse
import json  
from services import services
import responses
from language import detect_language

app = Flask(__name__)

user_state = {}

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
        user_state[user] = {"step": "start"}

    state = user_state[user]
    resp = MessagingResponse()
    
    #welcome logo
    if state["step"] == "start":
        lang = detect_language(msg)
        state["lang"] = lang
        state["step"] = "service"

        message = resp.message("Welcome to *Glow Salon*\n\n"
                               "Your beauty assistant and you can talk in your langunage\n\n")
        
        message.media("https://res.cloudinary.com/dd4bsgg46/image/upload/v1768571938/Untitled_design_2_t1kqlx.png")


    # STEP 2: Service selection
    if state["step"] == "service":
        for key in services:
            if key in msg:
                state["service"] = services[key]["name"]
                state["step"] = "time"

                return (
                    f"Great choice 👍\n\n"
                    f"{services[key]['name']} {services[key]['price']}\n\n"
                    f"Available slots:\n11 AM\n1 PM\n4 PM\n\n"
                    f"Kaunsa time convenient rahega?"
                )

        return "Please choose a valid service 😊"

    # STEP 3: Time
    if state["step"] == "time":
        state["time"] = msg
        state["step"] = "name"
        return responses.ask_name(state["lang"])

    # STEP 4: Name
    if state["step"] == "name":
        state["name"] = msg.title()
        state["step"] = "done"

        save_booking(state)

        return responses.confirm(
            state["name"],
            state["service"],
            state["time"],
            state["lang"]
        )

    return "Type hi to restart 😊"


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)