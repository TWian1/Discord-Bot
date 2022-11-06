import discord, time,sys, openai, os
from dotenv import load_dotenv
from gtts import gTTS
from discord import FFmpegPCMAudio
def configure():
    load_dotenv()
configure()
Token = str(os.getenv('Discord_Key'))
global Joined
Joined = False
autosaid = False
client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    autosaid = False
    print(f'Logged in on {time.ctime(time.time())} as {client.user}')

def check(checking, message):
    try:
        for a,b in enumerate(list(checking)):
            if message[a] != b: return False
        return True
    except: return False

def checkaiimg(message):
    default_credits = 15
    user = message.author.id
    dfile = open("names.txt", "r")
    names = dfile.readlines()
    dfile.close()
    dfile = open("credits.txt", "r")
    creditslist = dfile.readlines()
    dfile.close()
    infile=False
    indexinfile = 0
    for b,a in enumerate(names):
        if a.rstrip("\n") == str(user): 
            infile = True
            indexinfile = b
            break
    if infile == False:
        dfile = open("names.txt", "w")
        newnames = names
        newnames.append(str(user) + "\n")
        dfile.writelines(newnames)
        dfile.close()
        dfile = open("credits.txt", "w")
        newcredits = creditslist
        newcredits.append(str(default_credits) + "\n")
        dfile.writelines(newcredits)
        dfile.close()
        for b,a in enumerate(names):
            if a.rstrip("\n") == str(user): 
                indexinfile = b
                break
    if int(creditslist[indexinfile].rstrip("\n")) > 0:
        dfile = open("credits.txt", "w")
        newcredits = creditslist
        newcredits[indexinfile] = str(int(creditslist[indexinfile].rstrip("\n"))-1) + "\n"
        dfile.writelines(newcredits)
        dfile.close()
        return True, int(creditslist[indexinfile].rstrip("\n"))
    else:
        return False, int(creditslist[indexinfile].rstrip("\n"))

def gpt3(input_text, temp, fpenalty, mt):
    configure()
    openai.api_key = str(os.getenv('AI_Key'))
    response = openai.Completion.create(engine="davinci-instruct-beta", prompt=input_text, temperature=temp, max_tokens=mt, top_p=1, frequency_penalty=fpenalty, presence_penalty=0)
    return response.choices[0].text
    
def imgai(prompt, size):
    openai.api_key = str(os.getenv('AI_Key'))
    response = openai.Image.create(prompt=prompt, n=1, size=size)
    image_url = response['data'][0]['url']
    return image_url

