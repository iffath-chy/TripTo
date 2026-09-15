from google import genai

client = genai.Client(
    api_key="AQ.Ab8RN6LYpkYc5iO0-Bn9Mu_8-748rL3DNWnTAul-993FAu6w-g"
)

for model in client.models.list():
    print(model.name)