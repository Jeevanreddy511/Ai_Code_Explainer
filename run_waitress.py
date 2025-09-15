from waitress import serve
from Ai_Code_Explainer.wsgi import application

if __name__ == "__main__":
    serve(application, host="127.0.0.1", port=8000)
