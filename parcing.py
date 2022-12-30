import requests
from tqdm.notebook import tqdm
import pandas as pd

res = []


def get_vacancy(skills, pages=100):
    for skill in tqdm(skills):
        print(f'collecting <{skill}>')
        for page in tqdm(range(pages)):
            params = {
                'text': f'{skill}',
                'page': page,
                'per_page': 100,
                'only_with_salary': 'true',
            }
            req = requests.get('https://api.hh.ru/vacancies', params).json()
            if 'items' in req.keys():
                res.extend(req['items'])


skill_list = ['machine AND learning', 'data AND science', 'sql', 'NLP',
              'spark', 'hadoop', 'pandas', 'dask', 'deep AND learning', 'pytorch',
              'tensorflow', 'keras', 'ai AND developer', 'computer AND vision',
              'нейронные AND сети', 'big AND data']
get_vacancy(skill_list)

data = pd.DataFrame(res)

data.to_csv('data.csv', index=False)