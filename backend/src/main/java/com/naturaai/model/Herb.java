package com.naturaai.model;

import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "herbs")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Herb {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name;

    @Column(name = "scientific_name")
    private String scientificName;

    private String family;

    private String region;

    @Column(name = "active_compounds")
    private String activeCompounds;

    @Builder.Default
    @ElementCollection(fetch = FetchType.LAZY)
    private List<String> medicinalProperties = new ArrayList<>();

    @Builder.Default
    @ElementCollection(fetch = FetchType.LAZY)
    private List<String> benefits = new ArrayList<>();

    @Builder.Default
    @ElementCollection(fetch = FetchType.LAZY)
    private List<String> sideEffects = new ArrayList<>();

    @Builder.Default
    @ElementCollection(fetch = FetchType.LAZY)
    private List<String> contraindications = new ArrayList<>();

    @Builder.Default
    @ElementCollection(fetch = FetchType.LAZY)
    private List<String> preparationMethods = new ArrayList<>();

    @Enumerated(EnumType.STRING)
    @Column(name = "toxicity_level")
    private ToxicityLevel toxicityLevel;
}
