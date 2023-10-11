

"""
refer to: https://github.com/JushBJJ/Mr.-Ranedeer-AI-Tutor
use a creator agent that can select following actions:
1. create
2. save
3. search
4. additional meta prompt
    - exit
    - clear
    - resest
    - undo
    - help
tester, interpreter, extractor, and refactor agents are using differnt emoji
"""


"""
usage: usage: creator create [-h] [-r REQUEST] [-m MESSAGES] [-sp SKILL_JSON_PATH] [-c FILE_CONTENT] [-f FILE_PATH] [-hf_id HUGGINGFACE_REPO_ID] [-hf_path HUGGINGFACE_SKILL_PATH] [-s]

options:
  -h, --help            show this help message and exit
  -r REQUEST, --request REQUEST
                        Request string
  -m MESSAGES, --messages MESSAGES
                        Openai messages format
  -sp SKILL_JSON_PATH, --skill_json_path SKILL_JSON_PATH
                        Path to skill JSON file
  -c FILE_CONTENT, --file_content FILE_CONTENT
                        File content of API docs or code file
  -f FILE_PATH, --file_path FILE_PATH
                        Path to API docs or code file
  -hf_id HUGGINGFACE_REPO_ID, --huggingface_repo_id HUGGINGFACE_REPO_ID
                        Huggingface repo ID
  -hf_path HUGGINGFACE_SKILL_PATH, --huggingface_skill_path HUGGINGFACE_SKILL_PATH
                        Huggingface skill path
  -s, --save            Save skill after creation

usage: creator save [-h] [-s SKILL] [-sp SKILL_JSON_PATH] [-hf_id HUGGINGFACE_REPO_ID]

options:
  -h, --help            show this help message and exit
  -s SKILL, --skill SKILL
                        Skill json object
  -sp SKILL_JSON_PATH, --skill_json_path SKILL_JSON_PATH
                        Path to skill JSON file
  -hf_id HUGGINGFACE_REPO_ID, --huggingface_repo_id HUGGINGFACE_REPO_ID
                        Huggingface repo ID

usage: creator search [-h] [-q QUERY] [-k TOP_K] [-t THRESHOLD] [-r]

options:
  -h, --help            show this help message and exit
  -q QUERY, --query QUERY
                        Search query
  -k TOP_K, --top_k TOP_K
                        Number of results to return, default 3
  -t THRESHOLD, --threshold THRESHOLD
                        Threshold for search, default 0.8
  -r, --remote          Search from remote

Open Creator CLI

positional arguments:
  {create,save,search}
    create              Create a new skill from above various ways
    save                Save the skill
    search              Search for a skill

options:
  -h, --help            show this help message and exit
  -i, --interactive     Enter interactive mode
  -q, --quiet           Quiet mode to enter interactive mode and not rich_print LOGO and help
  -config, --config     open config.yaml file in text editor
"""

def _handle_command(creator):
    command_list = command.strip().split()
    command = command_list[0]
    params = command_list[1:]

    if command == "%exit":
        print(Markdown("> Bye!"))
        exit()
    elif command == "%help":
        print(Markdown(_HELP_STR))

    elif command.startswith("%create"):
        save = params[params.index('-s')+1] if '-s' in params else False

        skill = Creator.create(messages=messages)
        if skill is None:
            return False
        cache_skills.append(skill)
        if save:
            Creator.save(skill=skill)

    elif command == "%save":
        if len(cache_skills) == 0:
            print(Markdown("> No skill to save! Please create a skill first."))
            return False
        huggingface_repo_id = params[params.index('-hf')+1] if '-hf' in params else None
        skill_path = params[params.index('-sp')+1] if '-sp' in params else None

        choices = []
        for i, skill in enumerate(cache_skills):
            choice = "{} | {} | {} | {}".format(skill.skill_name, skill.skill_description, skill.skill_metadata.created_at, skill.skill_metadata.author)
            choices.append((choice, skill.skill_name))

        questions = [
            inquirer.Checkbox('skills', message="> Select skills to save", choices=choices),
        ]
        if not skill_path:
            questions.append(inquirer.Text('skill_path', message="> Enter your skill save path or save skill to?", default=config.local_skill_library_path))

        answers = inquirer.prompt(questions)
        skill_path = answers.get("skill_path", config.local_skill_library_path)
        selected_skills = answers.get("skills", [])
        if len(selected_skills) == 0:
            print(Markdown("> No skill to save!"))
            return False
        push_to_remote = inquirer.prompt([inquirer.Confirm("push_to_remote", message="push to remote?", default=False)])

        if push_to_remote["push_to_remote"]:
            questions = []
            if not huggingface_repo_id:
                selected_huggingface_repo_id = inquirer.prompt([inquirer.Text('huggingface_repo_id', message="> Enter your huggingface repo id")])
                huggingface_repo_id = selected_huggingface_repo_id["huggingface_repo_id"]

        for skill_name in selected_skills:
            skill = [skill for skill in cache_skills if skill.skill_name == skill_name][0]
            Creator.save(skill, skill_path, huggingface_repo_id)
            if push_to_remote:
                Creator.save(skill=skill, skill_path=skill_path, huggingface_repo_id=huggingface_repo_id)

    elif command == "%search":
        request = params[params.index('-q')+1] if '-q' in params else None
        if request is None:
            print(Markdown("> no search request Please use -q '<your search query>' "))
            return False
        top_k = params[params.index('-k')+1] if '-k' in params else None
        if top_k is None:
            skills = Creator.search(request)
        else:
            skills = Creator.search(request, top_k)
        cache_skills += skills
    else:
        print(Markdown("> Invalid command. Here is a list of available commands:"))
        print(Markdown(_HELP_STR))
        return False
    return True
