# -*- coding: utf-8 -*-

import urllib.request
import json
import git
import tarfile
import os


GITHUB_API_URL = 'https://api.github.com/users'
USER_NAME = 'PharbersDeveloper'
DOWNLOAD_PATH = '/Users/clock/Downloads/github'
ZIP_NAME = 'PharbersDeveloper.zip'


def get_all_public_repos(user_name, page=1):
    repos_api = 'repos'
    response = urllib.request.urlopen(f'{GITHUB_API_URL}/{user_name}/{repos_api}?page={page}')
    repos_info = json.load(response)
    repos_len = len(repos_info)

    if not repos_len:
        return []

    page_repos = [repo_info['clone_url'] for repo_info in repos_info]
    return page_repos + get_all_public_repos(user_name, page+1)


def download_repo(repo_url, download_path):
    git.Git(download_path).clone(repo_url)


def get_downloaded_repos(download_path):
    return os.listdir(download_path)


def zip_repos(zip_path, zip_name):
    with tarfile.open(zip_name, "w:gz") as tar:
        tar.add(zip_path, arcname=os.path.basename(zip_path))


if __name__ == '__main__':
    all_repos = get_all_public_repos(USER_NAME)
    downloaded_repos = get_downloaded_repos(DOWNLOAD_PATH)

    repos = [repo for repo in set(all_repos) if repo.split('/')[-1].split('.')[0] not in downloaded_repos]

    repos_count = len(repos)
    for index, repo in enumerate(set(repos)):
        print(f'下载第 {index+1}/{repos_count} 个，{repo}')
        download_repo(repo, DOWNLOAD_PATH)
    else:
        print('下载完成')

    zip_repos(DOWNLOAD_PATH, ZIP_NAME)
