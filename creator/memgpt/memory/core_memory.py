from .base import BaseMemory


class CoreMemory(BaseMemory):
    """Held in-context inside the system message

    Core Memory: Refers to the system block, which provides essential, foundational context to the AI.
    This includes the persona information, essential user details,
    and any other baseline data you deem necessary for the AI's basic functioning.
    """

    def __init__(self, persona=None, human=None, persona_char_limit=None, human_char_limit=None):
        self.persona = persona
        self.human = human
        self.persona_char_limit = persona_char_limit
        self.human_char_limit = human_char_limit

    def __repr__(self) -> str:
        return f"\n### CORE MEMORY ###\n=== Persona ===\n{self.persona}\n\n=== Human ===\n{self.human}"

    def to_dict(self):
        return {'persona': self.persona, 'human': self.human}

    @classmethod
    def load(cls, state):
        return cls(state['persona'], state['human'])

    def _edit(self, memory_string, name):
        char_limit = getattr(self, f"{name}_char_limit", None)
        if char_limit and len(memory_string) > char_limit:
            error_msg = (
                f"Add failed: Exceeds {char_limit} character limit (requested {len(memory_string)})."
                " Consider summarizing or moving content to archival memory and try again."
            )
            raise ValueError(error_msg)
        setattr(self, name, memory_string)
        return len(memory_string)

    async def add(self, message, name):
        new_content = getattr(self, name) + "\n" + message
        return self._edit(new_content, name)

    async def modify(self, old_content, new_content, name):
        current_content = getattr(self, name)
        if old_content not in current_content:
            raise ValueError(f'Content not found in {name} (ensure exact match)')
        updated_content = current_content.replace(old_content, new_content)
        return self._edit(updated_content, name)

    async def search(self, query, page, start_date=None, end_date=None):
        raise NotImplementedError('Core memory is always in-context and no need to search')