def Message_Function(message, admin, me, Admins, botdm, temp, fpenalty, djs, dj):
    try:
        mes = (message.content)[1:]
        mesl = mes.lower()
        print("\nprocessing: \"" + mes + "\"")
        if check("embed", mesl):
            try:
                title, description = mes[6:].split("|")[0], mes[6:].split("|")[1]
                if title.rstrip(" ") == "" or description.rstrip(" ") == "": raise Exception
                print("\nTitle: \"" + title + "\", Description: \"" + description + "\"")
                return discord.Embed(title=title, description=description, color=0xFF5733), 1
            except:return discord.Embed(title=".embed Title | Description", description="Creates an embed", color=0xFF5733), 4
        elif check("dm", mesl):
            if len(mes[3:].rstrip(" ")) == 0: return discord.Embed(title=".dm message", description="Direct Messages you the specified message", color=0xFF5733), 4
            if botdm and message.author.id != os.getenv('Master_ID'): return [[mes[3:], str(time.ctime(time.time())) + " TWbot: " + mes[3:]], [0, os.getenv('Master_ID')]], 5
            else: return mes[3:], 2
        elif check("aitemp", mesl):
            permission = True
            if permission == True and admin == False: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
            if len(mes[7:].rstrip(" ")) == 0: return discord.Embed(title=".aitemp number", description="changes the temperature of the ai(how random it is) between 0 and 1", color=0xFF5733), 4
            else:
                data_file = open("data.txt", "r")
                old_lines = data_file.readlines()
                data_file.close()
                counter = 0
                index = 0
                for ind,k in enumerate(old_lines):
                    if k[0] == "#": continue
                    else: 
                        counter += 1
                        if counter == 7: index = ind
                old_lines[index] = mes[7:] + "\n"
                data_file = open("data.txt", "w")
                data_file.writelines(old_lines)
                data_file.close()
        elif check("aifpenalty", mesl):
            permission = True
            if permission == True and admin == False: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
            if len(mes[10:].rstrip(" ")) == 0: return discord.Embed(title=".aifpenalty number", description="changes the the penalty for repeating things between 0 and 2", color=0xFF5733), 4
            else:
                data_file = open("data.txt", "r")
                old_lines = data_file.readlines()
                data_file.close()
                counter = 0
                index = 0
                for ind,k in enumerate(old_lines):
                    if k[0] == "#": continue
                    else: 
                        counter += 1
                        if counter == 8: index = ind
                old_lines[index] = mes[11:] + "\n"
                data_file = open("data.txt", "w")
                data_file.writelines(old_lines)
                data_file.close()
        elif mesl == "aisettings":
            permission = True
            if permission == True and admin == False: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
            return discord.Embed(title="Ai settings", description="temperature: " + str(temp) + "\n\nfrequency penalty: " + str(fpenalty), color=0xFF5733), 4
        elif check("aiimage", mesl):
            print("hi")
            if admin == False: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
            print(mes[8:])
            if len(mes[8:].rstrip(" ")) == 0: return discord.Embed(title="Ai Image", description=".aiimage *prompt*", color=0xFF5733), 4
            checkresponse = checkaiimg(message)
            if checkresponse[0]:
                if input("approve") == "y":
                    return [imgai(mes[8:], "512x512"), "Credits Left: " + str(checkresponse[1]) + "\n"], 6
                else:
                    return discord.Embed(title="No", description="Denied", color=0xFF5733), 4
            else:
                return discord.Embed(title="No", description="Insufficient funds", color=0xFF5733), 4
            #if input("approve") == "y": 
                #return imgai(mes[8:], "512x512"), 6
        elif mesl == "checkcredits":
            default_credits = 15
            user = message.author.id
            dfile = open("names.txt", "r")
            names = dfile.readlines()
            dfile.close()
            dfile = open("credits.txt", "r")
            creditslist = dfile.readlines()
            dfile.close()
            infile=False
            indexinfile = 0
            for b,a in enumerate(names):
                if a.rstrip("\n") == str(user): 
                    infile = True
                    indexinfile = b
                    break
            if infile == False: return discord.Embed(title="You Have " + str(default_credits) + " credits left.", color=0xFF5733), 4
            else: return discord.Embed(title="You Have " + creditslist[indexinfile].rstrip("\n") + " credits left.", color=0xFF5733), 4 
        elif check("ai ", mesl):
            permission = True
            if permission == True and admin == False: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
            if len(mes[3:].rstrip(" ")) == 0: return discord.Embed(title=".ai input", description="Returns an ai generated message based off of the input", color=0xFF5733), 4
            else: 
                ai_out = gpt3(mes[3:], temp, fpenalty, 300)
                print(len(ai_out))
                return ai_out, 3
        elif check("add", mesl):
            try:
                if check("credits", mesl[4:]):
                    if admin:
                        if len(mesl[12:]) == 0: return discord.Embed(title="Add credits", description=".add credits *credits* *user*", color=0xFF5733), 4
                        else:
                            newmesss = mesl[12:].split(" <@")
                            print("user: " + newmesss[1].rstrip(">"))
                            print("credits: " + newmesss[0])
                            user = int(newmesss[1].rstrip(">"))
                            dfile = open("names.txt", "r")
                            names = dfile.readlines()
                            dfile.close()
                            dfile = open("credits.txt", "r")
                            creditslist = dfile.readlines()
                            dfile.close()
                            infile=False
                            indexinfile = 0
                            for b,a in enumerate(names):
                                if a.rstrip("\n") == str(user): 
                                    infile = True
                                    indexinfile = b
                                    break
                            if infile:
                                dfile = open("credits.txt", "w")
                                newcredits = creditslist
                                newcredits[indexinfile] = str(int(creditslist[indexinfile].rstrip("\n")) + int(newmesss[0])) + "\n"
                                dfile.writelines(newcredits)
                                dfile.close()
                                return discord.Embed(title="Credits Updated", description="Previous balance: " + str(int(creditslist[indexinfile].rstrip("\n"))-int(newmesss[0])) + "\nCurrent balance: " + creditslist[indexinfile].rstrip("\n"), color=0xFF5733), 4
                            else: return discord.Embed(title="Error", description="Hasn't been used yet", color=0xFF5733), 4
                    else: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
                elif check("admin", mesl[4:]):
                    if me:
                        user = int(mes[12:].rstrip(">"))
                        data_file = open("data.txt", "r")
                        old_lines = data_file.readlines()
                        data_file.close()
                        counter = 0
                        index = 0
                        for ind,k in enumerate(old_lines):
                            if k[0] == "#": continue
                            else: 
                                counter += 1
                                if counter == 1: index = ind
                        old_lines[index] = old_lines[index].rstrip("\n") + "," + str(user) + "\n"
                        data_file = open("data.txt", "w")
                        data_file.writelines(old_lines)
                        data_file.close()
                        return discord.Embed(title="Admins Updated", description=(client.get_user(user).name + "#" + client.get_user(user).discriminator) + " is now a Admin", color=0xFF5733), 4
                    else: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
                elif check("dj", mesl[4:]):
                    if admin:
                        user = int(mes[9:].rstrip(">"))
                        data_file = open("data.txt", "r")
                        old_lines = data_file.readlines()
                        data_file.close()
                        counter = 0
                        index = 0
                        for ind,k in enumerate(old_lines):
                            if k[0] == "#": continue
                            else: 
                                counter += 1
                                if counter == 9: index = ind
                        old_lines[index] = old_lines[index].rstrip("\n") + "," + str(user) + "\n"
                        data_file = open("data.txt", "w")
                        data_file.writelines(old_lines)
                        data_file.close()
                        return discord.Embed(title="DJs Updated", description=(client.get_user(user).name + "#" + client.get_user(user).discriminator) + " is now a DJ", color=0xFF5733), 4
                    else: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
                else: return discord.Embed(title=".add", description="\"admin\" adds an admin\n\"dj\" adds a DJ\n\"credits\" adds credits to specified user", color=0xFF5733), 4
            except: return discord.Embed(title=".add", description="\"admin\" adds an admin\n\"dj\" adds a DJ", color=0xFF5733), 4
        elif check ("remove", mesl):
            if check("credits", mesl[7:]):
                if admin:
                    if len(mesl[15:]) == 0: return discord.Embed(title="Remove credits", description=".remove credits *credits* *user*", color=0xFF5733), 4
                    else:
                        newmesss = mesl[15:].split(" <@")
                        print("user: " + newmesss[1].rstrip(">"))
                        print("credits: " + newmesss[0])
                        user = int(newmesss[1].rstrip(">"))
                        dfile = open("names.txt", "r")
                        names = dfile.readlines()
                        dfile.close()
                        dfile = open("credits.txt", "r")
                        creditslist = dfile.readlines()
                        dfile.close()
                        infile=False
                        indexinfile = 0
                        for b,a in enumerate(names):
                            if a.rstrip("\n") == str(user): 
                                infile = True
                                indexinfile = b
                                break
                        if infile:
                            toremove = int(newmesss[0])
                            if int(creditslist[indexinfile].rstrip("\n")) - toremove < 0: toremove = int(creditslist[indexinfile].rstrip("\n"))
                            dfile = open("credits.txt", "w")
                            newcredits = creditslist
                            newcredits[indexinfile] = str(int(creditslist[indexinfile].rstrip("\n")) - toremove) + "\n"
                            dfile.writelines(newcredits)
                            dfile.close()
                            return discord.Embed(title="Credits Updated", description="Previous balance: " + str(int(creditslist[indexinfile].rstrip("\n"))+toremove) + "\nCurrent balance: " + creditslist[indexinfile].rstrip("\n"), color=0xFF5733), 4
                        else: return discord.Embed(title="Error", description="Hasn't been used yet", color=0xFF5733), 4
                else: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
            if check("admin", mesl[7:]):
                if me:
                    user = int(mes[15:].rstrip(">"))
                    data_file = open("data.txt", "r")
                    old_lines = data_file.readlines()
                    data_file.close()
                    counter = 0
                    index = 0
                    for ind,k in enumerate(old_lines):
                        if k[0] == "#": continue
                        else: 
                            counter += 1
                            if counter == 1: index = ind
                    old_lines[index] = "".join(old_lines[index].split("," + str(user)))
                    data_file = open("data.txt", "w")
                    data_file.writelines(old_lines)
                    data_file.close()
                    return discord.Embed(title="Admins Updated", description=(client.get_user(user).name + "#" + client.get_user(user).discriminator) + " is now not an admin", color=0xFF5733), 4
                else: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
            elif check("dj", mesl[7:]):
                if admin:
                    user = int(mes[12:].rstrip(">"))
                    data_file = open("data.txt", "r")
                    old_lines = data_file.readlines()
                    data_file.close()
                    counter = 0
                    index = 0
                    for ind,k in enumerate(old_lines):
                        if k[0] == "#": continue
                        else: 
                            counter += 1
                            if counter == 9: index = ind
                    old_lines[index] = "".join(old_lines[index].split("," + str(user)))
                    data_file = open("data.txt", "w")
                    data_file.writelines(old_lines)
                    data_file.close()
                    return discord.Embed(title="DJS Updated", description=(client.get_user(user).name + "#" + client.get_user(user).discriminator) + " is now not a DJ", color=0xFF5733), 4
                else: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
            else: return discord.Embed(title=".remove", description="\"admin\" removes an admin\n\"dj\" removes a DJ\n\"credits\" removes credits from specified user", color=0xFF5733), 4
            
        elif mesl == "listadmins":
            out = ""
            for b,a in enumerate(Admins):
                if b != 0: out += ", " 
                out += client.get_user(a).name + "#" + client.get_user(a).discriminator
            return discord.Embed(title="Admins", description=out, color=0xFF5733), 4
        elif mesl == "listdjs":
            out = ""
            for b,a in enumerate(djs):
                if b != 0: out += ", " 
                out += client.get_user(a).name + "#" + client.get_user(a).discriminator
            return discord.Embed(title="DJ's", description=out, color=0xFF5733), 4
        elif mesl == "help": 
            if not(admin):
                if dj: return discord.Embed(title="Help", description="**prefix: .**\n\n**Commands:**\nlistadmins - Lists all the admins.\nlistdjs - Lists al the DJ's\nembed - Creates a custom embed.(.embed for more info)\ndm - Direct messages you something\n\n**DJ Commands:**\nDirect message the bot .help for more info\n\n\n*Created by TWIan#9259 on 10/09/22*", color=0xFF5733), 4
                else: return discord.Embed(title="Help", description="**prefix: .**\n\n**Commands:**\nlistadmins - Lists all the admins.\nlistdjs - Lists al the DJ's\nembed - Creates a custom embed.(.embed for more info)\ndm - Direct messages you something\n\n\n*Created by TWIan#9259 on 10/09/22*", color=0xFF5733), 4
            else:
                if dj:return discord.Embed(title="Help", description="**prefix: .**\n\n**Commands:**\nlistadmins - Lists all the admins.\nlistdjs - Lists al the DJ's\nembed - Creates a custom embed.(.embed for more info)\ndm - Direct messages you something\n\n**DJ Commands:**\nDirect message the bot .help for more info\n\n**Admin Commands:** \nai - Gives an ai generated response to the prompt\nailast - Generates ai over the last specified messages\naitemp - Modifies the ai temperature(randomness)(0-1)\naifpenalty - Modifies the penalty for the ai for repeating thins(0-2)\naisettings - Check current ai settings\nadd - Adds permisions(.add for more info)\nremove - Removes permisions(.remove for more info)\n\n\n*Created by TWIan#9259 on 10/09/22*", color=0xFF5733), 4
                else: return discord.Embed(title="Help", description="**prefix: .**\n\n**Commands:**\nlistadmins - Lists all the admins.\nlistdjs - Lists al the DJ's\nembed - Creates a custom embed.(.embed for more info)\ndm - Direct messages you something\n\n**Admin Commands:** \nai - Gives an ai generated response to the prompt\nailast - Generates ai over the last specified messages\naitemp - Modifies the ai temperature(randomness)(0-1)\naifpenalty - Modifies the penalty for the ai for repeating thins(0-2)\naisettings - Check current ai settings\nadd - Adds permisions(.add for more info)\nremove - Removes permisions(.remove for more info)\n\n\n*Created by TWIan#9259 on 10/09/22*", color=0xFF5733), 4
                
        '''
        elif mes == "retro":
            diff= 1728435600-round(time.time())
            timeso = [31536000, 2628000, 86400, 3600, 60, 1]
            times = [math.floor(diff/x) for x in timeso]
            s = ["s", "s", "s", "s", "s", "s"]
            if times[0] == 1: s[0] = ""
            if times[1] - times[0]12 == 1: s[1] = ""
            if math.floor(times[2]-(times[0]365)) == 1: s[2] = ""
            if math.floor(times[3] - times[2]24) == 1: s[3] = ""
            if math.floor(times[4] - times[3]60) == 1: s[4] = ""
            if math.floor(times[5]- times[4]60) == 1: s[5] = ""
            return f"{times[0]} year{s[0]}, {times[1] - times[0]12} month{s[1]}, {times[2]-(times[0]365)} day{s[2]}, {times[3] - times[2]24} hour{s[3]}, {times[4] - times[3]60} minute{s[4]}, and {times[5]- times[4]60} second{s[5]}.", 0'''
    except Exception as error:
        print("\nCommand Error")
        print(error)
        print(str(sys.exc_info()[2].tb_lineno) + "\n")
        return ("Command Error: " + str(error)), -1
    return 0, -2
        
