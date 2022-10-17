import requests
from datetime import datetime, timedelta
import time

dtformat = '%Y-%m-%dT%H:%M:%SZ'

class Convo_grabber():

    def __init__(self, bearer_key, start_date, end_date, BASE_URL, EXTENDED_URL, query='klimaatverandering', lag=1):

        self.bearer_key =bearer_key
        self.ultimate_start_date = self.get_strptime(start_date)
        self.ultimate_end_date = self.get_strptime(end_date)
        self.keyword = f'lang:nl {query}'
        self.lag = lag

        self.query_params = {
                'query': self.keyword,
                'max_results': '100' }

        self.delta = self.get_delta().days
    
        self.end_time = ( datetime.strptime(self.ultimate_end_date, dtformat) - timedelta(_) for _ in range(0,self.delta) )

        first_start = ( datetime.strptime(self.ultimate_end_date, dtformat) - timedelta(lag) ) # for the startdates, start at -1
        self.start_time = ( first_start - timedelta(_) for _ in range(0,self.delta) )

        self.url = f'{BASE_URL}{EXTENDED_URL}'


    def get_strptime(self, date):
        '''takes date (str) and returns dt formats that can be used to query the Twitter API date 
        should be in the format: yyyy-m-d e.g., 2022-9-30'''

        return datetime.strptime(f"{date.split('-')[0]}-{date.split('-')[1]}-{date.split('-')[2]}T00:00:00Z", dtformat).strftime(dtformat)

    def get_start_date(end_time, lags=1):
        '''takes end_time (str) in format: yyyy-m-d e.g., 2022-9-30
        returns the start_date in strptime format at lag length  '''

        start_date = datetime.strptime(end_time, dtformat) - timedelta(lags)
        
        return start_date.strftime(dtformat)

    def get_delta(self):
        
        return datetime.strptime(self.ultimate_end_date, dtformat)- datetime.strptime(self.ultimate_start_date, dtformat)

    def make_request(self):
        #print(self.query_params)
        time.sleep(3)
        response = requests.get(self.url,  headers={"Authorization": f"Bearer {self.bearer_key}", "User-Agent" : "v2FullArchiveSearchPython"}, params = self.query_params)
        print(f"response status: {response.status_code}")
        return response.json()

    def get_conv_within_timeframe(self):

        print(f"start time: {self.query_params['start_time']}")
        print(f"end time: {self.query_params['end_time']}")
        data = self.make_request()

        try: 
            conv_ids = [e['conversation_id'] for e in data['data']]
        
            while "next_token" in data['meta']:
                self.query_params['next_token'] = data['meta']['next_token']
                data = self.make_request()
                print("making a new request...\n")
                conv_ids.extend([e['conversation_id'] for e in data['data']])

        except:
            print(f"the keys 'data' and 'meta' are not present:********\n\n{data}\n\n\**********")
            conv_ids = []

        return conv_ids

    def get_conversation_ids(self):
        results = []
        for s, e in zip(self.start_time, self.end_time):

            self.query_params['start_time'] =  s.strftime(dtformat)
            self.query_params['end_time'] =  e.strftime(dtformat)

            self.make_request()
    
            results.append({"start_time": s,
                          "end_time" : e , 
                          "conversation_ids": self.get_conv_within_timeframe() })

        return results