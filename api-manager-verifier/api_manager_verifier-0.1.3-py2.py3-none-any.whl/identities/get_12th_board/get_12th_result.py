
from verifiers.base import BaseResposne
from verifiers.model.get_marks import GetMarksApplicant
from bs4 import BeautifulSoup
from verifiers.identities.get_12th_board import rolls
from verifiers.exceptions.exception import NotFromPCM,EmptyDataFound
import pandas as pd

class GetMarks(BaseResposne):

    '''This scraer was created on 30/08/2021, and can provide result related to 12th board exam of 2021'''

    base_url = 'https://cbseresults.nic.in/class12/Class12th21.htm'
    result_url = 'https://cbseresults.nic.in/class12/class12th21.asp'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,vi;q=0.6',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'cbseresults.nic.in',
        'Origin': 'https://cbseresults.nic.in',
        'Referer': 'https://cbseresults.nic.in/class12/Class12th21.htm',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }

    excluded_subjects = []

    def __init__(self, to_verify):
        super(GetMarks, self).__init__(to_verify)
        self.to_verify = to_verify

    def filter(self, text: str, type='int'):
        if type == 'int':
            i = text.replace('\xa0\xa0\xa0\xa0', '').strip()
            try:
                return eval(i)
            except SyntaxError:
                return eval(i[1:])
        else:
            return text.strip()

    def get_user_details(self, soup):
        tables = soup.find_all('table')[4]
        tr = tables.find_all('tr')
        return {i.find_all('td')[0].text: i.find_all('td')[1].text for i in tr}

    def get_user_marks(self, soup):
        tables = soup.find_all('table')[5]
        tr = tables.find_all('tr')[1:6]
        tr.append(tables.find_all('tr')[len(tables.find_all('tr')) - 2])

        return [{'subject_code': self.filter(i.find_all('td')[0].text),
                 'subject_name': self.filter(i.find_all('td')[1].text, 'str'),
                 'theory': self.filter(i.find_all('td')[2].text),
                 'practical': self.filter(i.find_all('td')[3].text),
                 'total': self.filter(i.find_all('td')[4].text),
                 'grade': self.filter(i.find_all('td')[5].text, 'str')} for i in tr]

    def calculate_details(self, marks: list) -> dict:
        data = dict()
        total = 0
        count=0
        sub=[]
        for i in marks:
            if i.get('subject_code') not in self.excluded_subjects:
                total += i.get('total')
                sub.append(i.get('subject_name'))
                count += 1

        data['total_marks'] = total
        data['total_subjects'] = count
        data['overall_percent'] = round((total / count), 2)
        data['subjects'] = sub
        return data

    def check_if_pcm(self,marks):
        count=0
        for i in marks:
            if i.get('subject_code') in [41,42,43]:
                count+=1

        if count==3:
            return True

        return False


    def pre_query(self):
        response = self.smart_request('GET', self.base_url, headers=self.headers)
        hidden = self.get_hidden_payload_test(response)
        return self.query_info(hidden=hidden)

    def query_info(self, **kwargs):
        hidden = kwargs.get('hidden')
        payload = {'regno': self.to_verify.roll, 'sch': self.to_verify.scl_code, 'B2': 'Submit', **hidden}
        resposne = self.smart_request('POST', self.result_url, data=payload, headers=self.headers)

        return self.extract_info(resposne)

    def extract_info(self, response):
        soup = BeautifulSoup(response.content, 'lxml')
        details = dict()

        details['details'] = self.get_user_details(soup)

        details['marks'] = self.get_user_marks(soup)

        #TODO:uncomment below when only PCM student is needed
        # if not self.check_if_pcm(details.get('marks')):
        #     raise NotFromPCM

        marks = self.calculate_details(details.get('marks'))
        details.update(marks)

        return details

    @classmethod
    def extract_data(cls, db_ob, **kwargs):
        return cls(db_ob).pre_query()

def organize_data(data:dict):
    details=dict()
    details['Roll No.']=data.get('details').get('Roll No:')
    details['Name'] = data.get('details').get('Candidate Name:')
    details['Mother Name'] = data.get('details').get("Mother's Name:")
    for i in data.get('marks'):
        details[i.get('subject_name')] = i.get('total')

    details['Total marks Obtained']=data.get('total_marks')
    details['Total Subjects']=data.get('total_subjects')
    details['Subjects %age calculated']=', '.join(i for i in data.get('subjects'))
    details['%age']=data.get('overall_percent')

    return details


def test():
    applicant = GetMarksApplicant()
    applicant.roll = '14634373'
    applicant.scl_code = '29025'
    return GetMarks.extract_data(applicant)

    # roll = rolls()
    # final_df=[]
    # for i in roll:
    #     print('checking for {} ...'.format(i))
    #     applicant.roll = i.strip()
    #     applicant.scl_code = '29025'
    #     try:
    #         data = GetMarks.extract_data(applicant)
    #         data=organize_data(data)
    #         final_df.append(data)
    #     except (NotFromPCM, IndexError):
    #         continue
    # df = pd.DataFrame(final_df)
    #
    # if df.empty:
    #     raise EmptyDataFound
    #
    # df=df.sort_values(by=['%age'], ascending=False)
    # df=df.reset_index(drop=True)
    # df=df[['Roll No.','Name','Mother Name','ENGLISH CORE','PHYSICS','CHEMISTRY','MATHEMATICS','COMPUTER SCIENCE (NEW)','HINDI CORE',
    #        'Total Subjects','Subjects %age calculated','Total marks Obtained','%age']]
    #
    # df.to_excel('pcm_rank.xlsx')


if __name__ == '__main__':
    print(test())
