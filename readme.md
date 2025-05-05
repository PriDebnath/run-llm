# Ollama Chat API Script

This project demonstrates how to use the local [Ollama](https://ollama.com) API to interact with an AI model via Python. It includes instructions to install the necessary tools, download a model, and run a sample chat script.

## Step 1: Install Ollama

Download and install Ollama from the official site:

👉 [https://ollama.com/download](https://ollama.com/download)

Once installed, make sure Ollama is running,
or run by  clicking the app icon on your machine
then run

```bash
ollama run gemma3:1b  # This command downloads the gemma3:1b model if it’s not already present.

```


## Step 2: Install Packages
Install packages mentioned in project's requirements.txt file

```
  pip install -r requirements.txt
```
## Step 3: Run and Chat
#### serve frontend 
Open the directory on any browser or use *Live Server* vs code extentiion

#### serve backend 

```
python v2/chat-with-llm-v2.py
```
