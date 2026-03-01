# LLD 참조: docs/arch/LLD/hub/anonymizer.md
class AnonymizerService:
    """PII 제거 5단계 파이프라인"""

    async def anonymize(self, content: str, epsilon: float = 0.5):
        # TODO: Step1 NER → Step2 문맥익명화 → Step3 차등프라이버시 → Step4 의미보존 → Step5 신뢰도
        raise NotImplementedError
