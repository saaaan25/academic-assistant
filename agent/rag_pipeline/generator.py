from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from . import config, prompt

def generate_response(question, fragments):
    # Unir fragmentos para formar el contexto
    context_text = "\n\n---\n\n".join([doc.page_content for doc in fragments])
    
    # Configurar el modelo de lenguaje y el prompt
    llm = ChatGroq(
        model = config.LLM_MODEL_NAME, 
        temperature = 0, 
        groq_api_key = config.LLM_API_KEY
    )
    
    prompt_template = ChatPromptTemplate.from_template(prompt.PROMPT)
    chain = prompt_template | llm
    
    # Obtener respuesta del modelo
    response = chain.invoke({
        "context": context_text, 
        "question": question
    })
    
    return response.content


# Generar respuesta con historial de la sesión
def generate_response_with_history(question, fragments, history=""):
    # Unir fragmentos para formar el contexto
    context_text = "\n\n---\n\n".join([doc.page_content for doc in fragments])
    
    # Configurar modelo
    llm = ChatGroq(
        model=config.LLM_MODEL_NAME, 
        temperature=0, 
        groq_api_key=config.LLM_API_KEY
    )
    
    # Utilizar prompt
    prompt_template = ChatPromptTemplate.from_template(prompt.PROMPT_SESSION)
    chain = prompt_template | llm
    
    # Inyectar las variables que recibe el prompt
    response = chain.invoke({
        "context": context_text, 
        "history": history,
        "question": question
    })
    
    return response.content

