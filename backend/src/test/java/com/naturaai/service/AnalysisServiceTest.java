package com.naturaai.service;

import com.naturaai.dto.AnalyzeRequest;
import com.naturaai.dto.AnalyzeResponse;
import com.naturaai.model.Herb;
import com.naturaai.model.HerbCombination;
import com.naturaai.model.ToxicityLevel;
import com.naturaai.model.Verdict;
import com.naturaai.repository.HerbCombinationRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Collections;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AnalysisServiceTest {

    @Mock
    private HerbCombinationRepository combinationRepository;
    @Mock
    private HerbService herbService;
    @Mock
    private MlEngineClient mlEngineClient;

    private AnalysisService service() {
        return new AnalysisService(combinationRepository, herbService, mlEngineClient);
    }

    private static AnalyzeRequest request(List<String> ingredients, String remedyType,
                                          AnalyzeRequest.UserProfileDto profile) {
        return new AnalyzeRequest(ingredients, remedyType, profile);
    }

    private static HerbCombination combination(String a, String b, Verdict verdict) {
        return HerbCombination.builder()
                .herbA(a)
                .herbB(b)
                .verdict(verdict)
                .compatibilityScore(90)
                .safetyScore(92)
                .benefitScore(80)
                .scientificConfidence(85)
                .benefits(List.of("Supports digestion"))
                .risks(List.of("May cause mild heartburn"))
                .build();
    }

    @Test
    void analyzeReturnsMlResultWhenEngineSucceeds() {
        AnalyzeResponse ml = new AnalyzeResponse(10, 20, 30, 40, 50, ToxicityLevel.LOW,
                Verdict.SAFE, List.of(), List.of(), List.of(), "q", "f", "r");
        when(mlEngineClient.predict(any())).thenReturn(ml);

        AnalyzeResponse result = service().analyze(request(List.of("Tulsi", "Ginger"), "internal", null));

        assertSame(ml, result);
        verify(combinationRepository, never())
                .findByHerbAIgnoreCaseAndHerbBIgnoreCase(anyString(), anyString());
    }

    @Test
    void analyzeFallsBackToHeuristicWhenEngineFails() {
        when(mlEngineClient.predict(any())).thenThrow(new RuntimeException("down"));

        AnalyzeResponse result = service().analyze(request(List.of("Tulsi", "Ginger"), "internal", null));

        assertNotNull(result);
        assertTrue(result.benefits() != null);
        assertTrue(result.verdict() != null);
    }

    @Test
    void knownSafePairIsSafeWithHighCompatibility() {
        when(combinationRepository.findByHerbAIgnoreCaseAndHerbBIgnoreCase("Mint", "Green Tea"))
                .thenReturn(Optional.of(combination("Mint", "Green Tea", Verdict.SAFE)));

        AnalyzeResponse result = service().heuristicAnalyze(
                request(List.of("Mint", "Green Tea"), "internal", null));

        assertEquals(Verdict.SAFE, result.verdict());
        assertEquals(ToxicityLevel.LOW, result.toxicityLevel());
        assertTrue(result.compatibilityScore() >= 70);
        assertTrue(result.safetyScore() >= 70);
        assertTrue(result.scientificConfidence() >= 50);
    }

    @Test
    void reversedPairIsMatched() {
        when(combinationRepository.findByHerbAIgnoreCaseAndHerbBIgnoreCase("Ginger", "Tulsi"))
                .thenReturn(Optional.empty());
        when(combinationRepository.findByHerbAIgnoreCaseAndHerbBIgnoreCase("Tulsi", "Ginger"))
                .thenReturn(Optional.of(combination("Tulsi", "Ginger", Verdict.SAFE)));

        AnalyzeResponse result = service().heuristicAnalyze(
                request(List.of("Ginger", "Tulsi"), "internal", null));

        assertEquals(Verdict.SAFE, result.verdict());
        assertTrue(result.benefits().contains("Supports digestion"));
    }

    @Test
    void unknownPairIsCautionWithWarning() {
        when(combinationRepository.findByHerbAIgnoreCaseAndHerbBIgnoreCase("Moringa", "Rose"))
                .thenReturn(Optional.empty());
        when(combinationRepository.findByHerbAIgnoreCaseAndHerbBIgnoreCase("Rose", "Moringa"))
                .thenReturn(Optional.empty());

        AnalyzeResponse result = service().heuristicAnalyze(
                request(List.of("Moringa", "Rose"), "internal", null));

        assertEquals(Verdict.CAUTION, result.verdict());
        assertTrue(result.risks().stream()
                .anyMatch(risk -> risk.contains("Limited interaction data available")));
    }

    @Test
    void unsafePairIsUnsafeWithHighToxicity() {
        when(combinationRepository.findByHerbAIgnoreCaseAndHerbBIgnoreCase("Neem", "Honey"))
                .thenReturn(Optional.of(combination("Neem", "Honey", Verdict.UNSAFE)));

        AnalyzeResponse result = service().heuristicAnalyze(
                request(List.of("Neem", "Honey"), "internal", null));

        assertEquals(Verdict.UNSAFE, result.verdict());
        assertEquals(ToxicityLevel.HIGH, result.toxicityLevel());
        assertEquals("Not recommended", result.usageFrequency());
        assertTrue(result.riskScore() > result.safetyScore());
    }

    @Test
    void hazardousHerbAddsWarning() {
        AnalyzeResponse result = service().heuristicAnalyze(
                request(List.of("Honey"), "internal", null));

        assertTrue(result.risks().stream()
                .anyMatch(risk -> risk.contains("Avoid if diabetic")));
    }

    @Test
    void diabetesProfileAddsPersonalizedRisk() {
        AnalyzeRequest.UserProfileDto profile = new AnalyzeRequest.UserProfileDto(
                30, "female", List.of("Diabetes"), List.of(), List.of());
        when(combinationRepository.findByHerbAIgnoreCaseAndHerbBIgnoreCase("Honey", "Ginger"))
                .thenReturn(Optional.empty());
        when(combinationRepository.findByHerbAIgnoreCaseAndHerbBIgnoreCase("Ginger", "Honey"))
                .thenReturn(Optional.empty());

        AnalyzeResponse result = service().heuristicAnalyze(
                request(List.of("Honey", "Ginger"), "internal", profile));

        assertTrue(result.risks().stream()
                .anyMatch(risk -> risk.contains("Honey and other sweetening herbs")));
    }

    @Test
    void duplicateBenefitsAreDeduplicated() {
        Herb tulsi = Herb.builder()
                .name("Tulsi")
                .benefits(List.of("Supports digestion", "Reduces inflammation"))
                .sideEffects(List.of("May cause heartburn"))
                .toxicityLevel(ToxicityLevel.LOW)
                .build();
        when(combinationRepository.findByHerbAIgnoreCaseAndHerbBIgnoreCase("Tulsi", "Ginger"))
                .thenReturn(Optional.of(combination("Tulsi", "Ginger", Verdict.SAFE)));
        when(herbService.findByName("Tulsi")).thenReturn(tulsi);

        AnalyzeResponse result = service().heuristicAnalyze(
                request(List.of("Tulsi", "Ginger"), "internal", null));

        assertEquals(1, Collections.frequency(result.benefits(), "Supports digestion"));
    }

    @Test
    void internalRemedyHasBrewingSteps() {
        AnalyzeResponse result = service().heuristicAnalyze(
                request(List.of("Tulsi"), "internal", null));

        assertTrue(result.preparation().stream()
                .anyMatch(step -> step.contains("Boil 250 ml")));
    }

    @Test
    void externalRemedyHasPatchTestStep() {
        AnalyzeResponse result = service().heuristicAnalyze(
                request(List.of("Tulsi"), "external", null));

        assertTrue(result.preparation().stream()
                .anyMatch(step -> step.contains("Patch-test")));
    }

    @Test
    void scoresAreWithinBounds() {
        when(combinationRepository.findByHerbAIgnoreCaseAndHerbBIgnoreCase("Tulsi", "Ginger"))
                .thenReturn(Optional.of(combination("Tulsi", "Ginger", Verdict.SAFE)));

        AnalyzeResponse result = service().heuristicAnalyze(
                request(List.of("Tulsi", "Ginger"), "internal", null));

        assertTrue(result.compatibilityScore() >= 0 && result.compatibilityScore() <= 100);
        assertTrue(result.safetyScore() >= 0 && result.safetyScore() <= 100);
        assertTrue(result.benefitScore() >= 0 && result.benefitScore() <= 100);
        assertTrue(result.riskScore() >= 0 && result.riskScore() <= 100);
        assertFalse(result.rationale().isBlank());
    }
}
