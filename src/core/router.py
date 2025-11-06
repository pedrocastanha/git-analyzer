from src.core.state import GraphState


def route_after_diff(state: GraphState):
    current_action = state.get("current_action")
    diff = state.get("diff")

    if not diff:
        return "end"

    if current_action == "analyze":
        return "analyze_code"
    elif current_action == "deep_analyze":
        return "deep_analyze_critic"
    elif current_action == "commit":
        return "generate_commit"
    else:
        return "end"


def route_deep_analysis(state: GraphState):
    if state.get("error"):
        print(f"❌ Erro detectado: {state['error']}")
        print("Abortando discussão...\n")
        return "deep_generate_improvements"

    conversation_history = state.get("conversation_history", [])

    if len(conversation_history) >= 18:
        print("⏱️  Limite de 18 mensagens atingido. Finalizando discussão...")
        return "deep_generate_improvements"

    if len(conversation_history) >= 2:
        last_two_messages = conversation_history[-2:]

        agent_names = []
        for msg in last_two_messages:
            if hasattr(msg, "name"):
                agent_names.append(msg.name)

        has_critic = any(name in ["Crítico de Segurança e Padrões", "Security and Standards Critic"] for name in agent_names)
        has_constructive = any(name in ["Construtivo de Lógica e Desempenho", "Logic and Performance Constructive"] for name in agent_names)

        if has_critic and has_constructive:
            agreement_keywords = ["AGREEMENT", "AGREED", "CONCUR", "ACKNOWLEDGE", "CONSENSUS"]

            both_agreed = True
            for msg in last_two_messages:
                content_upper = str(msg.content).upper()
                has_agreement = any(keyword in content_upper for keyword in agreement_keywords)

                if not has_agreement:
                    both_agreed = False
                    break

            if both_agreed:
                print("\n🤝 ACORDO MÚTUO detectado!")
                print("   🔴 Crítico concordou ✓")
                print("   🟢 Construtivo concordou ✓")
                print("   Finalizando discussão...\n")
                return "deep_generate_improvements"

    if conversation_history:
        last_message = conversation_history[-1]
        if hasattr(last_message, "name"):
            if last_message.name in ["Crítico de Segurança e Padrões", "Security and Standards Critic"]:
                return "deep_analyze_constructive"
            elif last_message.name in ["Construtivo de Lógica e Desempenho", "Logic and Performance Constructive"]:
                return "deep_analyze_critic"

    return "deep_analyze_constructive"