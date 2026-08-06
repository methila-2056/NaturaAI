package com.naturaai.service;

import com.naturaai.model.Herb;
import com.naturaai.repository.HerbRepository;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class HerbService {

    private final HerbRepository herbRepository;

    public HerbService(HerbRepository herbRepository) {
        this.herbRepository = herbRepository;
    }

    @Transactional(readOnly = true)
    @Cacheable(value = "herbs", key = "#name")
    public Herb findByName(String name) {
        return herbRepository.findByNameIgnoreCase(name).orElse(null);
    }

    @Transactional(readOnly = true)
    @Cacheable(value = "herbSearch", key = "#query")
    public List<Herb> search(String query) {
        return herbRepository.findByNameContainingIgnoreCase(query);
    }

    @Transactional(readOnly = true)
    public List<Herb> findAll() {
        return herbRepository.findAll();
    }
}
