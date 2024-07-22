# How to run the code
1. Create a folder (named chatbot)say.
2. Open it with vs code.
3. Open the terminal and select the command prompt.
4.  Then create and activate the Python virtual environment.
5.  Write commands to create environment variable "python -m venv myEnv"
6.  To activate environment variable "mymyEnv\Scripts\activate"                                                                                                                                                     
   Now our myEnv named virtual Environment folder will be created.
   Further, run all the commands in that terminal that has activated virtual environment.
7. Now down all the files from my GitHub in your folder(chatbot) and save them.
8. Run  the command "pip install -r requirements.txt" in your terminal. To download all the 
   requirements.
9. Finally, run the command "streamlit run app.py". (app.py is the name of Python file)
   It will open the Streamlit app  in the browser with the localhost URL.

Note: I have provided my API keys in the .env file.                                                                                                                                                                    
In case you got API key error you can create your own api key and use it in place of mine in the .env file.
# To create groq API key
1. Go to "https://console.groq.com/playground"
2. SignUp or Login with you email id.
3. In the right side select model name 'Llama3-8b-8192'.
4. Then in the left side click on API keys.
5. Next click on the button 'create api key'. Now enter the name of the key and your API key is generated.
6. Copy the API key and paste into the .env file in front of the variable name GROQ_API_KEY.

# To create google API key




