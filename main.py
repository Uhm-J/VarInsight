# Langchain imports
from langchain.experimental import load_agent_executor
from langchain.tools import StructuredTool
from langchain.agents import AgentType, initialize_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.chat_models.openai import ChatOpenAI
from langchain.experimental.plan_and_execute import PlanAndExecute, load_chat_planner
from langchain.tools.file_management.read import ReadFileTool
from langchain.tools.file_management.write import WriteFileTool



# VarInsight imports
from utilities.tools import ClinVarAPIWrapper, PubMedAPIWrapper, OmimAPIWrapper

# Initialize tools
llm = ChatOpenAI(temperature=0)  # 0 temperature for deterministic output
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)  # Memory to store chat history
chat_history = MessagesPlaceholder(variable_name="chat_history")  # Placeholder for chat history

# Load tools from utilities
clinvar = ClinVarAPIWrapper()
pubmed = PubMedAPIWrapper()
ncbi = OmimAPIWrapper()
write_file = WriteFileTool()
read_file = ReadFileTool()

# Create tools list for agent, these are StructuredTools, which means they can handle multiple inputs
tools = [
    StructuredTool.from_function(
        func=clinvar.run,
        name=clinvar.name,
        description=clinvar.description,
    ),
    # StructuredTool.from_function(
    #     func=pubmed.run,
    #     name=pubmed.name,
    #     description=pubmed.description,
    # ),
    StructuredTool.from_function(
        func=ncbi.run,
        name=ncbi.name,
        description=ncbi.description,
    ),
    write_file,
    read_file
]

planner = load_chat_planner(llm)
executor = load_agent_executor(llm, tools, verbose=True)


# Initialize agent
# agent = initialize_agent(llm=llm,
#                          agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # Structured chat agent
#                          verbose=True,  # Print out the agent's reasoning and actions
#                          memory=memory,
#                          agent_kwargs={
#                             "memory_prompts": [chat_history],
#                             "input_variables": ["input", "agent_scratchpad", "chat_history"]
#                          },
#                          tools=tools)

agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)

#planner_and_exec = PlanAndExecute(planner=planner, executer=agent, verbose=True)

# Example usage
variant = "c.1187G>A in CMTR1 gene"  # https://www.ncbi.nlm.nih.gov/clinvar/RCV003191570/?redir=rcv
variant_alt = "c.1026_1027delinsCA + SCN1A"
variant_input = input("Enter a variant and gene: ")
file = "test.txt"

query = f"Goal: Generate a report using every tool available about {variant_input}.\n" \
        f"If you find protein changes in ClinVar, make sure to check the protein changes as well, " \
        f"as there might be multiple changes resulting in the same protein change. This can be done by extracting the protein change from the first search, and using this (in combination with the gene) as input for ClinVar, instead of the cdna change." \
        f"Make sure to refer to the information found using the doi, PMID, or ClinVar accession. You can save the information to {file}" \
        f"If the tools do not give valuable information, abort early." \
        f"Let's think step by step."
query = f"Goal: Generate a report using every tool available about {variant_input}.\n"
print("Task:", query)

response = agent.run(query)
print("VarInsight:", response)

"""
TODO:
Create a specific agent for this use case, which regenerates a report.
--> Can this have the tools already in it?
"""

print(agent.memory)
print(agent.step_container)