import discord, time,sys, openai, os
from dotenv import load_dotenv
from pytube import YouTube, Search
from gtts import gTTS
from discord import FFmpegPCMAudio
def configure():
    load_dotenv()
configure()
Token = str(os.getenv('Discord_Key'))
autosaid = False
client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    autosaid = False
    writinglines("queue.txt", [])
    print(f'Logged in on {time.ctime(time.time())} as {client.user}')

@client.event
async def on_voice_state_update(member, before, after):
    try:
        vclient = client.voice_clients[0]
        if len(vclient.channel.members) == 1: 
            await vclient.disconnect()
            print("Disconnecting") 
    except:pass

def getvcsearch(id, client):
    guilds = client.guilds
    for a in guilds:
        for b in a.members:
            if id == b.id:
                try: 
                    return str(b.voice.channel.id), True
                    gid = a.id
                except: pass
    return 0, False
def check(checking, message):
    try:
        for a,b in enumerate(list(checking)):
            if message[a] != b: return False
        return True
    except: return False
def readinglines(file):
    ab = open(file, "r")
    a = ab.readlines()
    ab.close()
    return a
def writinglines(file, content):
    ab = open(file, "w")
    ab.writelines(content)
    ab.close()
def check_queue():
    print("checking")
    lines = readinglines("queue.txt")
    newlist = []
    for a in lines:
        try: 
            if a[0:8] == "https://":
                newlist.append(a)
        except:pass
    if len(newlist) != 0:
        yt = YouTube(newlist.pop(0))
        wlist = []
        for a in newlist:
            wlist.append(a + "\n")
        writinglines("queue.txt", wlist)
        if yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().filesize <= 150000000:
            yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()                  
            for o in os.listdir():
                if o == "yt.mp3": os.remove("yt.mp3")
            for o in os.listdir():
                if o[-3:] == "mp4": os.rename(o, "yt.mp3")
            source = FFmpegPCMAudio("yt.mp3")
        else:
            gTTS(text="File Too Big", lang="en", slow=False).save("tts.mp3")
            source = FFmpegPCMAudio('tts.mp3')
        return source     
def voice_queue(vc):
    lines = readinglines("queue.txt")
    if len(lines) == 0:
        return 0
    source = check_queue()
    vc.play(source, after=lambda x=None: voice_queue(vc))
