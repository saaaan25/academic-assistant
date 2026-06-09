import os
import sys

# Añadir el directorio raíz al path para permitir ejecuciones directas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_groq import ChatGroq
from openai import OpenAI
from ragas import evaluate
from ragas.embeddings import HuggingFaceEmbeddings
from ragas.llms import llm_factory
from ragas.llms.base import LangchainLLMWrapper
from ragas.metrics._faithfulness import faithfulness
from ragas.metrics._answer_relevance import answer_relevancy
from ragas.metrics._context_precision import context_precision
from datasets import Dataset
from agent.rag_pipeline import config


class HuggingFaceRagasQueryAdapter(HuggingFaceEmbeddings):
    """Adapter for modern HuggingFace embeddings to expose legacy Ragas methods."""

    def embed_query(self, text: str):
        return self.embed_text(text)

    def embed_documents(self, texts: list[str]):
        return self.embed_texts(texts)

    async def aembed_query(self, text: str):
        return await self.aembed_text(text)

    async def aembed_documents(self, texts: list[str]):
        return await self.aembed_texts(texts)

def evaluate_rag_performance(
    question: str,
    context_list: list[str],
    answer: str,
    reference: str | None = None,
):
    """
    Evalúa la calidad de la respuesta generada usando métricas de Ragas.
    """
    if reference is None:
        reference = answer

    # Formateamos los datos para Ragas
    data = {
        "question": [question],
        "contexts": [context_list],
        "answer": [answer],
        "reference": [reference],
    }
    
    dataset = Dataset.from_dict(data)
    
    # Configurar el LLM de Ragas.
    # Se utiliza llm_factory para proveedores OpenAI modernos.
    if config.LLM_PROVIDER.lower() == "openai":
        if not config.LLM_API_KEY:
            raise ValueError("LLM_API_KEY is required when LLM_PROVIDER=openai")
        openai_client = OpenAI(api_key=config.LLM_API_KEY)
        llm_ragas = llm_factory(
            config.LLM_MODEL_NAME,
            provider="openai",
            client=openai_client,
        )
    else:
        # Fallback para proveedores que todavía no tienen adapter directo en esta versión de ragas.
        llm_langchain = ChatGroq(
            model=config.LLM_MODEL_NAME,
            temperature=0,
            groq_api_key=config.LLM_API_KEY,
        )
        llm_ragas = LangchainLLMWrapper(llm_langchain)

    embeddings = HuggingFaceRagasQueryAdapter(
        model=config.EMBEDDING_MODEL_NAME,
    )
    
    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
        ],
        llm=llm_ragas,
        embeddings=embeddings,
    )
    
    def _unwrap_score(value):
        return value[0] if isinstance(value, list) and len(value) == 1 else value

    scores = {
        "faithfulness": _unwrap_score(result["faithfulness"]),
        "answer_relevance": _unwrap_score(result["answer_relevancy"]),
        "context_precision": _unwrap_score(result["context_precision"]),
    }

    return scores

