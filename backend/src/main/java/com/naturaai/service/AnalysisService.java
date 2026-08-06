package com.naturaai.service;

import com.naturaai.dto.AnalyzeRequest;
import com.naturaai.dto.AnalyzeResponse;
import com.naturaai.model.Herb;
import com.naturaai.model.HerbCombination;
import com.naturaai.model.ToxicityLevel;
import com.naturaai.model.Verdict;
import com.naturaai.repository.HerbCombinationRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/**
 * Rule-based compatibility engine. Used as a fallback when the ML engine is
 * unavailable, and to personalize the ML result with profile context.
 */
@Service
public class AnalysisService {

    private static final Logger log = LoggerFactory.getLogger(AnalysisService.class);

    private static final Map<String, String> HERB_HAZARDS = Map.ofEntries(
            Map.entry("honey", "Avoid if diabetic"),
            Map.entry("aloe vera", "Internal use not recommended during pregnancy"),
            Map.entry("fenugreek", "May lower blood sugar; monitor if on antidiabetic medication"),
            Map.entry("ashwagandha", "Caution with sedatives and thyroid medication"),
            Map.entry("ginger", "Caution with blood thinners at high doses"),
            Map.entry("tulsi", "Caution with anticoagulants at very high doses"),
            Map.entry("cinnamon", "High doses may affect liver; caution with anticoagulants"),
            Map.entry("licorice", "Avoid with hypertension and low potassium"),
            Map.entry("ginkgo", "May interact with blood thinners"),
            Map.entry("kava", "Hepatotoxicity risk; avoid with liver disease")
    );

    private final HerbCombinationRepository combinationRepository;
    private final HerbService herbService;
    private final MlEngineClient mlEngineClient;

    public AnalysisService(
            HerbCombinationRepository combinationRepository,
            HerbService herbService,
            MlEngineClient mlEngineClient) {
        this.combinationRepository = combinationRepository;
        this.herbService = herbService;
        this.mlEngineClient = mlEngineClient;
    }

    public AnalyzeResponse analyze(AnalyzeRequest request) {
        try {
            return mlEngineClient.predict(request);
        } catch (Exception ex) {
            log.warn("ML engine predict failed for {}; falling back to heuristic", request.ingredients(), ex);
            return heuristicAnalyze(request);
        }
    }

    AnalyzeResponse heuristicAnalyze(AnalyzeRequest request) {
        List<String> ingredients = request.ingredients();
        List<String> benefits = new ArrayList<>();
        List<String> risks = new ArrayList<>();
        Set<Verdict> verdicts = new LinkedHashSet<>();
        List<HerbCombination> known = new ArrayList<>();
        int unknownPairs = 0;
        int hazardNotes = 0;

        for (int i = 0; i < ingredients.size(); i++) {
            for (int j = i + 1; j < ingredients.size(); j++) {
                HerbCombination combo = lookup(ingredients.get(i), ingredients.get(j));
                if (combo != null) {
                    known.add(combo);
                    verdicts.add(combo.getVerdict());
                    benefits.addAll(combo.getBenefits());
                    risks.addAll(combo.getRisks());
                } else {
                    unknownPairs++;
                    verdicts.add(Verdict.CAUTION);
                    risks.add("Limited interaction data available for "
                            + ingredients.get(i) + " + " + ingredients.get(j)
                            + "; consult a healthcare professional before use.");
                }
            }
        }

        for (String ingredient : ingredients) {
            Herb herb = herbService.findByName(ingredient);
            if (herb != null) {
                benefits.addAll(herb.getBenefits());
                risks.addAll(herb.getSideEffects());
                if (herb.getToxicityLevel() != ToxicityLevel.LOW) {
                    hazardNotes++;
                }
            }
            String hazard = HERB_HAZARDS.get(ingredient.toLowerCase(Locale.ROOT));
            if (hazard != null) {
                hazardNotes++;
                risks.add(ingredient + ": " + hazard);
            }
        }

        personalize(request, risks, benefits);

        benefits = dedupe(benefits);
        risks = dedupe(risks);

        double averageConfidence = known.isEmpty()
                ? 55.0
                : known.stream().mapToInt(c -> safe(c.getScientificConfidence(), 80)).average().orElse(80);

        Verdict verdict = verdicts.contains(Verdict.UNSAFE) ? Verdict.UNSAFE
                : verdicts.contains(Verdict.CAUTION) ? Verdict.CAUTION
                : Verdict.SAFE;

        int baseCompatibility = switch (verdict) {
            case SAFE -> 90;
            case CAUTION -> 68;
            case UNSAFE -> 40;
        };
        if (!known.isEmpty()) {
            baseCompatibility = (int) Math.round(known.stream()
                    .mapToInt(c -> safe(c.getCompatibilityScore(), 80))
                    .average()
                    .orElse(90));
        }
        int penalty = Math.min(20, unknownPairs * 10) + Math.min(10, hazardNotes) * 2;
        int compatibility = Math.max(20, Math.min(98, baseCompatibility - penalty));

        int safety = switch (verdict) {
            case UNSAFE -> 25;
            case CAUTION -> Math.max(45, 62 - hazardNotes * 3);
            case SAFE -> Math.max(70, 90 - hazardNotes * 4);
        };
        int risk = 100 - safety;
        int benefitBase = switch (verdict) {
            case SAFE -> 84;
            case CAUTION -> 68;
            case UNSAFE -> 48;
        };
        int benefit = Math.min(98, benefitBase + Math.min(12, benefits.size()));

        boolean internal = "internal".equalsIgnoreCase(request.remedyType());

        return new AnalyzeResponse(
                compatibility,
                safety,
                benefit,
                risk,
                (int) averageConfidence,
                toxicity(verdict, hazardNotes),
                verdict,
                limit(benefits, 6),
                limit(risks, 6),
                preparationSteps(request, ingredients, internal),
                quantity(internal, ingredients.size()),
                usageFrequency(internal, verdict),
                rationale(request, verdict, ingredients, risks)
        );
    }

