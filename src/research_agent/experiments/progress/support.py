"""Concrete progress collaborators, selected together at composition."""

from . import review, objective_review
from .control import evaluation_policy, reconciliation_policy
from .objectives import EvaluationState, digest
from .observations import OperationalObserver
from .external_review import knowledge
from ...continuity import assessment_context

DECISION_DIRECTION = "Elige la siguiente acción por su capacidad de mejorar la evaluación y resolver un impedimento material para decidir. Distingue obtener evidencia, calcular e interpretar información ya disponible. No amplíes la investigación sin explicar su contribución al resultado. Tras la exploración inicial construye y revisa el juicio provisional en el documento de evaluación indicado, con fundamentos, precio/escenarios, riesgos y bloqueos concretos. No inventes una recomendación ni esperes a terminar toda recopilación para razonar. Si un método no resuelve un bloqueo, expresa qué harás distinto y qué resultado observable esperas; comprueba después si funcionó. La distancia es secundaria a la utilidad para decidir. Mantén la agenda compacta: foco, impedimento, siguiente acción y referencias; el análisis vive en sus documentos."