if __name__ == "__main__":
    # Ejemplo de uso para verificar
    print("Ejecutando prueba de evaluate_rag_performance...")
    
    sample_question = "¿Cuál es el horario de atención de la biblioteca?"
    sample_context = [
        "La biblioteca central está abierta de lunes a viernes de 9:00 a 18:00.",
        "Los fines de semana la biblioteca permanece cerrada.",
        "Para consultas específicas, puede llamar al 555-1234."
    ]
    sample_answer = "El horario de atención de la biblioteca central es de lunes a viernes de 9:00 a 18:00."
    
    # Prueba con una respuesta correcta
    scores_correct = evaluate_rag_performance(
        sample_question,
        sample_context,
        sample_answer,
        reference=sample_answer,
    )
    print("\n--- Resultados para respuesta correcta ---")
    print(f"Faithfulness: {scores_correct['faithfulness']:.4f}")
    print(f"Answer Relevance: {scores_correct['answer_relevance']:.4f}")
    print(f"Context Precision: {scores_correct['context_precision']:.4f}")

    # Prueba con una respuesta que alucina
    sample_answer_hallucination = "La biblioteca abre los sábados de 10:00 a 14:00."
    scores_hallucination = evaluate_rag_performance(
        sample_question,
        sample_context,
        sample_answer_hallucination,
        reference=sample_answer_hallucination,
    )
    print("\n--- Resultados para respuesta con alucinación ---")
    print(f"Faithfulness: {scores_hallucination['faithfulness']:.4f}")
    print(f"Answer Relevance: {scores_hallucination['answer_relevance']:.4f}")
    print(f"Context Precision: {scores_hallucination['context_precision']:.4f}")

    # Prueba con un contexto irrelevante
    sample_context_irrelevant = [
        "El comedor universitario sirve almuerzo de 12:00 a 14:00.",
        "Las inscripciones para el próximo semestre cierran el 30 de julio."
    ]
    sample_answer_no_info = "Lo siento, no encuentro esa información en los reglamentos."
    scores_irrelevant_context = evaluate_rag_performance(
        sample_question,
        sample_context_irrelevant,
        sample_answer_no_info,
        reference=sample_answer_no_info,
    )
    print("\n--- Resultados para contexto irrelevante ---")
    print(f"Faithfulness: {scores_irrelevant_context['faithfulness']:.4f}")
    print(f"Answer Relevance: {scores_irrelevant_context['answer_relevance']:.4f}")
    print(f"Context Precision: {scores_irrelevant_context['context_precision']:.4f}") # Corregido key

    # ========== EVALUACIONES UNMSM ==========
    print("\n\n" + "="*80)
    print("EVALUACIONES UNMSM - Requisitos y Procedimientos")
    print("="*80)

    unmsm_questions = [
        "¿Cuáles son los requisitos para realizar la matrícula en la UNMSM?",
        "¿Cuáles son los requisitos para obtener el título profesional?",
        "¿Cuál es el procedimiento para convalidar asignaturas?",
        "¿Qué pasa si no me matriculo en el plazo establecido?",
    ]

    authoritative_contexts = [
        "Para matricularse en la UNMSM se requiere DNI, voucher de pago, constancia de estudios secundarios y llenar el formulario de matrícula en la plataforma institucional.",
        "Para obtener el título profesional se requiere haber aprobado todas las asignaturas del plan de estudios, presentar y aprobar el trabajo de titulación (tesis o examen), haber cumplido con las prácticas preprofesionales y estar al día con las obligaciones administrativas y financieras.",
        "El procedimiento de convalidación implica solicitar la convalidación en la secretaría académica, presentar el plan de estudios y el contenido programático de las asignaturas a convalidar, y esperar la resolución de la facultad que aprueba o rechaza la convalidación.",
        "Si no te matriculas en el plazo establecido puedes perder tu cupo, generar recargos o multas, y necesitar realizar una matrícula extraordinaria o reinscripción según la normativa de la universidad.",
    ]

    irrelevant_contexts = [
        ["El comedor universitario sirve almuerzo de 12:00 a 14:00."],
        ["La biblioteca central tiene salas de estudio."],
        ["Las actividades deportivas se realizan los sábados."],
        ["Las inscripciones para el festival cultural cierran pronto."],
    ]

    for i, q in enumerate(unmsm_questions):
        print(f"\n{'─'*80}")
        print(f"Pregunta {i+1}: {q}")
        print('─'*80)

        # Contexto autoritativo
        auth_ctx = [authoritative_contexts[i]]
        auth_answer = authoritative_contexts[i]
        scores_auth = evaluate_rag_performance(q, auth_ctx, auth_answer, reference=auth_answer)

        print(f"  Con contexto autoritativo:")
        print(f"    Faithfulness:      {float(scores_auth['faithfulness']):.4f}")
        print(f"    Answer Relevance:  {float(scores_auth['answer_relevance']):.4f}")
        print(f"    Context Precision: {float(scores_auth['context_precision']):.4f}")

        # Contexto irrelevante
        irr_ctx = irrelevant_contexts[i]
        irr_answer = "No encuentro esa información en los documentos proporcionados."
        scores_irr = evaluate_rag_performance(q, irr_ctx, irr_answer, reference=irr_answer)

        print(f"  Con contexto irrelevante:")
        print(f"    Faithfulness:      {float(scores_irr['faithfulness']):.4f}")
        print(f"    Answer Relevance:  {float(scores_irr['answer_relevance']):.4f}")
        print(f"    Context Precision: {float(scores_irr['context_precision']):.4f}")

    print("\n" + "="*80)