from openai import OpenAI
#from speech_translate import speech_translate
#import LLMBOT_Database
import pandas as pd
import csv
import time

client = OpenAI(api_key = "sk-proj-DPLwNxhwl6k0AxioGNN0T3BlbkFJR6HxqbMg6DjZwk9vLnbX")
#class basicCommands():
    #def moveLeft(self, object):
class Generation:
    def __init__(self):
        pass
    def subCommand_Generation(self, string, csv_file):
        df = pd.read_csv(csv_file)
        self.summary = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert psuedocoder, who is good at taking human commands, and breaking into simpler subtask commands"},
                {"role": "user", "content": f"You are given this string: {string}. Now, convert this into a series of simple commands." 
                 f"Every letter of the command should be capitalized, and spaces should be replaced with underscores. Keep commands simple and short(max 3 words)"
                 f"Here is some further context for example commands: {df["Command"]}"
                 "You do not need to only use example commands - but if there is a command in the dataframe that you want to use, use the exact command name without changes"
                 "Return at max 10 commands - do not feel the need to use all ten command slots"
                 "Only output the commands separated by a comma and without spaces. - do not include quotes in the commands"}
            ] 
            )
        return self.summary.choices[0].message.content.strip().split(',')
    def command_to_code(self, command, csv_file, bad_code):
        df = pd.read_csv(csv_file)
        self.summary = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert coder, who is good at taking human commands, and turning these commands into python code"},
                {"role": "user", "content": f"You are given this command: {command}. Now, convert this into a python code." 
                 f"Here is some further context for example commands and their associated code: {df}"
                 f"Here is some code that was rejected(bad code) for said command{bad_code} - do not return this code"
                 "Only output implementation code. "
                 "Do not include programming language in output"}
            ] 
            )
        return self.summary.choices[0].message.content.strip().replace("python","")
    def checkGen(self, command, new_code):
        user_input = input(f"Is this code good: {new_code} for the command {command}\n")
        if (user_input == "yes"):
            return True, new_code
        else:
            return False
class Retrieval:
    def commandRetrieval(self, command, csv_file):
        df = pd.read_csv(csv_file)
        #for command in df["Command"]:
            #print(command)
        if command in df["Command"]:
            return df[command]
        else:
            #print(f"{command} not in f{df["Command"]}")
            return None
def Runner(source_file, action):
    df = pd.read_csv(source_file)
    genInstance = Generation()
    retInstance = Retrieval()
    commandSteps = genInstance.subCommand_Generation(action, source_file)
    print(f"these are the generated command steps: {commandSteps}")
    #for command in commandSteps:
        #print(command)
    #print("done")
    i = 0
    for command in commandSteps:
        #print(command)
        #retrieval = retInstance.commandRetrieval(command, source_file)
        if(command not in df["Command"].values):
            #print(df["Command"].to_numpy())
            generate = True
            new_code = None
            while(generate):
                #if no retrieval generate new code
                new_code = genInstance.command_to_code(command, source_file, new_code)
                if(genInstance.checkGen(command, new_code)):
                    #csv database file input
                    with open(source_file, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        row = command, new_code
                        writer.writerow(row)
                    #list replace command with code
                    commandSteps[i] = new_code
                    #end loop
                    generate = False
                else:
                    #if bad generation, go back to start of loop and repeat
                    pass
            
        else:
            #if retrieval found, set input
            commandSteps[i] = df.loc[df["Command"] == command, "Code"]
            #commandSteps[i] = retrieval.strip()
        i += 1
    #print(commandSteps)


Runner("Command_Database - Sheet1.csv", "Move forward, turn right, then turn in place in a circle")