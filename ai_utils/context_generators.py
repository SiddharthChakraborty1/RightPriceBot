from ai_utils.constants import CONTEXT_MESSAGES


class DefaultContextGenerator:
    @classmethod
    def basic_context(cls):
        return CONTEXT_MESSAGES.get(
            "basic", "Return the number 0 for every question"
        )
