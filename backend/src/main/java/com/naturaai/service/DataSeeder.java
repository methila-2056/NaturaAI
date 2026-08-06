package com.naturaai.service;

import com.naturaai.model.Disease;
import com.naturaai.model.Herb;
import com.naturaai.model.HerbCombination;
import com.naturaai.model.ToxicityLevel;
import com.naturaai.model.Verdict;
import com.naturaai.repository.DiseaseRepository;
import com.naturaai.repository.HerbCombinationRepository;
import com.naturaai.repository.HerbRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class DataSeeder implements CommandLineRunner {

    private final HerbRepository herbRepository;
    private final HerbCombinationRepository combinationRepository;
    private final DiseaseRepository diseaseRepository;

    public DataSeeder(HerbRepository herbRepository,
                      HerbCombinationRepository combinationRepository,
                      DiseaseRepository diseaseRepository) {
        this.herbRepository = herbRepository;
        this.combinationRepository = combinationRepository;
        this.diseaseRepository = diseaseRepository;
    }

    @Override
    public void run(String... args) {
        if (herbRepository.count() == 0) {
            seedHerbs();
        }
        if (combinationRepository.count() == 0) {
            seedCombinations();
        }
        if (diseaseRepository.count() == 0) {
            seedDiseases();
        }
    }

    private void seedHerbs() {
        herbRepository.saveAll(List.of(
                herb("Tulsi", "Ocimum tenuiflorum", "Lamiaceae", "South Asia",
                        "Antioxidant, anti-inflammatory, immunomodulator",
                        List.of("Supports immunity", "Reduces stress", "Eases cold and cough"),
                        List.of("May lower blood sugar", "Avoid large doses in pregnancy"),
                        ToxicityLevel.LOW),
                herb("Neem", "Azadirachta indica", "Meliaceae", "Indian subcontinent",
                        "Antibacterial, antifungal, antiseptic",
                        List.of("Improves skin health", "Fights acne", "Supports oral hygiene"),
                        List.of("Strong doses may cause nausea", "Not for internal use in pregnancy"),
                        ToxicityLevel.LOW),
                herb("Turmeric", "Curcuma longa", "Zingiberaceae", "South Asia",
                        "Curcumin, antioxidant, anti-inflammatory",
                        List.of("Reduces inflammation", "Supports joints", "Aids digestion"),
                        List.of("May interact with blood thinners", "High doses upset stomach"),
                        ToxicityLevel.LOW),
                herb("Ginger", "Zingiber officinale", "Zingiberaceae", "South Asia",
                        "Gingerol, antiemetic, warming",
                        List.of("Relieves nausea", "Improves digestion", "Soothes throat"),
                        List.of("Caution with anticoagulants", "Heartburn at high doses"),
                        ToxicityLevel.LOW),
                herb("Aloe Vera", "Aloe barbadensis", "Asphodelaceae", "North Africa",
                        "Polysaccharides, anthraquinones, soothing",
                        List.of("Hydrates skin", "Soothes burns", "Improves hair condition"),
                        List.of("Internal latex may cause cramps", "Avoid in pregnancy"),
                        ToxicityLevel.LOW),
                herb("Ashwagandha", "Withania somnifera", "Solanaceae", "India",
                        "Withanolides, adaptogenic",
                        List.of("Reduces stress", "Improves sleep", "Supports energy"),
                        List.of("Caution with thyroid medication", "May cause drowsiness"),
                        ToxicityLevel.LOW),
                herb("Brahmi", "Bacopa monnieri", "Plantaginaceae", "Wetlands of India",
                        "Bacosides, nootropic",
                        List.of("Improves memory", "Supports focus", "Calms the mind"),
                        List.of("May cause mild digestive upset"),
                        ToxicityLevel.LOW),
                herb("Hibiscus", "Hibiscus sabdariffa", "Malvaceae", "West Africa, Asia",
                        "Anthocyanins, vitamin C, mild hypotensive",
                        List.of("Promotes hair growth", "Supports heart health", "Rich in antioxidants"),
                        List.of("May lower blood pressure", "Caution in pregnancy"),
                        ToxicityLevel.LOW),
                herb("Honey", "Apis mellifera product", "N/A", "Global",
                        "Flavonoids, natural sugars, antimicrobial",
                        List.of("Soothes sore throat", "Natural sweetener", "Antimicrobial"),
                        List.of("Avoid if diabetic", "Not for infants under 1 year"),
                        ToxicityLevel.LOW),
                herb("Moringa", "Moringa oleifera", "Moringaceae", "South Asia",
                        "Vitamins A/C, iron, polyphenols",
                        List.of("Boosts nutrition", "Supports energy", "Antioxidant rich"),
                        List.of("Leaf may interact with thyroid medication", "High doses laxative"),
                        ToxicityLevel.LOW),
                herb("Rose", "Rosa damascena", "Rosaceae", "Middle East",
                        "Essential oils, vitamin C, astringent",
                        List.of("Calms skin", "Aromatic", "Mild astringent"),
                        List.of("Rare contact dermatitis"),
                        ToxicityLevel.LOW),
                herb("Mint", "Mentha piperita", "Lamiaceae", "Europe, Asia",
                        "Menthol, cooling compounds",
                        List.of("Aids digestion", "Cools the body", "Freshens breath"),
                        List.of("Heartburn in sensitive people", "Avoid with GERD"),
                        ToxicityLevel.LOW),
                herb("Amla", "Phyllanthus emblica", "Phyllanthaceae", "India",
                        "Vitamin C, tannins, antioxidants",
                        List.of("Rich in vitamin C", "Improves hair", "Supports immunity"),
                        List.of("May irritate empty stomach"),
                        ToxicityLevel.LOW),
                herb("Fenugreek", "Trigonella foenum-graecum", "Fabaceae", "Mediterranean",
                        "Saponins, fiber, amino acids",
                        List.of("Lowers blood sugar", "Promotes hair growth", "Supports lactation"),
                        List.of("May lower blood sugar too much", "Maple-scented body odour"),
                        ToxicityLevel.LOW),
                herb("Green Tea", "Camellia sinensis", "Theaceae", "East Asia",
                        "Catechins, caffeine, L-theanine",
                        List.of("Antioxidant rich", "Boosts metabolism", "Supports focus"),
                        List.of("Caffeine sensitivity", "Iron absorption reduced"),
                        ToxicityLevel.LOW)
        ));
    }

    private void seedCombinations() {
        combinationRepository.saveAll(List.of(
                combo("Tulsi", "Ginger", Verdict.SAFE, 97, 92, 95, 8, 90,
                        List.of("Synergistic immune support", "Soothing for cold and cough"),
                        List.of("Limit honey if diabetic")),
                combo("Tulsi", "Honey", Verdict.SAFE, 95, 90, 92, 10, 88,
                        List.of("Combined antimicrobial effect"),
                        List.of("Honey raises blood sugar")),
                combo("Ginger", "Honey", Verdict.SAFE, 94, 89, 90, 11, 87,
                        List.of("Classic sore-throat remedy"),
                        List.of("Honey not for infants")),
                combo("Neem", "Aloe Vera", Verdict.SAFE, 94, 88, 93, 10, 86,
                        List.of("Acne-fighting synergy for face washes"),
                        List.of("Patch test before full use")),
                combo("Ashwagandha", "Brahmi", Verdict.SAFE, 95, 87, 94, 12, 88,
                        List.of("Cognitive calm and stress support"),
                        List.of("Drowsiness possible")),
                combo("Hibiscus", "Coconut Oil", Verdict.SAFE, 91, 90, 92, 9, 84,
                        List.of("Hair growth and scalp conditioning"),
                        List.of("Oily scalp may need less frequent use")),
                combo("Turmeric", "Black Pepper", Verdict.SAFE, 96, 91, 97, 9, 92,
                        List.of("Piperine boosts curcumin absorption 20-fold"),
                        List.of("Mild stomach irritation possible")),
                combo("Honey", "Cinnamon", Verdict.CAUTION, 78, 72, 80, 22, 75,
                        List.of("Traditional warming blend"),
                        List.of("Cinnamon high doses may affect liver", "Honey raises blood sugar")),
                combo("Ginger", "Ashwagandha", Verdict.SAFE, 90, 86, 89, 14, 82,
                        List.of("Warming and grounding blend"),
                        List.of("Caution with sedatives"))
        ));
    }

    private void seedDiseases() {
        diseaseRepository.saveAll(List.of(
                disease("Common Cold",
                        List.of("Runny nose", "Sore throat", "Cough", "Fatigue"),
                        List.of("Tulsi", "Ginger", "Honey"),
                        List.of()),
                disease("Diabetes",
                        List.of("High blood sugar", "Fatigue", "Thirst"),
                        List.of("Fenugreek", "Cinnamon", "Neem"),
                        List.of("Honey", "Sugar-containing syrups")),
                disease("Hypertension",
                        List.of("High blood pressure", "Headache", "Dizziness"),
                        List.of("Hibiscus", "Garlic"),
                        List.of("Licorice")),
                disease("Hair Loss",
                        List.of("Thinning hair", "Scalp exposure"),
                        List.of("Hibiscus", "Amla", "Fenugreek", "Coconut Oil"),
                        List.of()),
                disease("Acne",
                        List.of("Pimples", "Inflammation", "Oily skin"),
                        List.of("Neem", "Aloe Vera", "Tea Tree"),
                        List.of("Heavy oils that clog pores"))
        ));
    }

    private Herb herb(String name, String scientificName, String family, String region,
                      String compounds, List<String> benefits, List<String> sideEffects,
                      ToxicityLevel toxicity) {
        return Herb.builder()
                .name(name)
                .scientificName(scientificName)
                .family(family)
                .region(region)
                .activeCompounds(compounds)
                .medicinalProperties(List.of(compounds))
                .benefits(benefits)
                .sideEffects(sideEffects)
                .contraindications(sideEffects)
                .preparationMethods(List.of("Infusion", "Decoction", "Oil infusion"))
                .toxicityLevel(toxicity)
                .build();
    }

    private HerbCombination combo(String a, String b, Verdict verdict, int compatibility,
                                  int safety, int benefit, int risk, int confidence,
                                  List<String> benefits, List<String> risks) {
        return HerbCombination.builder()
                .herbA(a).herbB(b)
                .verdict(verdict)
                .compatibilityScore(compatibility)
                .safetyScore(safety)
                .benefitScore(benefit)
                .riskScore(risk)
                .scientificConfidence(confidence)
                .benefits(benefits)
                .risks(risks)
                .toxicityLevel(verdict == Verdict.UNSAFE ? "HIGH" : "LOW")
                .build();
    }

    private Disease disease(String name, List<String> symptoms, List<String> recommended, List<String> avoid) {
        return Disease.builder()
                .name(name)
                .symptoms(symptoms)
                .recommendedHerbs(recommended)
                .avoidHerbs(avoid)
                .build();
    }
}
