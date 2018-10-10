# Work with Python 3.6
import discord
import random
import urllib.request
import sys
import json
import random

cat_cs = "https://opentdb.com/api.php?amount=11&category=18&type=multiple"
cat_all = "https://opentdb.com/api.php?amount=11&type=multiple"
cat_videogame = "https://opentdb.com/api.php?amount=11&category=15&type=multiple"
cat_sports = "https://opentdb.com/api.php?amount=11&category=21&type=multiple"
cat_movies = "https://opentdb.com/api.php?amount=11&category=11&type=multiple"
request_string = cat_all

client = discord.Client()
questions = []
curvalues = []
alltime = {}
alltimefile = "highscores.txt"
alltimeseperator = ",,,,,"
def loadalltime():
	global alltime
	filein = open(alltimefile, "r")
	for line in filein:
		name = line.split(alltimeseperator)[0]
		score = int(line.split(alltimeseperator)[1])
		alltime[name] = score		
	filein.close()
	
def savealltime():
	global alltime
	fileout = open(alltimefile, "w")
	for name in alltime:
		fileout.write(name + alltimeseperator + str(alltime[name]) + "\n")
	fileout.close()
	
async def reset():
	global questions, curquestion, scores
	fp = urllib.request.urlopen(request_string)
	mybytes = fp.read()

	mystr = mybytes.decode(sys.stdout.encoding)
	obj = json.loads(mystr)
	y = obj["results"]
	questions = []
	for question in y:
		answers = []
		numbers = []
		for a in question["incorrect_answers"]:
			answers.append(str(random.randint(10,99)) + ". " + a)
		#answers = question["incorrect_answers"]
		realanswer = str(random.randint(10,99)) + ". " + question["correct_answer"]
		realanswer = realanswer.strip()
		answers.append(realanswer)
		random.shuffle(answers)
		
		q = question["question"] + "\n"
		for i in range(len(answers)):
			answers[i] = answers[i].strip()
			q += str(answers[i]) + "\n"
		result = [q, answers]
		
		q = q.replace("&#039;", "'")
		q = q.replace('&quot;', '"')
		q = q.replace("&amp;", "&")
		q = q.replace("&ldquo;", '"')
		q = q.replace("&ldquo;", '"')
		realanswer = realanswer.replace("&#039;", "'")
		realanswer = realanswer.replace('&quot;', '"')
		realanswer = realanswer.replace("&amp;", "&")
		realanswer = realanswer.replace("&ldquo;", '"')
		realanswer = realanswer.replace("&ldquo;", '"')
		questions.append([q, realanswer, answers])
	curquestion = 0
	scores = {}
	
def gettopx(scores, x):
	result = []
	names = []
	for name in scores:
		names.append(name)
	random.shuffle(names)
		
	for i in range(x):
		topscore = -100
		topname = None
		for name in names:
			if scores[name] > topscore:
				topscore = scores[name]
				topname = name
		if topname != None:
			result.append([topname, topscore])
			names.remove(topname)
	return result
				
			
def printleaders(scores):
	top = gettopx(scores, 5)
	result = ""
	for i in range(len(top)):
		result += str(i + 1) + ". " + str(top[i][0]) + " - " + str(top[i][1]) + "\n"
	return result
	
async def nextquestion(message):
	global curquestion, questions, countguesses, curanswer, curvalues
	print(curquestion)
	curquestion += 1
	if curquestion <= len(questions):
		msg = ""
		leaders = printleaders(scores)
		if len(leaders) > 0:
			msg = "The current leaderboard is:\n" + leaders + "\n\n"
		msg += "Question #" + str(curquestion) + "/" + str(len(questions)) + "\n" + questions[curquestion-1][0]
		curanswer = questions[curquestion-1][1]
		
		curvalues = questions[curquestion-1][2]
		for i in range(len(curvalues)):
			curvalues[i] = curvalues[i][:2]
		
		print("The current answer is: " + curanswer)
		countguesses = 0
		await client.send_message(message.channel, msg)
	else:
		await endtrivia(message)

async def endtrivia(message):
	global state
	state = "off"
	msg = "The trivia has ended.\n"
	highscore = -100
	highname = "nobody."
	for name in scores:
		if scores[name] > highscore:
			highscore = scores[name]
			highname = name
	msg += "The winner of the game is " + highname
	if highscore != -100:
		msg += " with a score of " + str(highscore)
	msg += "\n\nThe final leaderboard was:\n" + printleaders(scores) + "\n\n"
	
	if highname != "nobody.":
		if highname not in alltime:
			alltime[highname] = 1
		else:
			alltime[highname] = alltime[highname] + 1
		savealltime()
	msg += "\n\nThe all time leaderboard is:\n" + printleaders(alltime) + "\n"
	
	await reset()
	await client.send_message(message.channel, msg)
	
