import requests
import pandas as pd


def get_vacancy(skills, pages=100):
    res = []
    for skill in skills:
        print(f'collecting <{skill}>')
        for page in range(pages):
            params = {
                'text': f'{skill}',
                'page': page,
                'per_page': 100,
                'only_with_salary': 'true',
            }
            req = requests.get('https://api.hh.ru/vacancies', params).json()
            if 'items' in req.keys():
                res.extend(req['items'])
    return res


skill_list = ['machine AND learning', 'data AND science', 'sql', 'NLP',
              'spark', 'hadoop', 'pandas', 'dask', 'deep AND learning', 'pytorch',
              'tensorflow', 'keras', 'ai AND developer', 'computer AND vision',
              'нейронные AND сети', 'big AND data']

data = pd.DataFrame(get_vacancy(skill_list))

data.to_csv('data.csv', index=False)
