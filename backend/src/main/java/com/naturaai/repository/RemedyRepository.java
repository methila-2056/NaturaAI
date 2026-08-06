package com.naturaai.repository;

import com.naturaai.model.Remedy;
import com.naturaai.model.TreatmentType;
import com.naturaai.model.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface RemedyRepository extends JpaRepository<Remedy, Long> {

    List<Remedy> findByCreatedBy(User user);

    List<Remedy> findByTreatmentType(TreatmentType treatmentType);
}
