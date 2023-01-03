import requests
import pandas as pd
import numpy as np


def get_vacancies(skills, filename, pages=10):
    res = []
    for indx, skill in enumerate(skills):
        print(f'\ncollecting <{skill}> ({indx+1} of {len(skills)})')
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
            print('|', end='')

    df = pd.DataFrame(res)

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

    df = (df[df['salary_currency'] == 'RUR']
            .drop(['salary', 'area'], axis=1)
            .drop_duplicates()
            )
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
    print('\nskill parcing...')

    all_skills = []

    for id in df['id']:
        req = requests.get(f'https://api.hh.ru/vacancies/{id}').json()
        skills = [skill['name'] for skill in req['key_skills']]
        features['skills'].append(skills)
        all_skills.extend(skills)
        features['experience'].append(req['experience']['name'])
        features['professional roles'].append(req['professional_roles'][0]['name'])
        features['employer'].append(req['employer']['name'])
        features['employer trusted'].append(req['employer']['trusted'])
        features['url'].append(req['alternate_url'])
        print('|', end='')
    print()

    df['skills'] = features['skills']
    df['experience'] = features['experience']
    df['professional roles'] = features['professional roles']
    df['employer'] = features['employer']
    df['employer trusted'] = features['employer trusted']
    df['url'] = features['url']

    print(df.info())

    df.to_csv(filename, index=False)
    print(f'data stored in file {filename}')
