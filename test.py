from intent_model import predict_intent

while True:
    text = input("You: ")
    intent, confidence = predict_intent(text)

    print("Predicted Intent:", intent)
    print("Confidence:", round(confidence, 2))
    print()