from textual.suggester import Suggester


class SuggestFromDict(Suggester):
    """Give completion suggestions based on a nested dictionary of options.

    Example:
        ```py
        SUGGESTOR_TREE = {
            'create': {
                '--save': None,
                '-s': None,
            },
            'save': {
                '--skill_path': None,
                '--huggingface': None,
                '-sp': None,
                '-hf': None,
            },
            #... (other options)
        }

        suggester = SuggestFromDict(SUGGESTOR_TREE, case_sensitive=False)
        ```

        If the user types ++sa++ inside the input widget, a completion suggestion
        for `"save"` appears.
    """

    def __init__(self, suggestions: dict, *, case_sensitive: bool = True) -> None:
        """Creates a suggester based off of a given dictionary of possibilities.

        Args:
            suggestions: Valid suggestions in a nested dictionary format.
            case_sensitive: Whether suggestions are computed in a case sensitive manner
                or not. The keys in the `suggestions` dict represent the
                canonical representation of the completions and they will be suggested
                with that same casing.
        """
        super().__init__(case_sensitive=case_sensitive)
        self._suggestions = suggestions
        self.case_sensitive = case_sensitive
    
    def _handle_dot_suggestions(self, value):
        """
        Special handling for "." starting suggestions
        """
        dot_parts = value.split(".")
        if len(dot_parts) == 0:
            return None
        if len(dot_parts) == 1:
            return None
        if not dot_parts[-2].endswith(" "):
            last_part = "." + dot_parts[-1]
            return last_part
        return value

    def _get_suggestions_for_value(self, value: str) -> list[str]:
        """Recursively gets suggestions for a given value from the nested dictionary.

        Args:
            value: The current value.

        Returns:
            A list of valid completion suggestions.
        """
        parts = value.split()
        suggestions = self._suggestions

        for part in parts[:-1]:
            # If the part is in the suggestions, dive into the next level.
            if part in suggestions:
                suggestions = suggestions[part]
            # If not, try to find a deeper level where the part might be.
            else:
                for key, sub_suggestions in suggestions.items():
                    if isinstance(sub_suggestions, dict) and part in sub_suggestions:
                        suggestions = sub_suggestions[part]
                        break
        
        last_part = parts[-1] if parts else ""
        dot_last_part = self._handle_dot_suggestions(value)
        if dot_last_part is not None:
            last_part = dot_last_part
        return [
            key
            for key in suggestions.keys()
            if key.startswith(last_part) and (self.case_sensitive or key.lower().startswith(last_part.lower()))
        ]

    async def get_suggestion(self, value: str) -> str | None:
        """Gets a completion from the given possibilities.

        Args:
            value: The current value.

        Returns:
            A valid completion suggestion or `None`.
        """
        suggestions = self._get_suggestions_for_value(value)
        return suggestions[0] if suggestions else None
