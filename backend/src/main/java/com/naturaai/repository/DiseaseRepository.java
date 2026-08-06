package com.naturaai.repository;

import com.naturaai.model.Disease;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface DiseaseRepository extends JpaRepository<Disease, Long> {

    Optional<Disease> findByNameIgnoreCase(String name);
}
