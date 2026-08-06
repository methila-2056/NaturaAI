package com.naturaai.dto;

import com.naturaai.model.ToxicityLevel;
import com.naturaai.model.Verdict;

import java.util.List;

public record AnalyzeResponse(
        int compatibilityScore,
        int safetyScore,
        int benefitScore,
        int riskScore,
        int scientificConfidence,
        ToxicityLevel toxicityLevel,
        Verdict verdict,
        List<String> benefits,
        List<String> risks,
        List<String> preparation,
        String quantity,
        String usageFrequency,
        String rationale
) {
}
