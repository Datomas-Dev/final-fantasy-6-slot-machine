"""
slotmachine.py
Date: 9/23/2019
Author: David T.
	
"""

from breezypythongui import EasyFrame
from tkinter import PhotoImage
from tkinter.font import Font
import winsound, random

soundbank = { "slots":"snd/slots.wav",
              "lose":"snd/lose.wav",
              "payout":"snd/payout.wav",
              "reset":"snd/reset.wav" }

BACKGROUND_COMMON = "darkblue"
FOREGROUND_TEXT = "white"

class SlotMachine(EasyFrame):
	
	def __init__(self):
		EasyFrame.__init__(self,title = "FFVI Slot Machine", width = 400, height = 300, background = BACKGROUND_COMMON)
		self.setResizable(False)
		
		""" 
			initialize application variables
		"""
		self.fonts = { 	"title":Font(family = "Times New Roman",size = 14),
						"info":Font(family = "Verdana",size = 8, slant = "italic"),
						"score":Font(family = "Fixedsys",size = 18),
						"result":Font(family = "Fixedsys",size = 18) }
		
		self.values = [0,1,2,3,4,5,6,7,8,9]
		self.images = [PhotoImage(file = "pic/0.gif"),
		               PhotoImage(file = "pic/1.gif"),
		               PhotoImage(file = "pic/2.gif"),
		               PhotoImage(file = "pic/3.gif"),
		               PhotoImage(file = "pic/4.gif"),
		               PhotoImage(file = "pic/5.gif"),
		               PhotoImage(file = "pic/6.gif"),
		               PhotoImage(file = "pic/7.gif"),
		               PhotoImage(file = "pic/8.gif"),
		               PhotoImage(file = "pic/9.gif")]
		
		# If this is True, a decimal value will increase each time the player loses, increasing their chances of matching numbers the more they lose. Once they win, the value is reset. If False, winning will be completely random.
		self.boost = False
		self.boostBase = 0.0 # Starting chance to give the player a match
		self.boostStep = 0.0125 # Amount to increase chance of matching on each spin
		self.boostValue = self.boostBase # Actual value used to calculate a free match given to the player
		
		self.twoMult = 3.0
		self.jackpotMult = 5.0
		
		self.playerScore = 100
		self.playCost = 10
		self.lastOutcome = -1
		
		self.slotValue = [0,0,0]
		
		"""
			GUI components
		"""
		# Label setup
		self.titleLabel = self.addLabel("Final Fantasy VI Slot Machine", 0, 0, font = self.fonts["title"], background = BACKGROUND_COMMON, foreground = FOREGROUND_TEXT, sticky = "W")
		# self.infoLabel = self.addLabel("How to play:\nPlaying costs "+str(self.playCost)+" gil\nTwo-of-a-kind: Win "+str(self.twoMult)+"x\nThree-of-a-kind: Win "+str(self.jackpotMult)+"x", 1, 0, font = self.fonts["info"], background = BACKGROUND_COMMON, foreground = FOREGROUND_TEXT, sticky = "EW")
		self.infoLabel = self.addLabel("%-0s" % "How to play:\nPlaying costs "+str(self.playCost)+" gil\nTwo-of-a-kind: Win "+str(self.twoMult)+"x\nThree-of-a-kind: Win "+str(self.jackpotMult)+"x", 1, 0, font = self.fonts["info"], background = BACKGROUND_COMMON, foreground = FOREGROUND_TEXT, sticky = "EW")
		
		self.scoreLabel = self.addLabel(str(self.playerScore)+" gil", 2, 0, font = self.fonts["score"], sticky = "EW", background = BACKGROUND_COMMON, foreground = FOREGROUND_TEXT)
		
		self.slotPanel = self.addPanel(3, 0, background = BACKGROUND_COMMON)
		self.slotFrame = [self.slotPanel.addLabel("",0,0, sticky = "W"),self.slotPanel.addLabel("",0,1,sticky = "EW"),self.slotPanel.addLabel("",0,2,sticky="E")]
		self.slotFrame[0]["image"] = self.images[0]
		self.slotFrame[1]["image"] = self.images[0]
		self.slotFrame[2]["image"] = self.images[0]

		self.boostLabel = self.addLabel("Boost = ", 4, 0, font = self.fonts["info"], background = BACKGROUND_COMMON, foreground = FOREGROUND_TEXT, sticky = "EW")
		
		self.outcomeLabel = self.addLabel("Spin to Play", 5, 0, background = BACKGROUND_COMMON, foreground = FOREGROUND_TEXT, sticky = "EW")
		self.outcomeLabel["font"] = self.fonts["result"]
		
		# Buttons to spin and reset the game
		self.buttonPanel = self.addPanel(6, 0, background = BACKGROUND_COMMON)
		self.spinButton = self.buttonPanel.addButton("Spin!", 0, 0, command = self.spin)
		self.resetButton = self.buttonPanel.addButton("Reset", 0, 1, command = self.reset)

		self.updateUI()
	
	def spin(self):
		"""Spins all slots, processes the outcome and updates the UI"""
		
		self.playerScore -= self.playCost
		self.spinButton["state"] = "disabled"
		
		self.spinSlot(0)
		self.spinSlot(1)
		self.spinSlot(2)
		
		self.processOutcome()
		self.updateUI()
		
	
	def spinSlot(self,slot):
		"""Spins a single slot."""
		
		# If boosting is enabled
		if slot > 0 and self.boost:
			print("\nBoosting slot "+str(slot)+".")
			print(str(self.boostValue)+" chance.")
			chance = random.random()
			print("%2.2f" % (chance))
			if chance <= self.boostValue:
				print("Boosted match.")
				self.slotValue[slot] = self.slotValue[slot-1]
				self.slotFrame[slot]["image"] = self.slotFrame[slot-1]["image"]
				return
		
		# Randomize the slot
		index = random.randint(0,len(self.values)-1)
		self.slotValue[slot] = self.values[index]
		self.slotFrame[slot]["image"] = self.images[index]
	
	
	def spinAnimation(self):
		"""Animates the slot images"""
		pass
	
	
	def processOutcome(self):		
		matches = 0
		
		# Checks which slots match, and updates variable to keep track
		if self.slotValue[0] == self.slotValue[1]:
			matches += 1
		if self.slotValue[1] == self.slotValue[2]:
			matches += 1
		if self.slotValue[0] == self.slotValue[2]:
			matches += 1
		
		# Two of a kind
		if matches == 1:
			self.playerScore += self.playCost*self.twoMult
			self.resetBoost()
			playSound("payout")
		# Jackpot
		elif matches >= 2:
			self.playerScore += self.playCost*self.jackpotMult
			self.resetBoost()
			playSound("payout")
		# Loss
		else:
			playSound("lose")
			if self.boost:
				self.upgradeBoost()
				
		# Update variable to track outcome
		self.lastOutcome = matches
		
		# Decide if the plauer can proceed
		if self.playerScore < self.playCost:
			self.gameOver()
		else:
			self.spinButton["state"] = "normal"

	def updateUI(self):
		""" Upadates the user interface """
		self.scoreLabel["text"] = str(int(self.playerScore))+" gil"
		if self.boost:
			self.boostLabel["text"] = "Boost % = "+str("%0.2f" % ((self.boostValue/1)*100))+"%"
		else:
			self.boostLabel["text"] = ""
		
		if self.playerScore < self.playCost:
			self.outcomeLabel["text"] = "You don't have enough\nmoney to play!"
			self.outcomeLabel["foreground"] = "red"
		else:
			if self.lastOutcome < 0:
				self.outcomeLabel["text"] = "Spin to Play!"
				self.outcomeLabel["foreground"] = FOREGROUND_TEXT
			elif self.lastOutcome == 1:
				self.outcomeLabel["text"] = "Two-of-a-kind!"
				self.outcomeLabel["foreground"] = "lightgreen"
			elif self.lastOutcome >= 2:
				self.outcomeLabel["text"] = "Jackpot!"
				self.outcomeLabel["foreground"] = "yellow"
			else:
				self.outcomeLabel["text"] = "You Lose!"
				self.outcomeLabel["foreground"] = "red"
	
	def resetBoost(self):
		self.boostValue = self.boostBase
		print("Boost reset to %2.2f" % (self.boostValue))
	
	def upgradeBoost(self):
		self.boostValue += self.boostStep
		print("No win. Boost upgraded to %2.2f" % (self.boostValue))
	
	def gameOver(self):
		self.spinButton["state"] = "disabled"
	
	def reset(self):
		""" Resets all game values """
		playSound("reset")
		self.spinButton["state"] = "normal"
		self.playerScore = 100
		self.slotValue = [0,0,0]
		self.slotFrame[0]["image"] = self.images[0]
		self.slotFrame[1]["image"] = self.images[0]
		self.slotFrame[2]["image"] = self.images[0]
		self.lastOutcome = -1
		self.resetBoost()
		self.updateUI()
		
def main():
	SlotMachine().mainloop()
	
def playSound(name):
	winsound.PlaySound(soundbank[name],winsound.SND_ASYNC)
	

main()