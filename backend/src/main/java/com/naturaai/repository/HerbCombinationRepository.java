package com.naturaai.repository;

import com.naturaai.model.HerbCombination;
import com.naturaai.model.Verdict;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface HerbCombinationRepository extends JpaRepository<HerbCombination, Long> {

    Optional<HerbCombination> findByHerbAIgnoreCaseAndHerbBIgnoreCase(String herbA, String herbB);

    List<HerbCombination> findByHerbAInIgnoreCase(List<String> herbs);

    long countByVerdict(Verdict verdict);
}
