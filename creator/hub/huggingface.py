import json
from creator.schema.skill import CodeSkill
from creator.schema.library import config
from huggingface_hub import hf_hub_download, create_repo, Repository
import os
from loguru import logger
import subprocess


def hf_pull(repo_id, huggingface_skill_path, save_path) -> CodeSkill:
    return_path = hf_hub_download(repo_id=repo_id, subfolder=huggingface_skill_path, filename="skill.json", repo_type="space")
    with open(return_path) as f:
        skill_json = json.load(f)
    # copy to local skill library
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    os.system(command=f"cp {return_path} {save_path}")
    logger.success(f"Successfully pulled skill {huggingface_skill_path} from repo {repo_id} to {save_path}.")
    return CodeSkill(**skill_json)


def hf_update_app_file(local_dir):
    # download app.py
    repo_id = config.official_skill_library_path
    return_path = hf_hub_download(repo_id=repo_id, filename="app.py", repo_type="space")
    os.system(command=f"cp {return_path} {local_dir}")
    return_path = hf_hub_download(repo_id=repo_id, filename="requirements.txt")
    os.system(command=f"cp {return_path} {local_dir}")
    return_path = hf_hub_download(repo_id=repo_id, filename="README.md")
    os.system(command=f"cp {return_path} {local_dir}")
    logger.success(f"Successfully updated repo {repo_id}.")
    subprocess.run(['git', 'add', 'app.py', 'requirements.txt', 'README.md'], cwd=local_dir, check=True, capture_output=True)
    subprocess.run(['git', 'commit', '-am', 'Add application file'], cwd=local_dir, check=True, capture_output=True)
    subprocess.run(['git', 'push'], cwd=local_dir, check=True, capture_output=True)


def hf_repo_update(repo_id, local_dir):
    if not os.path.exists(local_dir):
        os.path.makedirs(local_dir)
        is_new = False
        try:
            repo_url = create_repo(repo_id=repo_id, repo_type="space", space_sdk="gradio")
            logger.success(f"Successfully created repo {repo_id}.")
            is_new = True
        except Exception as e:
            logger.warning(f"Failed to create repo {repo_id} with error {e}.")
            repo_url = f"https://huggingface.co/spaces/{repo_id}"
        
        Repository(local_dir=local_dir, clone_from=repo_url).git_pull()
        logger.success(f"Successfully cloned repo {repo_id} to {local_dir}.")
        if is_new:
            hf_update_app_file(local_dir=local_dir)
    else:
        Repository(local_dir=local_dir).git_pull()


def hf_push(folder_path):
    skill_name = os.path.basename(folder_path)
    subprocess.run(['git', 'add', '.'], cwd=folder_path, check=True, capture_output=True)
    subprocess.run(['git', 'commit', '-m', f'feat: add skill {skill_name}'], cwd=folder_path, check=True, capture_output=True)
    subprocess.run(['git', 'push'], cwd=folder_path, check=True, capture_output=True)
