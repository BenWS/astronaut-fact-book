# TODO: 12-05-2024-22-58-15

import pandas as pd
from pandas import DataFrame, Series
import json

def get_time_in_space(astronaut_record):
  if len(astronaut_record[1].get('time_in_space')) == 0:
    return None
  else:
    return astronaut_record[1].get('time_in_space')[0].get('time_in_space')

with open('astronaut_fact_book.json') as file:
  astronaut_fact_book_raw = file.read()
  astronaut_fact_book = json.loads(astronaut_fact_book_raw)
  astronaut_list = list(astronaut_fact_book.items())
  astronaut_records = [
    {
      'id':astronaut[0],
      'first_name':astronaut[1].get('person')[0].get('first_name'),
      'last_name':astronaut[1].get('person')[0].get('last_name'),
      'title':astronaut[1].get('person')[0].get('title'),
      'title_2':astronaut[1].get('person')[0].get('title2'),
      'title_3':astronaut[1].get('person')[0].get('title3'),
      'institution':astronaut[1].get('person')[0].get('organization'),
      'birth_date':astronaut[1].get('birth_life')[0].get('birth_date'),
      'birth_city':astronaut[1].get('birth_life')[0].get('birth_city'),
      'hometown':astronaut[1].get('birth_life')[0].get('hometown'),
      'time_in_space':get_time_in_space(astronaut)
     } for astronaut in astronaut_list
    ]
  astronaut_dataframe = DataFrame.from_records(astronaut_records)

  astronaut_education_records = []
  for astronaut_record in astronaut_list:
    education_records = astronaut_record[1].get('education')
    print(education_records)
    for education_record in education_records:
      astronaut_id = astronaut_record[0]
      degree = education_record.get('degree')
      specialization = education_record.get('specialization')
      school = education_record.get('school')
      education_record = {'astronaut_id':astronaut_id,'degree':degree,'specialization':specialization,'school':school}
      astronaut_education_records.append(education_record)
  
  education_dataframe = DataFrame.from_records(astronaut_education_records)

  astronaut_mission_records = []
  for astronaut_record in astronaut_list:
    mission_records = astronaut_record[1].get('missions')
    for mission_record in mission_records:
      astronaut_id = astronaut_record[0]
      name = mission_record.get('mission_name')
      vehicle = mission_record.get('vehicle')
      date = mission_record.get('mission_date')
      astronaut_mission_records.append({'astronaut_id':astronaut_id,'mission_name':name,'date':date,'vehicle':vehicle})

  astronaut_mission_dataframe = DataFrame.from_records(astronaut_mission_records)
  print(astronaut_mission_dataframe)