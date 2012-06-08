from datetime import timedelta, date, datetime
import time
from lxml import etree


class Schedule():

	shifts = {}
	shift_times = []

	#timestring = "2005-09-01 12:30:09"
	shift_duration = 3 # Shift duration in hours
	time_format = "%Y-%m-%d %H:%M:%S"
	start_time = datetime.strptime('2012-08-31 08:00:00', time_format)
	end_time = datetime.strptime('2012-09-04 17:00:00', time_format)

	def create(self):
		# Format is role - > (start,end,importance,heads)
		f = open("emf.xml",'r')
		xml = f.read()
		f.close()
		root = etree.fromstring(xml)

		for role in root.iter("role"):
			name = role.find("name")
			
			if name.text is not None:
				self.shifts[name.text] = []

				for duration in role.iter("duration"):
					start = duration.find("start").text
					end = duration.find("end").text

					start = datetime.fromtimestamp(time.mktime(time.strptime(start, self.time_format)))
					end = datetime.fromtimestamp(time.mktime(time.strptime(end, self.time_format)))

					importance = duration.find("importance")
					heads = duration.find("heads")

					self.shifts[name.text].append( (start,end, int(importance.text,10), int(heads.text,10)) )

		self.createShiftTimes()

	def numberOfShifts(self,role,ratings=[1,2,3]):
		delta = 0
		for shift in self.shifts[role]:
			if shift[2] in ratings:
				s = shift[0] # start
				e = shift[1] # end
				h = shift[3] # number of people
				d = e - s

				delta += ((abs(d.days) * 3600 * 24) + d.seconds) * h
		
		full_shifts = delta / (self.shift_duration * 3600)
		if delta % (self.shift_duration * 3600) > 0:
			full_shifts += 1

		return full_shifts


	def createShiftTimes(self):
		num_shifts = self.shiftRange()
		self.shift_times = []
		delta_time = timedelta(seconds=self.shift_duration * 3600)

		for i in range(0,num_shifts):
			self.shift_times.append(self.start_time + (delta_time * i) )

	def shiftRange(self, resolution= shift_duration):
		delta_time = self.end_time - self.start_time
		delta_time = ((delta_time.days * 3600 * 24) + delta_time.seconds ) / 3600
		num_shifts = delta_time / resolution
		return num_shifts

	def plotShifts(self):
		import pysvg.structure
		import pysvg.builders
		import pysvg.text

		svg_document = pysvg.structure.svg()
		shape_builder = pysvg.builders.ShapeBuilder()

		margin = 25
		row = margin

	
		for role in self.shifts:
			svg_document.addElement(pysvg.text.text(role, x = margin, y = row))
			column = 200

			start_block = self.start_time
			# Hour resolution
			resolution = timedelta(seconds=3600)
			end_block = self.start_time + resolution


			for s in range(0,self.shiftRange(resolution=1)):

				# In theory we could get overlapping shifts here :S
				onduty = False
				for shift in self.shifts[role]:					
					if start_block >= shift[0] and start_block <= shift[1]:
						onduty = True				

				if onduty:

					svg_document.addElement(shape_builder.createRect(column, row -15,
                                                 "10px", "5px",
                                                 strokewidth = 0,
                                                 stroke = "none",
                                                 fill = "rgb(255, 255, 0)"))
				else:
					svg_document.addElement(shape_builder.createRect(column, row -15,
                                                 "10px", "5px",
                                                 strokewidth = 0,
                                                 stroke = "none",
                                                 fill = "rgb(0, 0, 0)"))

				start_block += resolution
				end_block += resolution
				column += 10

			row += margin

		#print(svg_document.getXML())
		svg_document.save("emf_volunteers.svg")

	def printShifts(self):
		optimal = 0
		print self.shiftRange(), "shifts of", self.shift_duration, "hours each"
		for role in self.shifts:
			print "*", role, self.numberOfShifts(role)
			optimal = optimal + self.numberOfShifts(role)
		print "Optimal Number", optimal
		print 
		minimum = 0
		print self.shiftRange(), "shifts of", self.shift_duration, "hours each"
		for role in self.shifts:
			print "*", role, self.numberOfShifts(role,[3])
			minimum = minimum + self.numberOfShifts(role,[3])
		print "Minimal Number", minimum
	

	def foodCosts(self, people):
		return people * 5

	def tabardCosts(self, people):
		tabard_costs = people * 7
		if people >= 250:
			tabard_costs = people  * 2.5
		if people >=118:
			tabard_costs = 675
		return tabard_costs


	def printCostings(self):
		optimal = 0
		for role in self.shifts:
			optimal = optimal + self.numberOfShifts(role)
		minimum = 0
		for role in self.shifts:
			minimum = minimum + self.numberOfShifts(role,[3])

		spp = 3
		# Number of people eating - assume they do 3 shifts each
		# Tabards - Assume they get to keep if they do 3 shifts or more

		print "Optimal costs for Food", self.foodCosts(optimal / 3), "and tabards", self.tabardCosts(optimal / 3), "for", optimal / 3, "people assuming each person does",spp,"shifts" 
		print "Minimum costs for Food", self.foodCosts(minimum / 3), "and tabards", self.tabardCosts(minimum / 3), "for", minimum / 3, "people assuming each person does",spp,"shifts"

	def overlap(self, s0,e0, s1,e1):
		return (e0 >= s1 and e0 <= e1) or (s0 >= s1 and s1 <= e1)


if __name__ == "__main__":
	s = Schedule()
	s.create()
	s.printShifts()
	s.plotShifts()
	print 
	s.printCostings()
