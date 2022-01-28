#!/usr/bin/python3.6
from typing import List, Optional, cast, Dict
import gitlab
import os
import sys
import json

from gitlab.v4.objects.projects import ProjectMergeRequestManager, Project
from gitlab.v4.objects.merge_requests import ProjectMergeRequestManager, ProjectMergeRequest

PROJECT_ID = os.environ.get('GITLAB_PROJECT_ID')
GITLAB_URL = os.environ.get('GITLAB_URL')
GITLAB_TOKEN = os.environ.get('GITLAB_TOKEN')

script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
COMMIT_MR_FILE = f'{script_dir}/commit_mr.json'


def get_gitlab_instance() -> gitlab.Gitlab:
    return gitlab.Gitlab(url=GITLAB_URL, private_token=GITLAB_TOKEN)


def get_main_project(gl: gitlab.Gitlab, project_id: str) -> Project:
    return gl.projects.get(project_id)


def get_project_mr_manager(project: Project) -> ProjectMergeRequestManager:
    return project.mergerequests


def list_mr(mr_manager: ProjectMergeRequestManager, page: int = 1) -> List[ProjectMergeRequest]:
    return cast(List[ProjectMergeRequest],
                mr_manager.list(page=page, per_page=20, scope='all', order_by='created_at', sort='desc'))


def create_mr_commit_table(mr_manager: ProjectMergeRequestManager) -> Dict[str, str]:
    ''' Generate a commit -> MR url dict'''
    max_page = 60
    print('Fetching merge requests')
    commit_mr = {}
    for page in range(1, max_page):
        # let's show the user some progress
        print(f'Page: {page}/{max_page}')
        mrs = list_mr(mr_manager, page)
        for mr in mrs:
            for commit in mr.commits():
                commit_id = commit.get_id()
                if commit_id is not None:
                    commit_mr[commit_id] = mr._attrs['web_url']
    return commit_mr


def get_mr_by_commit_sha(mr_manager: ProjectMergeRequestManager, commit_id: str) -> Optional[ProjectMergeRequest]:
    max_page = 15
    for page in range(1, max_page):
        mrs = list_mr(mr_manager, page)
        for mr in mrs:
            for commit in mr.commits():
                if commit.get_id() == commit_id:
                    return mr
    return None


def find_mr_url_by_commit(commit_id: str):
    gl = get_gitlab_instance()
    project = get_main_project(gl, PROJECT_ID)
    mr_manager = get_project_mr_manager(project)
    mrs: List[ProjectMergeRequest] = []
    try:
        commit_mr_file = open(COMMIT_MR_FILE, 'r')
        commit_mr: Dict[str, str] = json.loads(commit_mr_file.read())
        mr_url = commit_mr.get(commit_id)
        if mr_url is not None:
            print(mr_url)
        else:
            print(f'No matching MR found for {commit_id}')
    except IOError:
        should_generate_table = input(
            'No commit -> mr table file found. This greatly improves efficiency by caching the requests. Generate one now? [y/n]'
        )
        if should_generate_table == 'y':
            generate_commit_mr_table()
            return
        else:
            mr = get_mr_by_commit_sha(mr_manager, commit_id)
            if mr is not None:
                print(mr._attrs['web_url'])
            else:
                print('No matching MR found')


def generate_commit_mr_table():
    gl = get_gitlab_instance()
    project = get_main_project(gl, PROJECT_ID)
    mr_manager = get_project_mr_manager(project)
    commit_mr = create_mr_commit_table(mr_manager)
    commit_mr_file = open(COMMIT_MR_FILE, 'w')
    json.dump(commit_mr, commit_mr_file)
    print('Commit to MR table successfully generated')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('please use: glab.py <commit_id>')
    elif sys.argv[1] == "gen-cache":
        generate_commit_mr_table()
    else:
        find_mr_url_by_commit(sys.argv[1])

