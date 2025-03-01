import urllib.request
import json
import os
import ssl

def allowSelfSignedHttps(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

def predict(data):
    allowSelfSignedHttps(True)
    body = str.encode(json.dumps(data))

    #url = 'http://1d0b4443-8610-4125-86cc-f3e226fb6c7b.westeurope.azurecontainer.io/score'
    #url = 'http://746ecc41-74c6-459f-b420-df039014d97b.westeurope.azurecontainer.io/score'
    #url = 'http://af285b00-8969-4255-8be3-5512191878de.westeurope.azurecontainer.io/score'
    url = 'http://8fd8b3e8-dba0-4199-bffc-70848a95f279.westeurope.azurecontainer.io/score'
    # Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
    #api_key = '77lvUQINoczP7IgepeQDwTnHl7HBMvsh'
    #api_key = 'vJlVyQdJfugPqbhzUyW4aLOaGwCgDfWb'
    #api_key = 'JDqh0QydJa4eA9DNsdcy6cYyrzxfrcaR'
    api_key = 'ilwVpqMh3mCtlw7DdwKcIhBElAVainZ4'
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")


    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        result = json.loads(result)
        return result
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))

def clean_results(results):
    entry = results["Results"]["WebServiceOutput0"][0]

    normalized = {key.replace("Scored Probabilities_", ""): value for key, value in entry.items() if key.startswith("Scored Probabilities_")}

    return normalized
