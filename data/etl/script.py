# standard library modules
import os
import re
import json
import hashlib

# pyInquirer for semi-automatic parsing interpretation
from PyInquirer import prompt


class Logger:
	'''
	Manages writes to the output log
	'''
	def __init__(self):
		self._log_list = []


	def persist_log(self):
		file_path = 'log.txt'
		with open(file_path,encoding='utf-8',mode='w+') as file:
			for item in self._log_list:
					file.write(str(item) + '\n')
		pass

	def log(self,input_record):
		'''
		Log Output
		'''
		self._log_list.append(input_record)

# main functions
def is_major_bullet(text):
	return text.lower().startswith('-')
	
def refresh_screen():
	print('\n'*100,sep='')

# match functions
def parse_line(file_string):
	'''
	Attempts to match the input string against match string(s) and returns matched groups.

	Returns a dictionary, adhering to a standard format for the given key.
	'''
	while True:
		# load regex configurations from file
		config_file_path = r'parsing_config.json'
		with open(config_file_path,encoding='utf-8') as file:
			config_file_string = file.read()


		config_dict = json.loads(config_file_string)
		match_list = []

		for match_category,matchers in config_dict.items():
			for matcher in matchers:
				try:
					match_group = re.match(matcher['regex'],file_string)
				except:
					print('Regular expression syntax error - please adjust in config file and retry')
					continue
				if match_group is None:
						continue
				else:
						# further processing for producing final dictionary
						match_dict = {}
						for key_name,match_index in zip(matcher['keys'],range(len(match_group.groups()))):
							match_dict[key_name] = match_group.group(match_index + 1)

						match_list.append({'match_category':match_category,'match_dict':match_dict})		
		
		questions = {
			'type':'list',
			'name':'parsing_result',
			'message':'Which result?',
			'choices': list(set([json.dumps(match) for match in match_list])) + ['Retry','Skip']
		}

		refresh_screen()
		print(file_string)
		selections = prompt(questions)

		selection = selections['parsing_result']
		if selection =='Skip':
			return None
		elif selection != 'Retry':
			return json.loads(selection)
		else:
			continue

# miscellaneous functions 
def load_database(source_database,database_type='list'):
	'''
	Read from parsed string results into program memory
	'''
	file_path = f'{source_database}.json'
	with open(file_path,encoding='utf-8',mode='r+') as file:
		if database_type == 'list':
			database_raw = file.read()
			database_empty = []
			if database_raw == '': # if database is empty string
				file.write('[]')
				return database_empty
		if database_type == 'dictionary':
			database_raw = file.read()
			database_empty = {}
			if database_raw == '': # if database is empty string
				file.write('{}')
				return database_empty
		return json.loads(database_raw) # if else, assume that the database file is in JSON format and can be represented as dictionary data structure

def write_record(target_database,record):
	'''
	Write parsed string results in memory to database
	'''
	file_path = f'{target_database}.json'
	with open(file_path, encoding='utf-8', mode='r+') as file:
		database = load_database(target_database)
		database.append(record)
		return file.write(json.dumps(database))


def update_record(target_database,record):
	file_path = f'{target_database}.json'
	database = load_database(target_database,database_type='dictionary')
	database.update(record)
	with open(file_path, encoding='utf-8', mode='w') as file:
			return file.write(json.dumps(database))

def record_exists(target_database,record):
	file_path = f'{target_database}.json'
	with open(file_path,encoding='utf-8',mode='r+') as file:
			database = load_database(target_database,database_type='dictionary')
			return list(record.keys())[0] in database

def process_file(logger):
	'''
	Reads the raw file and produces nested results
	'''
	# read file
	file_path = r'../raw/biographies.txt'
	lines_read_limit = None
	limit_exceeded = False

	current_record = {} # the current record to-be-appended to the final output
	output = [] # the final results 
	parsed_blocks = set(load_database('parsed_lines'))
	
	
	with open(file_path,encoding='utf-8') as file:
	
		line_list =	file.readlines()

		# first assume match isn't found 
		count_lines_read = 0
		initial_record = False
			
		for index,current_line in enumerate(line_list):
			if is_major_bullet(current_line):
				
				# previous parse 'block' processing
				initial_record = (index == 0)
				if not initial_record and not block_processed:
						update_record('astronaut_fact_book',current_record) # record record even if it was not fully processed
						if block_fully_processed:
								write_record('parsed_lines',block_id)	# record that current block has been processed
				
				# compute block ID and set initial variables
				block_fully_processed = True # assume that block will be fully processed until proven otherwise
				major_bullet_string = current_line
				md5_hash = hashlib.md5()
				md5_hash.update(major_bullet_string.encode('utf-8'))
				block_id = md5_hash.hexdigest()
				block_processed = block_id in parsed_blocks
				current_record = {block_id:{}}
				
				if not block_processed:
					match = parse_line(current_line)
					
					#initialize nested dictionaries
					current_record[block_id]['education'] = []
					current_record[block_id]['missions'] = []
					current_record[block_id]['time_in_space'] = []
					current_record[block_id]['spacewalks'] = []
					current_record[block_id]['birth_life'] = []
					current_record[block_id]['person'] = []

					if match is not None:
						match_category = match['match_category']
						match_dict = match['match_dict']
						if match_category == 'person':
							current_record[block_id]['person'].append(match_dict)
					
					elif match is None:
							block_fully_processed = False
			
			elif not is_major_bullet(current_line):
				
				if not block_processed:
					# run through all the string matching scenarios
					match = parse_line(current_line)
					if match is not None:
						match_category = match['match_category']
						match_dict = match['match_dict']
						logger.log({'Education Match':current_line})
						if match_category == 'education':
							current_record[block_id]['education'].append(match_dict)
						if match_category == 'missions':
								current_record[block_id]['missions'].append(match_dict)
						if match_category == 'time_in_space':
								current_record[block_id]['time_in_space'].append(match_dict)
						if match_category == 'spacewalks':
								current_record[block_id]['spacewalks'].append(match_dict)
						if match_category == 'birth_life':
								current_record[block_id]['birth_life'].append(match_dict)
						if match_category == 'person':
								current_record[block_id]['person'].append(match_dict)
					elif match is None:
						block_fully_processed = False
					
					count_lines_read += 1
					# check if limit of lines read has been exceeded
					if lines_read_limit is not None:
						limit_exceeded = (count_lines_read > lines_read_limit)
						if limit_exceeded:
							return output
					else:
						limit_exceeded = False
		
		return output
			

	
if __name__ == '__main__':

	logger = Logger()
	output = process_file(logger=logger)
	logger.persist_log()