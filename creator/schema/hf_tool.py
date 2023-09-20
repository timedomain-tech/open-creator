from creator.schema.skill import CodeSkill, BaseSkill
from transformers.tools import Tool
from typing import List


class HFSkill(Tool):
    """
    A base class for the functions used by the agent. Subclass this and implement the `__call__` method as well as the
    following class attributes:

    - **description** (`str`) -- A short description of what your tool does, the inputs it expects and the output(s) it
      will return. For instance 'This is a tool that downloads a file from a `url`. It takes the `url` as input, and
      returns the text contained in the file'.
    - **name** (`str`) -- A performative name that will be used for your tool in the prompt to the agent. For instance
      `"text-classifier"` or `"image_generator"`.
    - **inputs** (`List[str]`) -- The list of modalities expected for the inputs (in the same order as in the call).
      Modalitiies should be `"text"`, `"image"` or `"audio"`. This is only used by `launch_gradio_demo` or to make a
      nice space from your tool.
    - **outputs** (`List[str]`) -- The list of modalities returned but the tool (in the same order as the return of the
      call method). Modalitiies should be `"text"`, `"image"` or `"audio"`. This is only used by `launch_gradio_demo`
      or to make a nice space from your tool.

    You can also override the method [`~Tool.setup`] if your tool as an expensive operation to perform before being
    usable (such as loading a model). [`~Tool.setup`] will be called the first time you use your tool, but not at
    instantiation.
    """

    description: str = "This is a tool that ..."
    name: str = ""

    inputs: List[str]
    outputs: List[str]

    def __init__(self, *args, **kwargs):
        self.is_initialized = False

    def __call__(self, *args, **kwargs):
        return NotImplemented("Write this method in your subclass of `Tool`.")

    def setup(self):
        """
        Overwrite this method here for any operation that is expensive and needs to be executed before you start using
        your tool. Such as loading a big model.
        """
        self.is_initialized = True

    def save(self, output_dir):
        """
        Saves the relevant code files for your tool so it can be pushed to the Hub. This will copy the code of your
        tool in `output_dir` as well as autogenerate:

        - a config file named `tool_config.json`
        - an `app.py` file so that your tool can be converted to a space
        - a `requirements.txt` containing the names of the module used by your tool (as detected when inspecting its
          code)

        You should only use this method to save tools that are defined in a separate module (not `__main__`).

        Args:
            output_dir (`str`): The folder in which you want to save your tool.
        """
        os.makedirs(output_dir, exist_ok=True)
        # Save module file
        if self.__module__ == "__main__":
            raise ValueError(
                f"We can't save the code defining {self} in {output_dir} as it's been defined in __main__. You "
                "have to put this code in a separate module so we can include it in the saved folder."
            )
        module_files = custom_object_save(self, output_dir)

        module_name = self.__class__.__module__
        last_module = module_name.split(".")[-1]
        full_name = f"{last_module}.{self.__class__.__name__}"

        # Save config file
        config_file = os.path.join(output_dir, "tool_config.json")
        if os.path.isfile(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                tool_config = json.load(f)
        else:
            tool_config = {}

        tool_config = {"tool_class": full_name, "description": self.description, "name": self.name}
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(tool_config, indent=2, sort_keys=True) + "\n")

        # Save app file
        app_file = os.path.join(output_dir, "app.py")
        with open(app_file, "w", encoding="utf-8") as f:
            f.write(APP_FILE_TEMPLATE.format(module_name=last_module, class_name=self.__class__.__name__))

        # Save requirements file
        requirements_file = os.path.join(output_dir, "requirements.txt")
        imports = []
        for module in module_files:
            imports.extend(get_imports(module))
        imports = list(set(imports))
        with open(requirements_file, "w", encoding="utf-8") as f:
            f.write("\n".join(imports) + "\n")

    @classmethod
    def from_hub(
        cls,
        repo_id: str,
        model_repo_id: Optional[str] = None,
        token: Optional[str] = None,
        remote: bool = False,
        **kwargs,
    ):
        """
        Loads a tool defined on the Hub.

        Args:
            repo_id (`str`):
                The name of the repo on the Hub where your tool is defined.
            model_repo_id (`str`, *optional*):
                If your tool uses a model and you want to use a different model than the default, you can pass a second
                repo ID or an endpoint url to this argument.
            token (`str`, *optional*):
                The token to identify you on hf.co. If unset, will use the token generated when running
                `huggingface-cli login` (stored in `~/.huggingface`).
            remote (`bool`, *optional*, defaults to `False`):
                Whether to use your tool by downloading the model or (if it is available) with an inference endpoint.
            kwargs (additional keyword arguments, *optional*):
                Additional keyword arguments that will be split in two: all arguments relevant to the Hub (such as
                `cache_dir`, `revision`, `subfolder`) will be used when downloading the files for your tool, and the
                others will be passed along to its init.
        """
        if remote and model_repo_id is None:
            endpoints = get_default_endpoints()
            if repo_id not in endpoints:
                raise ValueError(
                    f"Could not infer a default endpoint for {repo_id}, you need to pass one using the "
                    "`model_repo_id` argument."
                )
            model_repo_id = endpoints[repo_id]
        hub_kwargs_names = [
            "cache_dir",
            "force_download",
            "resume_download",
            "proxies",
            "revision",
            "repo_type",
            "subfolder",
            "local_files_only",
        ]
        hub_kwargs = {k: v for k, v in kwargs.items() if k in hub_kwargs_names}

        # Try to get the tool config first.
        hub_kwargs["repo_type"] = get_repo_type(repo_id, **hub_kwargs)
        resolved_config_file = cached_file(
            repo_id,
            TOOL_CONFIG_FILE,
            use_auth_token=token,
            **hub_kwargs,
            _raise_exceptions_for_missing_entries=False,
            _raise_exceptions_for_connection_errors=False,
        )
        is_tool_config = resolved_config_file is not None
        if resolved_config_file is None:
            resolved_config_file = cached_file(
                repo_id,
                CONFIG_NAME,
                use_auth_token=token,
                **hub_kwargs,
                _raise_exceptions_for_missing_entries=False,
                _raise_exceptions_for_connection_errors=False,
            )
        if resolved_config_file is None:
            raise EnvironmentError(
                f"{repo_id} does not appear to provide a valid configuration in `tool_config.json` or `config.json`."
            )

        with open(resolved_config_file, encoding="utf-8") as reader:
            config = json.load(reader)

        if not is_tool_config:
            if "custom_tool" not in config:
                raise EnvironmentError(
                    f"{repo_id} does not provide a mapping to custom tools in its configuration `config.json`."
                )
            custom_tool = config["custom_tool"]
        else:
            custom_tool = config

        tool_class = custom_tool["tool_class"]
        tool_class = get_class_from_dynamic_module(tool_class, repo_id, use_auth_token=token, **hub_kwargs)

        if len(tool_class.name) == 0:
            tool_class.name = custom_tool["name"]
        if tool_class.name != custom_tool["name"]:
            logger.warning(
                f"{tool_class.__name__} implements a different name in its configuration and class. Using the tool "
                "configuration name."
            )
            tool_class.name = custom_tool["name"]

        if len(tool_class.description) == 0:
            tool_class.description = custom_tool["description"]
        if tool_class.description != custom_tool["description"]:
            logger.warning(
                f"{tool_class.__name__} implements a different description in its configuration and class. Using the "
                "tool configuration description."
            )
            tool_class.description = custom_tool["description"]

        if remote:
            return RemoteTool(model_repo_id, token=token, tool_class=tool_class)
        return tool_class(model_repo_id, token=token, **kwargs)

    def push_to_hub(
        self,
        repo_id: str,
        commit_message: str = "Upload tool",
        private: Optional[bool] = None,
        token: Optional[Union[bool, str]] = None,
        create_pr: bool = False,
    ) -> str:
        """
        Upload the tool to the Hub.

        Parameters:
            repo_id (`str`):
                The name of the repository you want to push your tool to. It should contain your organization name when
                pushing to a given organization.
            commit_message (`str`, *optional*, defaults to `"Upload tool"`):
                Message to commit while pushing.
            private (`bool`, *optional*):
                Whether or not the repository created should be private.
            token (`bool` or `str`, *optional*):
                The token to use as HTTP bearer authorization for remote files. If unset, will use the token generated
                when running `huggingface-cli login` (stored in `~/.huggingface`).
            create_pr (`bool`, *optional*, defaults to `False`):
                Whether or not to create a PR with the uploaded files or directly commit.
        """
        repo_url = create_repo(
            repo_id=repo_id, token=token, private=private, exist_ok=True, repo_type="space", space_sdk="gradio"
        )
        repo_id = repo_url.repo_id
        metadata_update(repo_id, {"tags": ["tool"]}, repo_type="space")

        with tempfile.TemporaryDirectory() as work_dir:
            # Save all files.
            self.save(work_dir)
            logger.info(f"Uploading the following files to {repo_id}: {','.join(os.listdir(work_dir))}")
            return upload_folder(
                repo_id=repo_id,
                commit_message=commit_message,
                folder_path=work_dir,
                token=token,
                create_pr=create_pr,
                repo_type="space",
            )

    @staticmethod
    def from_gradio(gradio_tool):
        """
        Creates a [`Tool`] from a gradio tool.
        """

        class GradioToolWrapper(Tool):
            def __init__(self, _gradio_tool):
                super().__init__()
                self.name = _gradio_tool.name
                self.description = _gradio_tool.description

        GradioToolWrapper.__call__ = gradio_tool.run
        return GradioToolWrapper(gradio_tool)



def skill_to_huggingface_tool(skill: CodeSkill | BaseSkill):
    skill_tool = Tool(
        name=skill.skill_name, 
        description=skill.skill_description
    )

