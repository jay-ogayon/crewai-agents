from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from auditiq.tools.custom_tool import EchoSearchTool, AuditSearchTool, SerperSearchTool, DocumentTranslationTool

@CrewBase
class Auditiq():
    """AuditIQ intelligent audit crew with RAG and research capabilities"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def query_router(self) -> Agent:
        """Agent that determines whether a query needs Q&A or research approach"""
        return Agent(
            config=self.agents_config['query_router'], # type: ignore[index]
            verbose=True
        )

    @agent
    def echo_rag_agent(self) -> Agent:
        """Agent that searches GT Guidelines and Policy using echo index"""
        return Agent(
            config=self.agents_config['echo_rag_agent'], # type: ignore[index]
            tools=[EchoSearchTool()],
            verbose=True
        )

    @agent
    def audit_rag_agent(self) -> Agent:
        """Agent that searches audit methodology using audit-iq index"""
        return Agent(
            config=self.agents_config['audit_rag_agent'], # type: ignore[index]
            tools=[AuditSearchTool()],
            verbose=True
        )

    @agent
    def audit_researcher(self) -> Agent:
        """Agent that conducts web research using SERPER API"""
        return Agent(
            config=self.agents_config['audit_researcher'], # type: ignore[index]
            tools=[SerperSearchTool()],
            verbose=True
        )

    @agent
    def document_translator(self) -> Agent:
        """Agent that translates documents (PDF or DOCX) while preserving formatting"""
        return Agent(
            config=self.agents_config['document_translator'], # type: ignore[index]
            tools=[DocumentTranslationTool()],
            verbose=True
        )

    @task
    def query_routing_task(self) -> Task:
        """Task to analyze and route user queries"""
        return Task(
            config=self.tasks_config['query_routing_task'], # type: ignore[index]
        )

    @task
    def echo_task(self) -> Task:
        """Task for answering queries using GT Guidelines and Policy"""
        return Task(
            config=self.tasks_config['echo_task'], # type: ignore[index]
        )

    @task
    def audit_task(self) -> Task:
        """Task for answering queries using audit methodology"""
        return Task(
            config=self.tasks_config['audit_task'], # type: ignore[index]
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
        if query_type.upper().startswith('ECHO'):
            # ECHO workflow: Use GT Guidelines and Policy agent
            return Crew(
                agents=[self.echo_rag_agent()],
                tasks=[self.echo_task()],
                process=Process.sequential,
                verbose=True,
            )
        elif query_type.upper().startswith('AUDIT'):
            # AUDIT workflow: Use audit methodology agent
            return Crew(
                agents=[self.audit_rag_agent()],
                tasks=[self.audit_task()],
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
        1. Route the query to determine if it's ECHO, AUDIT, RESEARCH, or TRANSLATE
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
