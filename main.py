import discord as dc
import os,requests,json,random
from dotenv import load_dotenv
from replit import db # database
from keep_alive import keep_alive

load_dotenv('the_bot.env')

''' Components '''

client = dc.Client()  # discord object to send command to                         # dc's server
sad_words = ["sad", 
"depressed", 
"unhappy", 
"miserable", 
"depressing"]

starter_encouragements = ['Cheer up!', 
"Hang in there!", 
"You are doing great! Don't worry too much",
"Nice!", 
"Neat"]

lofi_channel_id = ['UCSJ4gkVC6NrvII8umztf0Ow']
api_key = os.environ.get('API_KEY')


""" Functions """

# update and delete encouragements

if "responding" not in db.keys():
  db["responding"] = True

def update_encouragements(encouraging_message):
  if "encouragements" in db.keys():
    encouragements = db["encouragements"] # store encou in db
    encouragements.append(encouraging_message)  
    db["encouragements"] = encouragements
  else: # if encouragements are in database already
    db["encouragements"] = [encouraging_message]

def delete_encouragement(index):
  encouragements = db["encouragements"]
  if len(encouragements) > index:
    del encouragements[index]
    db["encouragements"] = encouragements # save enco to db

# update and delete music

def update_music(new_music):
  if "lofi" in db.keys():
    music = db["lofi"] # store music in db by replit
    music.append(new_music)  
    db["lofi"] = music
  else: # if encouragements are in database already
    db["lofi"] = [new_music]

def delete_music(index):  # delete elem of chosen index
  music = db["lofi"]
  if len(music) > index:
    del music[index]
    db["lofi"] = music # save enco to db


def get_quote():  # get random quote from an API
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " - " + json_data[0]['a']
  # q for quote and a for author
  return(quote)

@client.event
async def on_ready(): # bot joins server successfully
  print("Logged in as {0.user}".format(client)) # client replaces zero

@client.event
async def on_message(message):
  if message.author == client.user: # message not from the                                      bot
    return

  msg = message.content

  if message.content.startswith('$quote'):  # all commands starts with $
    quote = get_quote()
    await message.channel.send(quote)

  if db["responding"]:  # respond to sad words
    options = starter_encouragements

    if "encouragements" in db.keys():
      options = options + list(db["encouragements"])  # add enco from db

    if any(word in msg for word in sad_words):  # send random encouraging msg
      await message.channel.send(random.choice(options))

  if msg.startswith("$new"):
    encouraging_message = msg.split("$new ",1)[1]
    update_encouragements(encouraging_message)
    await message.channel.send("New encouraging message added!")

  if msg.startswith("$del"):
    encouragements = [] # return a list of encou
    if "encouragements" in db.keys():
      index = int(msg.split("$del ",1)[1])
      delete_encouragement(index)
      encouragements = db["encouragements"]     
      # get the list of all deleted encouragements
    await message.channel.send(encouragements)

  if msg.startswith("$list"): # get a list of encou
    encouragements = []
    if "encouragements" in db.keys():
      encouragements = db["encouragements"]
    await message.channel.send(encouragements)

  if msg.startswith("$responding"):   # turn on/off responding
    value = msg.split("$responding ", 1)[1]  # get the 2nd elem

    if value.lower() == "true":
      db["responding"] = True
      await message.channel.send("Responding is on! Embrace your sadness here.")

    else:
      db["responding"] = False
      await message.channel.send("Responding is off! Go home you are drunk.")



    # hmm, need a recheck: https://medium.com/pythonland/build-a-discord-bot-in-python-that-plays-music-and-send-gifs-856385e605a1
    # also: https://dev.to/mikeywastaken/events-in-discord-py-mk0

  if db["responding"]:  # respond to music selection
    music_options = lofi_channel_id

    if "lofi" in db.keys():
      music_options = music_options + list(db["lofi"])  # add music from db

  if msg.startswith("$add_song"):  # with channel URL
    new_music = msg.split("$add_song https://www.youtube.com/channel/",1)[1]
    update_music(new_music)
    await message.channel.send("New music added!")

  if msg.startswith("$less_song"):
    music = [] # return a list of encou
    if "encouragements" in db.keys():
      index = int(msg.split("$less_song https://www.youtube.com/channel/",1)[1])
      delete_music(index)
      music = db["lofi"]     
      # get the list of all deleted encouragements
    await message.channel.send(music)

  if msg.startswith("$channel_list"): # get a list of encou
    music = []
    if "lofi" in db.keys():
      music = db["lofi"]
    await message.channel.send(music)


  if message.content.startswith("$lofi"):
    random_id = random.choice(music_options)  # in the same scope so use this instead                                               of lofi_channel_id
    print(random_id)
    r = requests.get(
        'https://www.googleapis.com/youtube/v3/search?key=' + api_key + '&channelId=' + random_id
    )
    
    json_data = r.json()
    #print(json_data)  # print out a dict (clearly?)
    videoId =json_data["items"][0]["id"]["videoId"]  # gain access to an elem in json file
    await message.channel.purge(limit=1)
    await message.channel.send("Hey @everyone, listen to some lofi!\n"
                              + "https://youtu.be/" + videoId)
    print(videoId)


# running the bot

token = os.environ.get('DISCORD_BOT_SECRET')  # to protect token
keep_alive()  # run our webserver with a cloud host
client.run(token)
