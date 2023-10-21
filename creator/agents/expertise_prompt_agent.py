from typing import Any, Dict

from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import parse_partial_json

from creator.config.library import config
from creator.utils import load_system_prompt
from creator.llm.llm_creator import create_llm

from base import BaseAgent


class ExpertisePromptAgent(BaseAgent):
    output_key: str = "expertise_prompt"

    @property
    def _chain_type(self):
        return "ExpertisePromptAgent"

    def construct_prompt(self, langchain_messages: Dict[str, Any]):
        prompt = ChatPromptTemplate.from_messages(messages=[
            *langchain_messages,
            ("system", self.system_template)
        ])
        return prompt
 
    def parse_output(self, messages):
        function_call = messages[-1].get("function_call", None)
        if function_call is not None:
            rewrited_prompt = parse_partial_json(function_call.get("arguments", "{}"))
            prefix_prompt = rewrited_prompt.get("prefix_prompt", "")
            postfix_prompt = rewrited_prompt.get("postfix_prompt", "")
            result = {"prefix_prompt": prefix_prompt, "postfix_prompt": postfix_prompt}
            return {"expertise_prompt": result}
        return {"expertise_prompt": None}


def create_expertise_prompt_agent(llm):
    template = load_system_prompt(config.expertise_prompt_agent_prompt_path)

    function_schema = {
        "name": "expertise_prompt",
        "description": "a function that guide GPT to act as an expert in the field to respond to the user's request",
        "parameters": {
            "properties": {
                "prefix_prompt": {
                    "type": "string",
                    "description": "A concise directive provided at the beginning of the user's request, guiding GPT to adopt a specific expert role or mindset.",
                },
                "postfix_prompt": {
                    "type": "string",
                    "description": "A brief set of tips or guidelines placed after the user's original request, offering additional context or direction for GPT's response.",
                }
            },
            "type": "object",
            "required": ["prefix_prompt", "postfix_prompt"]
        }
    }

    chain = ExpertisePromptAgent(
        llm=llm,
        system_template=template,
        function_schemas=[function_schema],
        verbose=False
    )
    return chain


llm = create_llm(config)
expertise_prompt_agent = create_expertise_prompt_agent(llm)

if __name__ == "__main__":
    TabMWP_test = """\"question\": \"Hannah baked cookies each day for a bake sale. How many more cookies did Hannah bake on Saturday than on Sunday?\", \"table\": \"Name: Cookies baked\nUnit: cookies\nContent:\nDay | Number of cookies\nFriday | 163\nSaturday | 281\nSunday | 263\"
"""
    tool_transfer_test=""""intro": "The tool is used to calculate the optimal number of units to produce to maximize profit for a manufacturing company. It takes into account the fixed costs, variable costs, selling price, and demand for the product. The function uses the formula Profit = (Selling Price * Quantity) - (Variable Cost * Quantity) - Fixed Cost to calculate the profit and returns the optimal quantity to produce.", "tool": "```python\ndef calculate_optimal_units(selling_price, variable_cost, fixed_cost, demand):\n    \"\"\"\n    Calculates the optimal number of units to produce to maximize profit.\n\n    Parameters:\n    selling_price (float): The price at which the product is sold.\n    variable_cost (float): The cost of producing one unit of the product.\n    fixed_cost (float): The fixed cost of production.\n    demand (int): The number of units that can be sold at the given price.\n\n    Returns:\n    int: The optimal number of units to produce to maximize profit.\n    \"\"\"\n    # Calculate the profit for each quantity\n    profits = []\n    for quantity in range(1, demand+1):\n        profit = (selling_price * quantity) - (variable_cost * quantity) - fixed_cost\n        profits.append(profit)\n\n    # Find the quantity that maximizes profit\n    optimal_quantity = profits.index(max(profits)) + 1\n\n    # Return the optimal quantity\n    return optimal_quantity\n```", "scn1": "Production Planning\nA manufacturing company produces a product that has a fixed cost of $10,000, a variable cost of $5 per unit, and a selling price of $20 per unit. The company can sell up to 5,000 units of the product at this price. What is the optimal number of units to produce to maximize profit?", "sol1": "```python\n# Set the inputs for the manufacturing company\nselling_price = 20\nvariable_cost = 5\nfixed_cost = 10000\ndemand = 5000\n\n# Calculate the optimal number of units to produce\noptimal_quantity = calculate_optimal_units(selling_price, variable_cost, fixed_cost, demand)\n\n# Print the optimal quantity\nprint(optimal_quantity)\n```", "ans1": 5000.0, "scn2": "Pricing Strategy\nA company produces a product that has a fixed cost of $20,000, a variable cost of $10 per unit, and a demand of 10,000 units. The company wants to maximize profit and is considering two pricing strategies. The first strategy is to sell the product at $30 per unit, and the second strategy is to sell the product at $35 per unit. What is the optimal pricing strategy for the company?", "sol2": "```python\n# Set the inputs for the company\nfixed_cost = 20000\nvariable_cost = 10\ndemand = 10000\n\n# Strategy 1: Selling the product at $30 per unit\nselling_price_1 = 30\noptimal_quantity_1 = calculate_optimal_units(selling_price_1, variable_cost, fixed_cost, demand)\nprofit_1 = (selling_price_1 * optimal_quantity_1) - (variable_cost * optimal_quantity_1) - fixed_cost\n\n# Strategy 2: Selling the product at $35 per unit\nselling_price_2 = 35\noptimal_quantity_2 = calculate_optimal_units(selling_price_2, variable_cost, fixed_cost, demand)\nprofit_2 = (selling_price_2 * optimal_quantity_2) - (variable_cost * optimal_quantity_2) - fixed_cost\n\n# Determine the optimal pricing strategy\nif profit_1 > profit_2:\n    print(\"The optimal pricing strategy is to sell the product at $30 per unit.\")\nelse:\n    print(\"The optimal pricing strategy is to sell the product at $35 per unit.\")\n```", "ans2": 35.0, "scn3": "Capacity Planning\nA company produces a product that has a fixed cost of $50,000, a variable cost of $15 per unit, and a selling price of $25 per unit. The company has a production capacity of 10,000 units. What is the optimal number of units to produce to maximize profit?", "sol3": "```python\n# Set the inputs for the company\nselling_price = 25\nvariable_cost = 15\nfixed_cost = 50000\ndemand = 10000\n\n# Calculate the optimal number of units to produce\noptimal_quantity = calculate_optimal_units(selling_price, variable_cost, fixed_cost, demand)\n\n# Print the optimal quantity\nprint(optimal_quantity)\n```"
"""
    messages = [{
            "role": "user",
            "content": TabMWP_test
        }]
    result = expertise_prompt_agent.run({
                "messages": messages,
                "verbose": True,
            })
