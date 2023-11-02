from typing import List, Dict, Any, Optional
import networkx as nx

from creator.agents.base import BaseAgent
from creator.utils import print

from langchain.chains.base import Chain
from langchain.callbacks.manager import CallbackManagerForChainRun


class GroupChat(Chain):
    graph: Optional[nx.DiGraph] = None
    max_consecutive_auto_reply: int = 3

    @property
    def input_keys(self) -> List[str]:
        """Keys expected to be in the chain input."""
        return ["messages", "sender", "receivers"]

    @property
    def output_keys(self) -> List[str]:
        """Keys expected to be in the chain output."""
        return ["messages", "sender", "receivers"]

    def add_agent(self, agent: BaseAgent):
        """
        Add an agent to the graph.

        :param agent: The agent to be added.
        """
        self.graph.add_node(agent.agent_name, agent=agent)

    def add_agents(self, agents: List[BaseAgent]):
        """
        Add a list of agents to the graph.

        :param agents: The list of agents to be added.
        """
        for agent in agents:
            self.add_agent(agent)

    def remove_agent(self, agent_name: str):
        """
        Remove an agent from the graph.

        :param agent_name: The name of the agent to be removed.
        """
        if agent_name in self.graph:
            self.graph.remove_node(agent_name)

    def add_edge(self, agent1: BaseAgent, agent2: BaseAgent):
        """
        Add an edge between two agents.

        :param agent1: The first agent.
        :param agent2: The second agent.
        """
        self.graph.add_edge(agent1.agent_name, agent2.agent_name)

    def remove_edge(self, agent1: BaseAgent, agent2: BaseAgent):
        """
        Remove an edge between two agents.

        :param agent1: The first agent.
        :param agent2: The second agent.
        """
        self.graph.remove_edge(agent1.agent_name, agent2.agent_name)

    @classmethod
    def from_mapping(cls, mapping: Dict[BaseAgent, List[BaseAgent]]):
        graph = nx.DiGraph()
        node_set = set()
        for from_node, to_nodes in mapping.items():
            if from_node.agent_name not in node_set:
                node_set.add(from_node)
            for node in to_nodes:
                if node.agent_name not in node_set:
                    node_set.add(node)
                graph.add_edge(from_node.agent_name, node.agent_name)
        cls.graph = graph
        return cls

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        return self.run_chat(inputs["messages"], inputs["sender"], inputs["receivers"])

    def run_chat(self, messages: List[Dict], sender: str, receivers: List[str], run_manager: Optional[CallbackManagerForChainRun] = None):
        """Run a group chat."""
        assert len(messages) > 0, "Input Messages Must Not Be Empty"
        curr_cnt = 0
        while curr_cnt < self.max_consecutive_auto_reply:
            for receiver in receivers:
                try:
                    receiver_agent = self.graph.nodes[receiver]
                except KeyError:
                    print("> agent {receiver} not found", print_type="markdown")
                    raise KeyError
                if not receiver_agent.share_memory:
                    messages = [messages[-1]]
                output_messages = receiver_agent.with_config({"callbacks": run_manager.get_child()}).invoke({"messages": messages})
                sender = receiver
                try:
                    receiver = output_messages[-1]["receiver"]
                except KeyError:
                    print("> agent {receiver} has no receiver", print_type="markdown")
                    raise KeyError

                if not receiver_agent.share_memory:
                    messages = messages[:-1] + output_messages
                else:
                    messages = output_messages

                if receiver == "human":
                    return messages, sender, receiver
                curr_cnt += 1
