import requests
import pandas as pd
import numpy as np


def get_vacancy(skills, pages=100):
    res = []
    for indx, skill in enumerate(skills):
        print(f'collecting <{skill}> ({indx+1} of {len(skills)})')
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


skill_list = ['machine AND learning', 'data AND science', 'NLP',
              'spark', 'hadoop', 'pandas', 'dask', 'deep AND learning', 'pytorch',
              'tensorflow', 'keras', 'ai AND developer', 'computer AND vision',
              'нейронные AND сети', 'big AND data']

df = pd.DataFrame(get_vacancy(skill_list))

df = df[['id', 'name', 'salary', 'schedule', 'accept_temporary', 'area', 'published_at']]


df["city"] = (df["area"]
                     .apply(lambda x: x.get("name")
                                      if isinstance(x, dict)
                                      else np.nan))
df["schedule"] = (df["schedule"]
                     .apply(lambda x: x.get("id")
                                      if isinstance(x, dict)
                                      else np.nan))
df["salary_from"] = (df["salary"]
                     .apply(lambda x: x.get("from")
                                      if isinstance(x, dict)
                                      else np.nan))
df["salary_to"] = (df["salary"]
                     .apply(lambda x: x.get("to")
                                      if isinstance(x, dict)
                                      else np.nan))
df["salary_currency"] = (df["salary"]
                     .apply(lambda x: x.get("currency")
                                      if isinstance(x, dict)
                                      else np.nan))

df = df[df['salary_currency'] == 'RUR']
df = df.drop(['salary', 'area'], axis=1)
df = df.drop_duplicates()
df['salary_from'] = df['salary_from'].fillna(df['salary_to'])
df['salary_to'] = df['salary_to'].fillna(df['salary_from'])
df = df.dropna(subset=['salary_from', 'salary_to'])
df['salary_mean'] = round((df['salary_from'] + df['salary_to']) / 2)
df = df.drop(['salary_currency', 'salary_from', 'salary_to'], axis=1)

features = {
    'skills': [],
    'experience': [],
    'professional roles': [],
    'employer': [],
    'employer trusted': [],
    'url': [],
}
print('skill parcing...')

all_skills = []

for indx, id in enumerate(df['id']):
    req = requests.get(f'https://api.hh.ru/vacancies/{id}').json()
    skills = [skill['name'] for skill in req['key_skills']]
    features['skills'].append(skills)
    all_skills.extend(skills)
    features['experience'].append(req['experience']['name'])
    features['professional roles'].append(req['professional_roles'][0]['name'])
    features['employer'].append(req['employer']['name'])
    features['employer trusted'].append(req['employer']['trusted'])
    features['url'].append(req['alternate_url'])
    if indx == 100:
        print(f'skill parcing: {(indx+1) * 100/len(df):.0f}% comleted')

df['skills'] = features['skills']
df['experience'] = features['experience']
df['professional roles'] = features['professional roles']
df['employer'] = features['employer']
df['employer trusted'] = features['employer trusted']
df['url'] = features['url']

print(df.info())

df.to_csv('data.csv', index=False)