def checkaiimg(message):
    default_credits = 15
    user = message.author.id
    names = readinglines("names.txt")
    creditslist = readinglines("credits.txt")
    infile=False
    indexinfile = 0
    for b,a in enumerate(names):
        if a.rstrip("\n") == str(user): 
            infile = True
            indexinfile = b
            break
    if infile == False:
        newnames = names
        newnames.append(str(user) + "\n")
        writinglines("names.txt", newnames)
        newcredits = creditslist
        newcredits.append(str(default_credits) + "\n")
        writinglines("credits.txt", newcredits)
        for b,a in enumerate(names):
            if a.rstrip("\n") == str(user): 
                indexinfile = b
                break
    if int(creditslist[indexinfile].rstrip("\n")) > 0:
        newcredits = creditslist
        newcredits[indexinfile] = str(int(creditslist[indexinfile].rstrip("\n"))-1) + "\n"
        writinglines("credits.txt", newcredits)
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
                old_lines = readinglines("data.txt")
                counter = 0
                index = 0
                for ind,k in enumerate(old_lines):
                    if k[0] == "#": continue
                    else: 
                        counter += 1
                        if counter == 7: index = ind
                old_lines[index] = mes[7:] + "\n"
                writinglines("data.txt", old_lines)
        elif check("aifpenalty", mesl):
            permission = True
            if permission == True and admin == False: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
            if len(mes[10:].rstrip(" ")) == 0: return discord.Embed(title=".aifpenalty number", description="changes the the penalty for repeating things between 0 and 2", color=0xFF5733), 4
            else:
                old_lines = readinglines("data.txt")
                counter = 0
                index = 0
                for ind,k in enumerate(old_lines):
                    if k[0] == "#": continue
                    else: 
                        counter += 1
                        if counter == 8: index = ind
                old_lines[index] = mes[11:] + "\n"
                writinglines("data.txt", old_lines)
        elif mesl == "aisettings":
            permission = True
            if permission == True and admin == False: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
            return discord.Embed(title="Ai settings", description="temperature: " + str(temp) + "\n\nfrequency penalty: " + str(fpenalty), color=0xFF5733), 4
        elif check("aiimage", mesl):
            if False: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
            print(mes[8:])
            if len(mes[8:].rstrip(" ")) == 0: return discord.Embed(title="Ai Image", description=".aiimage *prompt*", color=0xFF5733), 4
            checkresponse = checkaiimg(message)
            if checkresponse[0]:
                if me:
                    return [imgai(mes[8:], "512x512"), "Credits Left: " + str(checkresponse[1]) + "\n"], 6
                else:
                    verification = True
                    if verification == False: return discord.Embed(title="No", description="Verification is off so this can't be processed", color=0xFF5733), 4
                    if input("approve") == "y":
                        return [imgai(mes[8:], "512x512"), "Credits Left: " + str(checkresponse[1]) + "\n"], 6
                    else:
                        return discord.Embed(title="No", description="Denied", color=0xFF5733), 4
            else:
                return discord.Embed(title="No", description="Insufficient funds", color=0xFF5733), 4
        elif mesl == "checkcredits":
            default_credits = 15
            user = message.author.id
            names = readinglines("names.txt")
            creditslist = readinglines("credits.txt")
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
            permission = False
            if permission == True and admin == False: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
            if len(mes[3:].rstrip(" ")) == 0: return discord.Embed(title=".ai input", description="Returns an ai generated message based off of the input", color=0xFF5733), 4
            else: 
                ai_out = gpt3(mes[3:], temp, fpenalty, 300)
                return ai_out, 3
        elif check("add", mesl):
            try:
                if check("credits", mesl[4:]):
                    if admin:
                        if len(mesl[12:]) == 0: return discord.Embed(title="Add credits", description=".add credits *credits* *user*", color=0xFF5733), 4
                        else:
                            newmesss = mesl[12:].split(" <@")
                            user = int(newmesss[1].rstrip(">"))
                            names = readinglines("names.txt")
                            creditslist = readinglines("credits.txt")
                            infile=False
                            indexinfile = 0
                            for b,a in enumerate(names):
                                if a.rstrip("\n") == str(user): 
                                    infile = True
                                    indexinfile = b
                                    break
                            if infile:
                                newcredits = creditslist
                                newcredits[indexinfile] = str(int(creditslist[indexinfile].rstrip("\n")) + int(newmesss[0])) + "\n"
                                writinglines("credits.txt", newcredits)
                                return discord.Embed(title="Credits Updated", description="Previous balance: " + str(int(creditslist[indexinfile].rstrip("\n"))-int(newmesss[0])) + "\nCurrent balance: " + creditslist[indexinfile].rstrip("\n"), color=0xFF5733), 4
                            else: return discord.Embed(title="Error", description="Hasn't been used yet", color=0xFF5733), 4
                    else: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
                elif check("admin", mesl[4:]):
                    if me:
                        user = int(mes[12:].rstrip(">"))
                        old_lines = readinglines("data.txt")
                        counter = 0
                        index = 0
                        for ind,k in enumerate(old_lines):
                            if k[0] == "#": continue
                            else: 
                                counter += 1
                                if counter == 1: index = ind
                        old_lines[index] = old_lines[index].rstrip("\n") + "," + str(user) + "\n"
                        writinglines("data.txt", old_lines)
                        return discord.Embed(title="Admins Updated", description=(client.get_user(user).name + "#" + client.get_user(user).discriminator) + " is now a Admin", color=0xFF5733), 4
                    else: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
                elif check("dj", mesl[4:]):
                    if admin:
                        user = int(mes[9:].rstrip(">"))
                        old_lines = readinglines("data.txt")
                        counter = 0
                        index = 0
                        for ind,k in enumerate(old_lines):
                            if k[0] == "#": continue
                            else: 
                                counter += 1
                                if counter == 9: index = ind
                        old_lines[index] = old_lines[index].rstrip("\n") + "," + str(user) + "\n"
                        writinglines("data.txt", old_lines)
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
                        user = int(newmesss[1].rstrip(">"))
                        names = readinglines("names.txt")
                        creditslist = readinglines("credits.txt")
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
                    old_lines = readinglines("data.txt")
                    counter = 0
                    index = 0
                    for ind,k in enumerate(old_lines):
                        if k[0] == "#": continue
                        else: 
                            counter += 1
                            if counter == 1: index = ind
                    old_lines[index] = "".join(old_lines[index].split("," + str(user)))
                    writinglines("data.txt", old_lines)
                    return discord.Embed(title="Admins Updated", description=(client.get_user(user).name + "#" + client.get_user(user).discriminator) + " is now not an admin", color=0xFF5733), 4
                else: return discord.Embed(title="No", description="Insuffecient Permissions", color=0xFF5733), 4
            elif check("dj", mesl[7:]):
                if admin:
                    user = int(mes[12:].rstrip(">"))
                    old_lines = readinglines("data.txt")
                    counter = 0
                    index = 0
                    for ind,k in enumerate(old_lines):
                        if k[0] == "#": continue
                        else: 
                            counter += 1
                            if counter == 9: index = ind
                    old_lines[index] = "".join(old_lines[index].split("," + str(user)))
                    writinglines("data.txt", old_lines)
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
    if len(client.voice_clients) == 1 and autos == 1 and message.content[0] != ".": autosaid = True
    else:autosaid = False
    if autosaid:
        print(message.channel.id)
        if message.channel.id == int(voicemess):
            if len(message.content) < 100:
                voice = client.voice_clients[0]
                if not(voice.is_playing() or voice.is_paused()):
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
            if len(message.content) == 0: return 0
            if message.content[0] == ".":
                newmes = message.content[1:]
                print("Processed " + newmes)
                if len(client.voice_clients) == 1:voice = client.voice_clients[0]
                if Admin:
                    if check("autosayon", newmes.lower()) and len(client.voice_clients) == 1:
                        old_lines = readinglines("data.txt")
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
                        writinglines("data.txt", old_lines)
                        voice_client = client.voice_clients[0]
                        gTTS(text="AUTO AI SAY ON", lang="en", slow=False).save("tts.mp3")
                        source = FFmpegPCMAudio('tts.mp3')
                        player = voice.play(source)
                    if check("autosayoff", newmes.lower()) and len(client.voice_clients) == 1:
                        old_lines = readinglines("data.txt")
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
                        writinglines("data.txt", old_lines)
                        gTTS(text="AUTO AI SAY IS NOW OFF", lang="en", slow=False).save("tts.mp3")
                        source = FFmpegPCMAudio('tts.mp3')
                        player = voice.play(source)
                if check("join", newmes.lower()):
                    mestoid = newmes[5:]
                    if len(newmes[5:].lower().rstrip(" ")) == 0: 
                        h = message.author.id
                        outv = getvcsearch(h, client)
                        if outv[1] == False:
                            await message.reply(embed=discord.Embed(title="Not in a voice channel", description="Join a voice channel for the bot to join", color=0xFF5733))
                            return 0
                        else: mestoid = outv[0]
                    if len(client.voice_clients) == 0:
                        ch_id = int(mestoid) 
                        print(ch_id)
                        if len(client.get_channel(ch_id).members) >= 1: 
                            await client.get_channel(ch_id).connect()
                            await message.reply(embed=discord.Embed(title="Voice channel Joined", description=".join\n.leave\n.say\n.pause\n.unpause\n.play", color=0xFF5733))
                        else:
                            await message.reply(embed=discord.Embed(title="No one in voice channel", description="someone needs to be in the channel to connect", color=0xFF5733))
                    else:message.reply(embed=discord.Embed(title="Already in voice channel", color=0xFF5733))
                if newmes.lower() == "leave":
                    if len(client.voice_clients) == 1:
                        await client.voice_clients[0].disconnect()
                        await message.reply(embed=discord.Embed(title="Voice channel left", color=0xFF5733))
                        writinglines("queue.txt", [])
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
                        writinglines("data.txt", old_lines)
                    else: await message.reply(embed=discord.Embed(title="Not in A voice Channel", color=0xFF5733))
                if newmes.lower() == "help": await message.reply(embed=discord.Embed(title="DJ Commands", description="\n**Prefix: .**\n\n**Commands**\njoin - joins the specified voice channel(do .join for more info)\n.leave - leaves the voice channel\n.say - using tts says the message(.say for more info)\n.pause - pauses the audio\n.unpause - unpauses the audio\n.play - CURRENTLY NOT IMPLEMENTED", color=0xFF5733))
                if check("say", newmes.lower()):
                    if len(newmes[4:].lower().rstrip(" ")) == 0: 
                        await message.reply(embed=discord.Embed(title=".say", description="format: .say message|language|slow\n\nexample: .say hello there|it|true\n\n some languages work some don't but most common ones do.  Not all options are required but they do have to be in order.\n\n .say hello there   WORKS\n.say hello there|en    WORKS\n.say hello there|true DOESN'T WORK", color=0xFF5733))
                        return 0
                    if len(client.voice_clients) == 1:
                        if not(voice.is_playing() or voice.is_paused()):
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
                            player = voice.play(source)     
                    else: await message.reply(embed=discord.Embed(title="Not in A voice Channel", color=0xFF5733))
                if check("play", newmes.lower()):
                    if len(newmes[5:].lower().rstrip(" ")) == 0: return 0 
                    if len(client.voice_clients) == 1:
                        messager = str(newmes[5:]) 
                        if not(voice.is_playing() or voice.is_paused()):
                            print(messager[0:7])
                            if messager[0:8] != "https://":
                                messager = str(Search(messager).results[0].watch_url)
                                await message.reply("Playing: " + messager)
                            voice_client = client.voice_clients[0]
                            m = await message.reply(embed=discord.Embed(title="Downloading", color=0xFF5733))
                            btime = time.time()
                            yt = YouTube(messager)
                            print(yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().filesize)
                            if yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().filesize <= 150000000:
                                yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
                                for o in os.listdir():
                                    if o == "yt.mp3":
                                        os.remove("yt.mp3")
                                for o in os.listdir():
                                    if o[-3:] == "mp4":
                                        os.rename(o, "yt.mp3")
                                source = FFmpegPCMAudio("yt.mp3")
                            else:
                                gTTS(text="File Too Big", lang="en", slow=False).save("tts.mp3")
                                source = FFmpegPCMAudio('tts.mp3')
                            atime = time.time()
                            try:
                                player = voice_client.play(source, after=lambda x=None: voice_queue(voice_client))
                                await m.edit(embed=discord.Embed(title="Finished and Playing, time to download: " + str(round(atime-btime)) + " Seconds", color=0xFF5733))
                            except: await m.edit(embed=discord.Embed(title="Download error or someone else was already downloading", color=0xFF5733))
                        else:
                            linkmes = True
                            if messager[0:8] != "https://": 
                                print("searched")
                                linkmes = False
                                messager = str(Search(messager).results[0].watch_url)
                            ab = open("queue.txt", "a")
                            ab.write(messager+"\n")
                            ab.close()
                            ab = open("queue.txt", "r")
                            await message.reply(embed=discord.Embed(title="Added to queue", description="Position: " + str(len(ab.readlines())), color=0xFF5733))
                            if linkmes == False: await message.reply(messager)
                            ab.close()
                    else: await message.reply(embed=discord.Embed(title="Not in A voice Channel", color=0xFF5733))
                if newmes.lower() == "pause":
                    if len(client.voice_clients) == 1:
                        if voice.is_playing(): voice.pause()
                    else: await message.reply(embed=discord.Embed(title="Not in A voice Channel", color=0xFF5733))
                if newmes.lower() == "unpause":
                    if len(client.voice_clients) == 1:
                        if voice.is_paused():voice.resume()
                    else: await message.reply(embed=discord.Embed(title="Not in A voice Channel", color=0xFF5733))
                if newmes.lower() == "skip":
                    voice.stop()
                    voice_queue(voice)
                    await message.reply(embed=discord.Embed(title="Skipped", color=0xFF5733))
                if newmes.lower() == "queue":
                    ab = open("queue.txt", "r")
                    lines = ab.readlines()
                    ab.close()
                    if len(lines) == 0: await message.reply(embed=discord.Embed(title="No Queue", color=0xFF5733))
                    else:
                        out = ""
                        for b,c in enumerate(lines):
                            title = str(YouTube(c.rstrip("\n")).streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().title)
                            if b == 0: out += str(b+1) + ". " + title
                            else: out += "\n" + str(b+1) + ". " + title
                        await message.reply(embed=discord.Embed(title="Queue", description=out, color=0xFF5733))
                if newmes.lower() == "stop":
                    if len(client.voice_clients) == 1:
                        voice.stop()
                        writinglines("queue.txt", [])
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
                            if type(out[0]) == str: await user.send(out[0]) 
                            else: await user.send(out[0][b]) 
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
                    await message.channel.send("Command Out Error")
                    print("\nCommand Out Error\n" + str(error) + "\n" + str(sys.exc_info()[2].tb_lineno) + "\n")
        except:
            await message.channel.send("Main Error")
            print("\nMain Error\n" + str(error) + "\n" + str(sys.exc_info()[2].tb_lineno) + "\n")
client.run(Token)
