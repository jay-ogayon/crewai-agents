from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from auditiq.tools.custom_tool import azure_search_tool, serper_search_tool, document_translation_tool

@CrewBase
class Auditiq():
    """AuditIQ intelligent audit crew with RAG and research capabilities"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def query_router(self) -> Agent:
        """Agent that determines whether a query needs Q&A or research approach"""
        return Agent(
            config=self.agents_config['query_router'], # type: ignore[index]
            verbose=True
        )

    @agent
    def rag_agent(self) -> Agent:
        """Agent that searches internal audit knowledge base using Azure Search"""
        return Agent(
            config=self.agents_config['rag_agent'], # type: ignore[index]
            tools=[azure_search_tool],
            verbose=True
        )

    @agent
    def audit_researcher(self) -> Agent:
        """Agent that conducts web research using SERPER API"""
        return Agent(
            config=self.agents_config['audit_researcher'], # type: ignore[index]
            tools=[serper_search_tool],
            verbose=True
        )

    @agent
    def document_translator(self) -> Agent:
        """Agent that translates documents (PDF or DOCX) while preserving formatting"""
        return Agent(
            config=self.agents_config['document_translator'], # type: ignore[index]
            tools=[document_translation_tool],
            verbose=True
        )

    @task
    def query_routing_task(self) -> Task:
        """Task to analyze and route user queries"""
        return Task(
            config=self.tasks_config['query_routing_task'], # type: ignore[index]
        )

    @task
    def qa_task(self) -> Task:
        """Task for answering queries using internal knowledge base"""
        return Task(
            config=self.tasks_config['qa_task'], # type: ignore[index]
        )

    @task
    def research_task(self) -> Task:
        """Task for conducting web research"""
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def document_translation_task(self) -> Task:
        """Task for translating documents (PDF or DOCX)"""
        return Task(
            config=self.tasks_config['document_translation_task'], # type: ignore[index]
        )

    def create_dynamic_crew(self, query_type: str) -> Crew:
        """Creates a crew based on the determined query type"""
        if query_type.upper().startswith('QA'):
            # Q&A workflow: Use only RAG agent
            return Crew(
                agents=[self.rag_agent()],
                tasks=[self.qa_task()],
                process=Process.sequential,
                verbose=True,
            )
        elif query_type.upper().startswith('TRANSLATE'):
            # Translation workflow: Use only document translator agent
            return Crew(
                agents=[self.document_translator()],
                tasks=[self.document_translation_task()],
                process=Process.sequential,
                verbose=True,
            )
        else:
            # Research workflow: Use only research agent
            return Crew(
                agents=[self.audit_researcher()],
                tasks=[self.research_task()],
                process=Process.sequential,
                verbose=True,
            )

    @crew
    def crew(self) -> Crew:
        """Creates the initial routing crew to determine query type"""
        return Crew(
            agents=[self.query_router()],
            tasks=[self.query_routing_task()],
            process=Process.sequential,
            verbose=True,
        )

    def kickoff_intelligent_routing(self, inputs: dict) -> str:
        """
        Intelligent routing workflow:
        1. Route the query to determine if it's Q&A or Research
        2. Execute the appropriate specialized crew
        3. Return the final result
        """
        try:
            # Step 1: Route the query
            routing_crew = self.crew()
            routing_result = routing_crew.kickoff(inputs=inputs)
            
            # Extract the routing decision from the result
            routing_decision = str(routing_result).strip()
            print(f"Routing decision: {routing_decision}")
            
            # Step 2: Create and execute appropriate crew based on routing
            specialized_crew = self.create_dynamic_crew(routing_decision)
            final_result = specialized_crew.kickoff(inputs=inputs)
            
            return str(final_result)
            
        except Exception as e:
            return f"Error in intelligent routing workflow: {str(e)}"