@client.event
async def on_message(message):
    print(message.content)
    data_file = open("data.txt", "r")
    data = data_file.readlines()
    counter = 0
    for a in data:
        line = a.rstrip("\n")
        if line[0] == "#": continue 
        else:
            counter += 1
            if counter == 1:
                Admins = [int(b) for b in line.split(",")]
            if counter == 2:
                Super_Admins = [int(b) for b in line.split(",")]
            if counter == 3:
                if line == "0": React_to_own = False
                else: React_to_own = True
            if counter == 4:
                if line == "0": Not_a_command = False
                else: Not_a_command = True
            if counter == 5:
                if line == "0": Bot_DM = False
                else: Bot_DM = True
            if counter == 6:
                if line == "0": DMDM = False
                else: DMDM = True
            if counter == 7:
                temp = float(line)
            if counter == 8:
                fpenalty = float(line)
            if counter == 9:
                djs = [int(b) for b in line.split(",")]
            if counter == 10:
                autos = int(line)
            if counter == 11:
                voicemess = line
    print(Admins)
    if len(client.voice_clients) == 1 and autos == 1 and message.content[0] != ".": autosaid = True
    else:autosaid = False
    print(autosaid)
    if autosaid:
        print(message.channel.id)
        if message.channel.id == int(voicemess):
            if len(message.content) < 100:
                voice = client.voice_clients[0]
                if not(voice.is_playing() or voice.is_paused()):
                    print("test")
                    messager = message.content + gpt3(message.content, temp, fpenalty, 50).rstrip("|") + "|en|true"
                    print(messager)
                    voice_client = client.voice_clients[0]
                    accent = 'it'
                    slowed = False
                    countermes = 0
                    out = ""
                    for a in messager.split("|"):
                        countermes += 1
                        if countermes == 1: out += a
                        elif countermes == 2: accent = a.rstrip(" ").lower()
                        elif countermes == 3:
                            if a.rstrip(" ").lower() == 'true': slowed = True
                    gTTS(text=out, lang=accent, slow=slowed).save("tts.mp3")
                    source = FFmpegPCMAudio('tts.mp3')
                    player = voice_client.play(source)
    data_file.close()
    Admin = False
    me = False
    dj = False
    if message.author.id in Admins: Admin = dj = True
    if message.author.id in djs: dj = True
    if message.author.id in Super_Admins: me = Admin = dj = True
    if str(message.channel) == "Direct Message with Unknown User":
        if dj and not(message.author.id == os.getenv('Discord_ID')):
            if message.content[0] == ".":

                #Master Commands
                newmes = message.content[1:]
                print("Processed " + newmes)
                if Admin:
                    if check("autosayon", newmes.lower()) and len(client.voice_clients) == 1:
                        print("file")
                        data_file = open("data.txt", "r")
                        old_lines = data_file.readlines()
                        data_file.close()
                        counter = 0
                        index = 0
                        index2 = len(old_lines)
                        for ind,k in enumerate(old_lines):
                            if k[0] == "#": continue
                            else: 
                                counter += 1
                                if counter == 10: index = ind
                                if counter == 11: index2 = ind
                        old_lines[index] = "1\n"
                        print(newmes.lower()[10:])
                        old_lines[index2] = newmes.lower()[10:]
                        data_file = open("data.txt", "w")
                        data_file.writelines(old_lines)
                        data_file.close()
                        voice_client = client.voice_clients[0]
                        gTTS(text="AUTO AI SAY ON", lang="en", slow=False).save("tts.mp3")
                        source = FFmpegPCMAudio('tts.mp3')
                        player = voice_client.play(source)
                    if check("autosayoff", newmes.lower()) and len(client.voice_clients) == 1:
                        print("file")
                        data_file = open("data.txt", "r")
                        old_lines = data_file.readlines()
                        data_file.close()
                        counter = 0
                        index = 0
                        index2 = 0
                        for ind,k in enumerate(old_lines):
                            if k[0] == "#": continue
                            else: 
                                counter += 1
                                if counter == 10: index = ind
                                if counter == 11: index2 = ind
                        old_lines[index] = "0\n"
                        old_lines[index2] = "0\n"
                        data_file = open("data.txt", "w")
                        data_file.writelines(old_lines)
                        data_file.close()
                        voice_client = client.voice_clients[0]
                        gTTS(text="AUTO AI SAY IS NOW OFF", lang="en", slow=False).save("tts.mp3")
                        source = FFmpegPCMAudio('tts.mp3')
                        player = voice_client.play(source)
                if check("join", newmes.lower()):
                    if len(newmes[5:].lower().rstrip(" ")) == 0: 
                        await message.reply(embed=discord.Embed(title=".join", description="format: .join voice-channel-id\n\nexample: .join 298105398793827985\n\n\n\n  TO FIND THE VOICE CHANNEL ID turn on discord developer mode.  LOOK UP HOW TO!!! and then right click on the desired voice channel and at the bottom of the popup should be something saying copy id.", color=0xFF5733))
                        return 0
                    if len(client.voice_clients) == 0:
                        ch_id = int(newmes[5:]) 
                        print(ch_id)
                        await client.get_channel(ch_id).connect()
                        Joined = True
                        await message.reply(embed=discord.Embed(title="Voice channel Joined", description=".join\n.leave\n.say\n.pause\n.unpause\n.play", color=0xFF5733))
                    else:message.reply(embed=discord.Embed(title="Already in voice channel", color=0xFF5733))
                if newmes.lower() == "leave":
                    if len(client.voice_clients) == 1:
                        await client.voice_clients[0].disconnect()
                        await message.reply(embed=discord.Embed(title="Voice channel left", color=0xFF5733))
                    else: await message.reply(embed=discord.Embed(title="Not in A voice Channel", color=0xFF5733))
                if newmes.lower() == "help": await message.reply(embed=discord.Embed(title="DJ Commands", description="\n**Prefix: .**\n\n**Commands**\njoin - joins the specified voice channel(do .join for more info)\n.leave - leaves the voice channel\n.say - using tts says the message(.say for more info)\n.pause - pauses the audio\n.unpause - unpauses the audio\n.play - CURRENTLY NOT IMPLEMENTED", color=0xFF5733))
                if check("say", newmes.lower()):
                    if len(newmes[4:].lower().rstrip(" ")) == 0: 
                        await message.reply(embed=discord.Embed(title=".say", description="format: .say message|language|slow\n\nexample: .say hello there|it|true\n\n some languages work some don't but most common ones do.  Not all options are required but they do have to be in order.\n\n .say hello there   WORKS\n.say hello there|en    WORKS\n.say hello there|true DOESN'T WORK", color=0xFF5733))
                        return 0
                    if len(client.voice_clients) == 1:
                        voice = client.voice_clients[0]
                        if not(voice.is_playing() or voice.is_paused()):
                            voice_client = client.voice_clients[0]
                            messager = str(newmes[4:]) 
                            accent = 'it'
                            slowed = False
                            countermes = 0
                            out = ""
                            for a in messager.split("|"):
                                countermes += 1
                                if countermes == 1: out += a
                                elif countermes == 2: accent = a.rstrip(" ").lower()
                                elif countermes == 3:
                                    if a.rstrip(" ").lower() == 'true': slowed = True
                            gTTS(text=out, lang=accent, slow=slowed).save("tts.mp3")
                            source = FFmpegPCMAudio('tts.mp3')
                            player = voice_client.play(source)
                        
                    else: await message.reply(embed=discord.Embed(title="Not in A voice Channel", color=0xFF5733))
                if check("play", newmes.lower()):
                    if len(newmes[5:].lower().rstrip(" ")) == 0: return 0 
                    if len(client.voice_clients) == 1:
                        voice = client.voice_clients[0]
                        if not(voice.is_playing() or voice.is_paused()):
                            messager = str(newmes[5:]) 
                            voice_client = client.voice_clients[0]
                            source = FFmpegPCMAudio(messager)
                            player = voice_client.play(source)
                    else: await message.reply(embed=discord.Embed(title="Not in A voice Channel", color=0xFF5733))
                if newmes.lower() == "pause":
                    if len(client.voice_clients) == 1:
                        voice = client.voice_clients[0]
                        if voice.is_playing():
                            voice.pause()
                    else: await message.reply(embed=discord.Embed(title="Not in A voice Channel", color=0xFF5733))
                if newmes.lower() == "unpause":
                    if len(client.voice_clients) == 1:
                        voice = client.voice_clients[0]
                        if voice.is_paused():
                            voice.resume()
                    else: await message.reply(embed=discord.Embed(title="Not in A voice Channel", color=0xFF5733))
                if newmes.lower() == "stop":
                    if len(client.voice_clients) == 1:
                        voice = client.voice_clients[0]
                        voice.stop()
                    else: await message.reply(embed=discord.Embed(title="Not in A voice Channel", color=0xFF5733))

        if str(message.author.name) != "TWIan" and str(message.author.name) != "TWbot" and DMDM:
            print("\n" + str(time.ctime(time.time())) + "  " + str(message.author.name) + ": " + str(message.content))
            user = client.get_user(os.getenv('Master_ID'))
            await user.send("\n" + str(time.ctime(time.time())) + "  " + str(message.author.name) + ": " + str(message.content))
    else:
        try:
            if message.author.id == os.getenv('Discord_ID') and React_to_own == False: return 0
            if len(message.content) == 0: return 0
            if message.content[0] == ".":
                try:
                    if check("ailast", message.content[1:].lower()):
                        permission = True
                        if permission == True and Admin == False: 
                            await message.reply(embed=discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733))
                            return 0
                        if len(message.content[7:].rstrip(" ")) == 0: await message.reply(embed=discord.Embed(title=".ailast number", description="Creates an ai message based on the last number of messages", color=0xFF5733))
                        else:
                            try:
                                numberai = int(message.content[7:].rstrip(" "))
                                if numberai > 10 or numberai < 1: raise Exception
                                newout = ""
                                counters = 0
                                for j in [i async for i in message.channel.history(limit=100)]:
                                    if counters >= numberai: break
                                    if len(j.content.rstrip(" ")) == 0:continue
                                    if j.content[0] != "." and j.author.id != os.getenv('Discord_ID'): 
                                        counters += 1
                                        if len(newout) == 0:newout += j.content
                                        else: newout += "\n" + j.content
                                print(len(newout))
                                if len(newout) > 300: raise Exception
                                await message.reply(gpt3(newout, temp, fpenalty, 300))
                            except: await message.reply(embed=discord.Embed(title="Error", description="you must input a number between 1 and 10 and message lengths must be under 300 characters", color=0xFF5733))
                    else:
                        # out_types
                        # -2 Not a command
                        # -1 Error print
                        # 0 Print
                        # 1 Embed
                        # 2 Direct message author
                        # 3 Print reply
                        # 4 Embed reply
                        # 5 Specific direct message(can be multiple)
                        # 6 link embed
                        out, out_type = Message_Function(message, Admin, me, Admins, Bot_DM, temp, fpenalty, djs, dj)
                        if out_type == 0: await message.channel.send(out)
                        elif out_type == 1: await message.channel.send(embed=out)
                        elif out_type == 2: await message.author.send(out)
                        elif out_type == 3: await message.reply(out)
                        elif out_type == 4: await message.reply(embed=out)
                        elif out_type == 5:
                            for b,a in enumerate(out[1]):
                                if a == 0: user = message.author
                                else: user = client.get_user(a)
                                if type(out[0]) == str:
                                    print("str")
                                    await user.send(out[0]) 
                                else:
                                    await user.send(out[0][b]) 
                        elif out_type == 6:
                            embed=discord.Embed(title=out[1] + message.content[9:], color=0xFF5733)
                            embed.set_image(url=out[0])
                            await message.reply(embed=embed)
                        elif out_type == -1: await message.channel.send(out)
                        elif out_type == -2: 
                            print("No Command Found")
                            if Not_a_command: await message.channel.send("Not A Command <@" + str(message.author.id) + ">")
                            else: return 0
                except Exception as error: 
                    await message.channel.send("Command Out Error: " + str(error))
                    print("\nCommand Out Error")
                    print(error)
                    print(str(sys.exc_info()[2].tb_lineno) + "\n")
        except:
            await message.channel.send("Main Error: " + str(error))
            print("\nMain Error")
            print(error)
            print(str(sys.exc_info()[2].tb_lineno) + "\n")
client.run(Token)
