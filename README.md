# How to run the code
1. Create a folder named 'chatbot'.
2. Open the 'chatbot' folder with VS Code.
3. Open the terminal in VS Code and select the Command Prompt.
4. Create and activate a Python virtual environment with the following commands:
   >To create the environment: "python -m venv myEnv"     
   >To activate the environment: "myEnv\Scripts\activate"
5. With the virtual environment activated, run all subsequent commands in the same terminal.
6. Download all the files from your GitHub repository into the 'chatbot' folder.
7. In the terminal, run the command "pip install -r requirements.txt" to install all necessary 
   packages.
8. Finally, run the command "streamlit run app.py" to launch the Streamlit app in your browser 
   using the localhost URL (replace 'app.py' with the name of your Python file if different).
   

Note: I have provided my API keys in the .env file.                                                                                                                                                                    
In case you got API key error while running the app you can create your own api key and use it in place of mine in the .env file.                                                                                     
# To create Groq API key    
1. Go to "https://console.groq.com/playground"
2. SignUp or Login with you email id (if required).
3. In the right side select model name 'Llama3-8b-8192'.
4. Then in the left side click on API keys.
5. Next click on the button 'create api key'. Now enter the name of the key and your API key is generated.
6. Copy the API key and paste into the .env file in front of the variable name GROQ_API_KEY.

# To create Google API key
1. Go to "https://aistudio.google.com/app/apikey"
2. Signin or signUp with your mail id (if required).
3. Dialog box will open. Click on 'Get API key'.
4. Then Click on 'Create API key'.
5. Again dialog box will pop up. Click on 'Create API key in new project'.
6. Your API key will be generated.
7. Copy the API key and paste into the .env file in front of the variable name GOOGLE_API_KEY.