@client.event
async def on_message(message):
	global state, questions, countguesses, alltime, request_string, curvalues
	# we do not want the bot to reply to itself
	if message.author == client.user:
		return
		
	if message.channel.name.lower() != "trivia":
		return

	'''if message.content == "Albus, tell a joke.":
		msg = "I don't joke."
		await client.send_message(message.channel, msg)
		return
	'''	
	'''if state == "off" and message.content.startswith("!addquestion"):
		pass
		if(message.content.count('"') == 3):
			temp = message.content
			startq = temp.find('"')
			temp = temp[startq+1:]
			endq = temp.find('"')
			question = temp[:endq]
			temp = temp[endq+1:]
			answer = temp[:temp.find('"')]
			questions.append([question,answer])
			print("Added question: " + question)
			print("Added answer: " + answer)
			msg = "The question was added."
			await client.send_message(message.channel, msg)
			return
		else:
			msg = 'The question format was incorrect.\nIt should be of the format: !addquestion "What is your question?"Your answer"\nNote, there are only 3 quotation marks.'
			await client.send_message(message.channel, msg)
	'''
	if message.content.startswith("!myscore"):
		name = message.author.name
		msg = ""
		if name not in alltime:
			msg = "Sorry " + name + ", you are not in my database."
		else:
			msg = name + "'s total wins: " + str(alltime[name])
		await client.send_message(message.channel, msg)
		return
		
	if message.content.startswith("!alltime"):
		msg = "\n\nThe all time leaderboard is: " + printleaders(alltime) + "\n"
		await client.send_message(message.channel, msg)
		return
	
	if state == "off" and (message.content.startswith("!starttrivia") or message.content.lower() == "ask me the questions, bridgekeeper. i am not afraid."):
		state = "on"
		await reset()
		await client.send_message(message.channel, "Let us begin then.\n")		
		await nextquestion(message)
		return
		
	if state == "off" and message.content.startswith("!setcat"):
		cat = message.content.split(" ")[1]
		msg = ""
		if cat == "cs":
			request_string = cat_cs
			msg = "Okay, Computer Science it will be."
		elif cat == "all":
			request_string = cat_all
			msg = "All things strike your fancy."
		elif cat == "games":
			request_string = cat_videogame
			msg = "Ahh, a gamer I see."
		elif cat == "sports":
			request_string = cat_sports
			msg = "Sports and recreation!"
		elif cat == "movies":
			request_string = cat_movies
			msg = "You say movies, it shall be movies."
		else:
			msg = "I'm not too sure what you mean."
		await client.send_message(message.channel, msg)
		
	if state == "on" and message.content.startswith("!endtrivia") and message.channel.name.lower() == "trivia":
		await endtrivia(message)
		return
		
	if state == "on" and message.content.startswith("!starttrivia"):
		msg = "Trivia is currently running.\n\n"
		leaders = printleaders(scores)
		if len(leaders) > 0:
			msg += "The current leaderboard is: " + leaders + "\n\n"
		msg += "Question #" + str(curquestion) + "/" + str(len(questions)) + "\n" + questions[curquestion-1][0]
		await client.send_message(message.channel, msg)
		return
		
	if state == "on" and message.channel.name.lower() == "trivia":
		print("Received message: " + message.content + ", answer is: " + curanswer)
		countguesses += 1
		if message.content[:2] == curanswer[:2] or message.content.lower() == curanswer.lower():
			print("The answer was correct")
			name = message.author.name
			if message.author.nick != None:
				name = message.author.nick
			msg = curanswer + " is correct! Congratulations " + message.author.name + "!\n\n"
			if name not in scores:
				scores[name] = 100
			else:
				scores[name] = scores[name] + 100
			await client.send_message(message.channel, msg)
			await nextquestion(message)
			return
		else:
			if message.content[:2] in curvalues:
				print("Sorry wrong answer, -50 points")
				name = message.author.name
				if message.author.nick != None:
					name = message.author.nick
				msg = message.content + " is wrong. -50 points!\n"
				if name not in scores:
					scores[name] = -50
				else:
					scores[name] = scores[name] - 50
				await client.send_message(message.channel, msg)
				return
			print(message.content[:2] + " wrong answer: " + str(curvalues))
		

@client.event
async def on_ready():
	await reset()
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
	
state = "off"
curquestion = -1
curanswer = ""
countguesses = 0
maxguesses = 20
loadalltime()
scores = {}
client.run('YOU NEED YOUR OWN BOT TOKEN FROM DISCORD')
