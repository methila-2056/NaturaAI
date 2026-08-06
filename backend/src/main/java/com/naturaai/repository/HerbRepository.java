package com.naturaai.repository;

import com.naturaai.model.Herb;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface HerbRepository extends JpaRepository<Herb, Long> {

    Optional<Herb> findByNameIgnoreCase(String name);

    List<Herb> findByNameContainingIgnoreCase(String name);

    List<Herb> findByMedicinalPropertiesContainingIgnoreCase(String property);
}
