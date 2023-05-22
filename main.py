# Langchain imports
from langchain.tools import StructuredTool
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.chat_models.openai import ChatOpenAI

# VarInsight imports
from utilities.tools import ClinVarAPIWrapper, PubMedAPIWrapper

# Initialize tools
llm = ChatOpenAI(temperature=0)  # 0 temperature for deterministic output
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)  # Memory to store chat history
chat_history = MessagesPlaceholder(variable_name="chat_history")  # Placeholder for chat history

# Load tools from utilities
clinvar = ClinVarAPIWrapper()
pubmed = PubMedAPIWrapper()

# Create tools list for agent, these are StructuredTools, which means they can handle multiple inputs
tools = [
    StructuredTool.from_function(
        func=clinvar.run,
        name=clinvar.name,
        description=clinvar.description,
    ),
    StructuredTool.from_function(
        func=pubmed.search_variant,
        name=pubmed.name,
        description=pubmed.description,
    ),
]

# Initialize agent
agent = initialize_agent(llm=llm,
                         agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # Structured chat agent
                         verbose=True,  # Print out the agent's reasoning and actions
                         memory=memory,
                         agent_kwargs={
                            "memory_prompts": [chat_history],
                            "input_variables": ["input", "agent_scratchpad", "chat_history"]
                         },
                         tools=tools)

# Example usage
variant_alt = "c.1187G>A in CMTR1 gene"  # https://www.ncbi.nlm.nih.gov/clinvar/RCV003191570/?redir=rcv
variant = "c.1026_1027delinsCA + SCN1A"
query = f"Tell me about {variant}"
print("You:", query)
response = agent.run(query)
print("VarInsight:", response)

"""
TODO:
Create a specific agent for this use case, which regenerates a report.
--> Can this have the tools already in it?
"""