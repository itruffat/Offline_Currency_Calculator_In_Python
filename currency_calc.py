#-*-coding:utf8;-*-
#qpy:3
#qpy:console

import os
from math import ceil
import urllib.request
import json
import time


if __name__ == "__main__":

	# TRIVIAL VARIALBES	
	clear = 'cls' if (os.name == 'nt') else 'clear'
	name_tags = {}
	suggar_names = {}
	exchange = {}
	instructions = """
	[LIST]: 	Show a list of all currencies. (requires internet)
	[ADD]: 		To add a new currency.
	[REMOVE]: 	To remove a previous currency.
	[UPDATE]: 	To get a new currency value. (requires internet)
	[CURRENCY]:	Show the exchange values with  USD.
	[CHANGE]: 	Update a exchange value manually. (against USD)
	[EXIT]: 	Allows you to save changes and quit.
	[RESET]: 	Deletes all configurations files. (in case they get bugged)
	[INSTRUCTIONS]: Shows instructions.
	[ANY LETTER EXCEPT 'K']: Change to the currency defined with that letter.
	>>> Letter 'k' is reserved and counts as '000', so 5kk is equal to 500000
	"""

	#LOAD PREVIOUS CONFIGURATIONS AND/OR DEFAULT VALUES
	if os.path.isfile("currency_calc.names"):
		with open("currency_calc.names", "r") as file_open:
			for line in file_open.readlines():
				letter, name, suggar = line.split(":")
				name_tags[letter] = name
				suggar_names[letter] = suggar
	else:
		name_tags 		= {'j': 'JPY', 		'c' : 'CAD', 	'u':'USD'}
		suggar_names 	= {'j': "Yenes(¥)",	'c':"CAD (C)",	'u':"USA(U$S)"}

	if os.path.isfile("currency_calc.rates"):
		with open("currency_calc.rates", "r") as file_open:
			for line in file_open.readlines():
				letter, value = line.split(":")
				exchange[letter] = float(value)
	else:
		exchange		= {'j': 111.079002,	'c': 1.31183,	'u': 1.0}


	#AUXILIARY FUNCITONS
	def exchangeRate(_from,_to):
		return exchange[_to]/exchange[_from]

	def getAllCurrencies():
		url = "https://free.currencyconverterapi.com/api/v5/currencies"
		return_val = []
		try:
			contents = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))["results"]
			return_val = (["{1}({0})".format(cn,contents[cn]['currencyName']) for cn in contents])
		except urllib.error.URLError:
				print("Url error, page unavaiable and/or internet is down.")
			
		return return_val


	def getExchangeRateUpdate(names):
		update_url = "http://free.currencyconverterapi.com/api/v5/convert?q={}_{}&compact=y"
		exchangeRate = {}

		for key, name in names.items():
			contents = "{}"
			found = False
			try:
				contents = urllib.request.urlopen(update_url.format("USD",name)).read().decode('utf-8')
				found = True
			except urllib.error.URLError:
				print("Url error, currency name is incorrect and/or internet is down.")

			if found:
				jsondata = json.loads(contents)
				exchangeRate[key] = float(jsondata[next(iter(jsondata))]['val'])
		
		return exchangeRate

	#MAIN
	title = "\033[4m\033[1m~~Offline Currency Calculator~~\033[0m"
	os.system(clear)
	print(title)
	print("For more instructions, write 'instructions'")
	time.sleep(1)
	os.system(clear)
	print(title)

	mode = "u"
	step = 0
	i = ""
	changed_currency_names = False
	changed_currency_values = False
	under   	= "\033[4m"
	flat 		= "\033[0m"

	
	while i != "exit" and i!='reset':
		options_list = ''.join([x for x in name_tags])
		request_str = '/'.join(["{0}{1}{2}".format(under if l == mode else flat,l.upper(),flat) for l in options_list])
		request = "[{}]>>".format(request_str)
		
		i = input(request).lower().replace("k","000")
		if step > 2:
			step = 0
			os.system(clear)
			print(title)
			print(request + i)
		step += 1 
		if i == "instructions":
			print(instructions)
		elif i == "list":
			n = 30
			clist = (getAllCurrencies())
			while len(clist) > 0:
				nlist = clist[:n]
				clist = clist[n:]
				print(", ".join(nlist))
				input("Press enter to continue")
		elif i == "exchange":
			print (exchange)
		elif i == "change":
			letter = input("Write letter: [example C for canadian Dollars]").lower()
			assert(len(letter) == 1)
			if letter in list(options_list):
				value = input("Write new value of currency vs USD: [example 1.31 for canadian Dollars]")
				exchange[letter] = float(value)
				changed_currency_values = True
		elif i == "update":
			exchange = getExchangeRateUpdate(name_tags)
			changed_currency_values = True
		elif i == "add":
			letter = input("Write letter: [example C for canadian Dollars]").lower()
			assert(len(letter) == 1)
			tag    = input("Write currency abreviation: [example CAD for Canadian Dollars]").upper()
			suggar = input("<optional> Write a name for the currency: [example Canadian for Canadian Dollars]")
			suggar = tag if suggar  == "" else suggar
			name_tags[letter] = tag
			suggar_names[letter] = suggar
			exchange = getExchangeRateUpdate(name_tags)
			changed_currency_names = True
			changed_currency_values = True
		elif i == "remove":
			if len(name_tags) < 3:
				print("Can not have less than 2 currencies")
			else:
				letter = input("Select letter to remove: (leave empty to cancel)  ").lower()
				if letter != "":
					del name_tags[letter]
					del suggar_names[letter]
					if letter == mode:
						mode = next(iter(name_tags))
					changed_currency_names = True
					changed_currency_values = True
		elif i in list(options_list):
			mode = i
		elif i.isnumeric():
			n = float(i)
			for l in options_list:
				print("{:<8}: {:.2f}".format(suggar_names[l], (n * exchangeRate(mode,l))))
			print("")
				
	if i == 'reset':
		changed_currency_names = False
		changed_currency_values = False
		if os.path.isfile("currency_calc.names"):
			os.remove("currency_calc.names") 
		if os.path.isfile("currency_calc.rates"):
			os.remove("currency_calc.rates") 
		
	if changed_currency_names or changed_currency_values:
		if input("Do you want to save changes? (Yes/No)").lower() in ["y","yes"]:
			problems = False
			
			if changed_currency_names:
				try:
					with open("currency_calc.names", "w") as file_open:
						for key,value in name_tags.items():
							print("{}:{}:{}".format(key,value, suggar_names[key]), file = file_open)
				except:
					print("CCN failure")
					problems = True 
			
			if not problems:
				try:
					with open("currency_calc.rates", "w") as file_open:
						for key,value in exchange.items():
							print("{}:{}".format(key,value), file = file_open)
					print("Changes saved")
				except:
					print("CCR failure")
					problems = True
			
			if problems:
				print("Something went wrong when storing the file(s), changes not properly saved")
				print("Hint: you may need a 'Reset'")
		else:
			print("Changes not saved")

	input("PRESS ENTER TO CLOSE")
