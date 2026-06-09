#!/usr/bin/env python
"""
Script para generar evaluaciones en CSV usando Ragas.
"""
import os
import sys
import csv

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.evaluator import evaluate_rag_performance

def generate_csv():
    questions = [
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

    # Crear directorio si no existe
    os.makedirs("data", exist_ok=True)

    csv_path = "data/evaluation_results.csv"
    
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Pregunta",
            "Tipo de Contexto",
            "Faithfulness",
            "Answer Relevance",
            "Context Precision",
        ])

        for i, q in enumerate(questions):
            print(f"Evaluando pregunta {i+1}/4: {q[:50]}...")
            
            # Contexto autoritativo
            auth_ctx = [authoritative_contexts[i]]
            auth_answer = authoritative_contexts[i]
            scores_auth = evaluate_rag_performance(q, auth_ctx, auth_answer, reference=auth_answer)

            writer.writerow([
                q,
                "Autoritativo",
                float(scores_auth['faithfulness']),
                float(scores_auth['answer_relevance']),
                float(scores_auth['context_precision']),
            ])

            # Contexto irrelevante
            irr_ctx = irrelevant_contexts[i]
            irr_answer = "No encuentro esa información en los documentos proporcionados."
            scores_irr = evaluate_rag_performance(q, irr_ctx, irr_answer, reference=irr_answer)

            writer.writerow([
                q,
                "Irrelevante",
                float(scores_irr['faithfulness']),
                float(scores_irr['answer_relevance']),
                float(scores_irr['context_precision']),
            ])

    print(f"\nCSV generado: {csv_path}")
    print(f"Total de filas: 8 (4 preguntas × 2 contextos)")

if __name__ == "__main__":
    generate_csv()
