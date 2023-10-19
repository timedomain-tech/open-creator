
## Commands

see help

```shell
creator -h
```

**Arguments**:

- `-h, --help`  
    show this help message and exit
- `-c, --config`
    open config.yaml file in text editor
- `-i, --interactive`
    Enter interactive mode
- COMMANDS `{create,save,search,server,ui}`


---

### ui

streamlit demo:

```
creator ui
```

open [streamlit demo](http://localhost:8501/)

---

### create

usage:

```
creator create [-h] [-r REQUEST] [-m MESSAGES] [-sp SKILL_JSON_PATH] [-c FILE_CONTENT] [-f FILE_PATH] [-hf_id HUGGINGFACE_REPO_ID]
                      [-hf_path HUGGINGFACE_SKILL_PATH] [-s]
```

`-h, --help`  
    show this help message and exit

`-r REQUEST, --request REQUEST`  
    Request string

`-m MESSAGES, --messages MESSAGES`  
    Openai messages format

`-sp SKILL_JSON_PATH, --skill_json_path SKILL_JSON_PATH`  
    Path to skill JSON file

`-c FILE_CONTENT, --file_content FILE_CONTENT`  
    File content of API docs or code file

`-f FILE_PATH, --file_path FILE_PATH`  
    Path to API docs or code file

`-hf_id HUGGINGFACE_REPO_ID, --huggingface_repo_id HUGGINGFACE_REPO_ID`  
    Huggingface repo ID

`-hf_path HUGGINGFACE_SKILL_PATH, --huggingface_skill_path HUGGINGFACE_SKILL_PATH`  
    Huggingface skill path

`-s, --save`  
    Save skill after creation

---

### save

usage:

```
creator save [-h] [-s SKILL] [-sp SKILL_JSON_PATH] [-hf_id HUGGINGFACE_REPO_ID]
```

`-h, --help`  
    show this help message and exit

`-s SKILL, --skill SKILL`  
    Skill json object

`-sp SKILL_JSON_PATH, --skill_json_path SKILL_JSON_PATH`  
    Path to skill JSON file

`-hf_id HUGGINGFACE_REPO_ID, --huggingface_repo_id HUGGINGFACE_REPO_ID`  
    Huggingface repo ID

---

### search

```
creator search [-h] [-q QUERY] [-k TOP_K] [-t THRESHOLD] [-r]
```

`-h, --help`  
    show this help message and exit

`-q QUERY, --query QUERY`  
    Search query

`-k TOP_K, --top_k TOP_K`  
    Number of results to return, default 3

`-t THRESHOLD, --threshold THRESHOLD`  
    Threshold for search, default 0.8

`-r, --remote`  
    Search from remote

---

### server

```
creator server [-h] [-host HOST] [-p PORT]
```

`-h, --help`  
    show this help message and exit

`-host HOST, --host HOST`  
    IP address

`-p PORT, --port PORT`  
    Port number


After running the server, you can access the API documentation at [docs](http://localhost:8000/docs)


---

### Interactive mode

Directly enter
```shell
creator
```

or 

```shell
creator [-i] [--interactive] [-q] [--quiet]
```

- `q, --quiet`           Quiet mode to enter interactive mode and not rich_print LOGO and help
