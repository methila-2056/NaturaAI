package com.naturaai.repository;

import com.naturaai.model.Recommendation;
import com.naturaai.model.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface RecommendationRepository extends JpaRepository<Recommendation, Long> {

    List<Recommendation> findByUserOrderByCreatedAtDesc(User user);

    List<Recommendation> findTop10ByOrderByCreatedAtDesc();
}
