#!/usr/bin/env python3
"""
Debug script to analyze text processing and sentence splitting
"""

import sys
import os

# Add backend/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from strategies.feature_extractor import FeatureExtractor
from strategies.stage_macro import MacroStageEvaluator
from strategies.stage_meso import MesoStageEvaluator
from strategies.cascade_orchestrator import CascadeOrchestrator
from services.strategy_detector import StrategyDetector

def debug_text_processing():
    """Debug text processing pipeline"""

    # Source text (from test_files/text_pairs/texto-fonte.txt)
    source_text = """**Saúde da mulher: uma abordagem integral a partir de perspectivas contemporâneas**

A saúde da mulher, enquanto campo de estudos e práticas clínicas, demanda uma abordagem integral que transcenda os aspectos meramente biológicos e reconheça a complexidade das interações entre fatores fisiológicos, sociais, culturais e políticos. Embora muitos dos agravos à saúde feminina estejam ancorados em fatores comuns à saúde geral da população, há especificidades que exigem um olhar técnico e crítico, especialmente no que tange às particularidades do ciclo reprodutivo, às doenças ginecológicas prevalentes e às iniquidades de gênero que ainda estruturam o acesso e a qualidade do cuidado.

Do ponto de vista biomédico, é fundamental considerar os processos fisiológicos relacionados à menarca, gestação, parto, puerpério e menopausa como fenômenos que, embora naturais, são frequentemente medicalizados de maneira excessiva ou inadequada. A ginecologia e a obstetrícia modernas têm avançado na promoção de práticas baseadas em evidências que respeitam a autonomia das pacientes, reconhecendo a importância do consentimento informado e da escuta qualificada como fundamentos éticos e clínicos indispensáveis. Nesse contexto, a incorporação de tecnologias reprodutivas e métodos contraceptivos diversificados deve ser orientada por princípios de justiça reprodutiva, assegurando o direito ao planejamento familiar e à autodeterminação corporal.

Quanto às patologias mais incidentes, destaca-se a alta prevalência de endometriose, síndrome dos ovários policísticos (SOP), miomas uterinos e disfunções hormonais associadas ao eixo hipotálamo-hipófise-ovariano. Tais condições demandam estratégias diagnósticas que superem a negligência histórica dos relatos de dor e desconforto feminino no contexto clínico. A dor pélvica crônica, por exemplo, ainda é subvalorizada em muitos serviços de saúde, refletindo um viés androcêntrico persistente na prática médica.

Além disso, o campo da saúde mental tem demonstrado a necessidade de abordagens específicas para mulheres, dado que os transtornos depressivos, de ansiedade e alimentares apresentam maior prevalência no sexo feminino, muitas vezes em decorrência de violências estruturais, sobrecarga de trabalho reprodutivo e desigualdade nas relações de poder. A integração entre atenção psicossocial e serviços de saúde física deve ser uma prioridade em políticas públicas que busquem equidade de gênero na saúde.

Por fim, é imprescindível reconhecer que a saúde da mulher não se resume à função reprodutiva. A abordagem centrada exclusivamente no aparelho genital feminino desconsidera a multiplicidade de experiências e identidades das mulheres. Mulheres trans, por exemplo, enfrentam barreiras significativas ao acesso a serviços de saúde adequados, exigindo práticas que sejam verdadeiramente inclusivas e sensíveis à diversidade de corpos e vivências.

Assim, uma política de saúde da mulher efetiva deve ser orientada por princípios de equidade, autonomia e integralidade, incorporando não apenas o conhecimento técnico-científico mais atual, mas também uma perspectiva crítica que reconheça o impacto das relações de gênero na produção do adoecimento e na vivência da saúde. A formação profissional contínua, a implementação de protocolos clínicos com viés interseccional e a escuta ativa das usuárias dos serviços são estratégias fundamentais para superar as lacunas históricas e promover um cuidado que valorize a dignidade, a pluralidade e os direitos das mulheres em todas as fases do ciclo vital."""

    # Target text (from test_files/text_pairs/texto-alvo.txt)
    target_text = """Saúde da mulher: entender para cuidar melhor

Falar sobre saúde da mulher é ir muito além do corpo. É entender que fatores como alimentação, emoções, cultura, desigualdade de gênero e até decisões políticas afetam diretamente o bem-estar das mulheres. Mesmo que alguns problemas de saúde sejam comuns a todas as pessoas, existem questões específicas que precisam ser tratadas com atenção e respeito.

Durante a vida, o corpo da mulher passa por muitas mudanças: a primeira menstruação, a possibilidade de engravidar, o parto, o pós-parto e a menopausa. Esses momentos são naturais, mas, muitas vezes, são tratados como doenças. Felizmente, a medicina tem avançado e hoje há mais respeito pelas escolhas das mulheres. O uso de métodos contraceptivos e tecnologias reprodutivas, por exemplo, deve sempre levar em conta o direito de cada pessoa decidir sobre o próprio corpo.

Algumas doenças afetam muitas mulheres, como a endometriose, a síndrome dos ovários policísticos (SOP) e os miomas. Essas condições podem causar dor e outros sintomas difíceis de lidar. Infelizmente, por muito tempo, os relatos das pacientes foram ignorados ou minimizados nos atendimentos médicos. A dor pélvica crônica, por exemplo, ainda é pouco valorizada em muitos consultórios.

A saúde mental também merece atenção. Mulheres são mais afetadas por depressão, ansiedade e distúrbios alimentares. Isso tem relação com a sobrecarga de tarefas, o preconceito e diferentes formas de violência — que podem ser físicas, psicológicas ou até institucionais. Por isso, é importante que o cuidado com a saúde envolva o corpo e também a mente.

Outro ponto importante é lembrar que ser mulher não está ligado apenas à capacidade de ter filhos. Focar só no aparelho reprodutor deixa de fora muitas realidades. Mulheres trans, por exemplo, enfrentam grandes dificuldades para acessar cuidados básicos de saúde. A inclusão e o respeito à diversidade precisam estar no centro de qualquer política pública voltada à saúde da mulher.

Promover a saúde feminina é garantir o direito à informação, ao cuidado de qualidade e ao respeito. Isso exige profissionais preparados, políticas públicas justas e um olhar sensível para a pluralidade das experiências. Afinal, toda mulher merece viver com dignidade e ser ouvida em todas as fases da vida."""

    print("🔍 DEBUGGING TEXT PROCESSING PIPELINE")
    print("=" * 60)

    # Test sentence splitting
    print("\n📝 TESTING SENTENCE SPLITTING")
    print("-" * 40)

    # Test with spaCy if available
    try:
        import spacy
        nlp = spacy.load("pt_core_news_sm")
        print("✅ spaCy Portuguese model loaded")

        src_doc = nlp(source_text)
        tgt_doc = nlp(target_text)

        src_sentences = [sent.text.strip() for sent in src_doc.sents if sent.text.strip()]
        tgt_sentences = [sent.text.strip() for sent in tgt_doc.sents if sent.text.strip()]

        print(f"Source sentences (spaCy): {len(src_sentences)}")
        print(f"Target sentences (spaCy): {len(tgt_sentences)}")

        print("\nFirst 5 source sentences:")
        for i, sent in enumerate(src_sentences[:5]):
            print(f"  {i+1}: {sent[:80]}{'...' if len(sent) > 80 else ''}")

        print("\nFirst 5 target sentences:")
        for i, sent in enumerate(tgt_sentences[:5]):
            print(f"  {i+1}: {sent[:80]}{'...' if len(sent) > 80 else ''}")

    except Exception as e:
        print(f"❌ spaCy not available: {e}")

        # Fallback to regex
        import re
        src_sentences = re.split(r'(?<=[.!?])\s+', source_text)
        tgt_sentences = re.split(r'(?<=[.!?])\s+', target_text)

        print(f"Source sentences (regex): {len(src_sentences)}")
        print(f"Target sentences (regex): {len(tgt_sentences)}")

    # Test feature extraction
    print("\n🔧 TESTING FEATURE EXTRACTION")
    print("-" * 40)

    try:
        extractor = FeatureExtractor()
        features = extractor.extract_features(source_text, target_text)

        print("✅ Feature extraction successful")
        print(f"Semantic similarity: {features.semantic_similarity:.3f}")
        print(f"Lexical overlap: {features.lexical_overlap:.3f}")
        print(f"Length ratio: {features.length_ratio:.3f}")
        print(f"Sentence count ratio: {features.sentence_count_ratio:.3f}")

    except Exception as e:
        print(f"❌ Feature extraction failed: {e}")

    # Test macro stage
    print("\n🏗️ TESTING MACRO STAGE")
    print("-" * 40)

    try:
        macro_evaluator = MacroStageEvaluator()
        macro_evidences, should_continue = macro_evaluator.evaluate(
            features, source_text, target_text, complete_analysis_mode=True
        )

        print(f"✅ Macro stage completed: {len(macro_evidences)} strategies detected")
        print(f"Should continue to meso: {should_continue}")

        for evidence in macro_evidences:
            print(f"  - {evidence.strategy_code}: {evidence.confidence:.3f}")

    except Exception as e:
        print(f"❌ Macro stage failed: {e}")

    # Test meso stage
    print("\n🔬 TESTING MESO STAGE")
    print("-" * 40)

    try:
        meso_evaluator = MesoStageEvaluator()
        meso_evidences, should_continue = meso_evaluator.evaluate(
            features, source_text, target_text, complete_analysis_mode=True
        )

        print(f"✅ Meso stage completed: {len(meso_evidences)} strategies detected")
        print(f"Should continue to micro: {should_continue}")

        for evidence in meso_evidences:
            print(f"  - {evidence.strategy_code}: {evidence.confidence:.3f}")

    except Exception as e:
        print(f"❌ Meso stage failed: {e}")

    # Test cascade orchestrator
    print("\n🎭 TESTING CASCADE ORCHESTRATOR")
    print("-" * 40)

    try:
        orchestrator = CascadeOrchestrator(complete_analysis_mode=True)
        strategies = orchestrator.detect_strategies(source_text, target_text)

        print(f"✅ Cascade orchestrator completed: {len(strategies)} strategies detected")

        for strategy in strategies:
            print(f"  - {strategy.sigla}: {strategy.confianca:.3f} ({strategy.nome})")

    except Exception as e:
        print(f"❌ Cascade orchestrator failed: {e}")

if __name__ == "__main__":
    debug_text_processing()