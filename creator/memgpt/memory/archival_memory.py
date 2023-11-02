from .converter import ArchivalMessage
from .recall_memory import RecallMemory


class ArchivalMemory(RecallMemory):

    def __repr__(self) -> str:
        if len(self.message_database.messages) == 0:
            memory_str = "<empty>"
        else:
            memory_str = "\n".join([d.content for d in self.message_database.messages])
        return f"\n### ARCHIVAL MEMORY ###\n{memory_str}"

    def _filter_messages(self):
        """Utility to filter messages based on roles."""
        return [d for d in self.message_database.messages if d.type in ['archival']]

    async def add(self, message, name=None):
        """Adds a new memory string. Optionally, a name can be provided."""
        self.message_database.add_message(ArchivalMessage(content=message))
