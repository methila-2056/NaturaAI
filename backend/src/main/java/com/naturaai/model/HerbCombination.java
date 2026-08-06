package com.naturaai.model;

import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "herb_combinations")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class HerbCombination {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "herb_a", nullable = false)
    private String herbA;

    @Column(name = "herb_b", nullable = false)
    private String herbB;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Verdict verdict;

    @Column(name = "compatibility_score")
    private Integer compatibilityScore;

    @Column(name = "safety_score")
    private Integer safetyScore;

    @Column(name = "benefit_score")
    private Integer benefitScore;

    @Column(name = "risk_score")
    private Integer riskScore;

    @Column(name = "scientific_confidence")
    private Integer scientificConfidence;

    @Builder.Default
    @ElementCollection(fetch = FetchType.LAZY)
    @CollectionTable(name = "herb_combination_benefits", joinColumns = @JoinColumn(name = "combination_id"))
    @Column(name = "benefits")
    private List<String> benefits = new ArrayList<>();

    @Builder.Default
    @ElementCollection(fetch = FetchType.LAZY)
    @CollectionTable(name = "herb_combination_risks", joinColumns = @JoinColumn(name = "combination_id"))
    @Column(name = "risks")
    private List<String> risks = new ArrayList<>();

    @Column(name = "toxicity_level")
    private String toxicityLevel;
}