    private void personalize(AnalyzeRequest request, List<String> risks, List<String> benefits) {
        if (request.profile() == null) {
            return;
        }
        List<String> diseases = request.profile().diseases() == null ? List.of() : request.profile().diseases();
        List<String> allergies = request.profile().allergies() == null ? List.of() : request.profile().allergies();

        for (String disease : diseases) {
            String key = disease.toLowerCase(Locale.ROOT);
            if (key.contains("diabet")) {
                risks.add("Honey and other sweetening herbs may raise blood sugar — limited for diabetics.");
            }
            if (key.contains("hypertension")) {
                risks.add("Licorice and high-sodium preparations may raise blood pressure.");
            }
            if (key.contains("pcos") || key.contains("thyroid")) {
                risks.add("Hormone-active herbs (fenugreek, ashwagandha) may interfere with hormonal balance.");
            }
        }

        for (String allergy : allergies) {
            String key = allergy.toLowerCase(Locale.ROOT);
            if (key.contains("pollen")) {
                risks.add("Individuals with pollen allergy may cross-react with chamomile and tulsi.");
            }
            if (key.contains("nuts")) {
                risks.add("Check for nut-based carrier oils in external formulations.");
            }
        }
    }

    private HerbCombination lookup(String a, String b) {
        HerbCombination combo = combinationRepository.findByHerbAIgnoreCaseAndHerbBIgnoreCase(a, b).orElse(null);
        if (combo == null) {
            combo = combinationRepository.findByHerbAIgnoreCaseAndHerbBIgnoreCase(b, a).orElse(null);
        }
        return combo;
    }

    private ToxicityLevel toxicity(Verdict verdict, int hazardNotes) {
        if (verdict == Verdict.UNSAFE) {
            return ToxicityLevel.HIGH;
        }
        if (verdict == Verdict.CAUTION || hazardNotes > 0) {
            return ToxicityLevel.MEDIUM;
        }
        return ToxicityLevel.LOW;
    }

    private List<String> preparationSteps(AnalyzeRequest request, List<String> ingredients, boolean internal) {
        List<String> steps = new ArrayList<>();
        if (internal) {
            steps.add("Boil 250 ml of filtered water.");
            steps.add("Add " + String.join(", ", ingredients) + " and steep for 5–8 minutes.");
            steps.add("Strain and consume warm.");
        } else {
            steps.add("Combine " + String.join(", ", ingredients) + " with a suitable base carrier.");
            steps.add("Blend into a smooth, even consistency.");
            steps.add("Patch-test on a small skin area before full application.");
        }
        return steps;
    }

    private String quantity(boolean internal, int ingredientCount) {
        if (internal) {
            return "1 cup (250 ml), using " + (1 + ingredientCount) + " g total of dried herbs";
        }
        return "Small handful per application (10–15 g)";
    }

    private String usageFrequency(boolean internal, Verdict verdict) {
        if (verdict == Verdict.UNSAFE) {
            return "Not recommended";
        }
        return internal ? "Daily (max twice daily for up to 2 weeks)" : "2–3 times per week";
    }

    private String rationale(AnalyzeRequest request, Verdict verdict, List<String> ingredients, List<String> risks) {
        String base = "Based on your profile, " + String.join(" + ", ingredients)
                + " appears " + verdict.name().toLowerCase(Locale.ROOT)
                + " for " + request.remedyType() + " use.";
        if (verdict == Verdict.CAUTION && !risks.isEmpty()) {
            return base + " Caution advised: " + risks.get(0) + ".";
        }
        return base + " Follow the recommended dosage and stop use if any adverse reaction occurs.";
    }

    private static int safe(Integer value, int fallback) {
        return value == null ? fallback : value;
    }

    private static List<String> dedupe(List<String> items) {
        return new ArrayList<>(new LinkedHashSet<>(items));
    }

    private static List<String> limit(List<String> items, int max) {
        return items.size() <= max ? items : new ArrayList<>(items.subList(0, max));
    }
}
